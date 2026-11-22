package br.com.philips.pocketzapper

import android.app.Activity
import android.content.Context
import android.hardware.ConsumerIrManager
import android.net.Uri
import android.os.Bundle
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import org.json.JSONArray
import org.json.JSONObject

class MainActivity : Activity() {
    private lateinit var webView: WebView
    // Intentionally empty until pulse patterns are verified for Philips 50PUG6654/78.
    private val commands = emptyMap<String, IntArray>()
    private var ir: ConsumerIrManager? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        ir = getSystemService(Context.CONSUMER_IR_SERVICE) as? ConsumerIrManager

        webView = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            settings.javaScriptCanOpenWindowsAutomatically = false
            settings.setSupportMultipleWindows(false)
            webViewClient = object : WebViewClient() {
                override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                    return !isTrustedUrl(request.url)
                }

                @Suppress("DEPRECATION")
                override fun shouldOverrideUrlLoading(view: WebView, url: String): Boolean {
                    return !isTrustedUrl(Uri.parse(url))
                }
            }
            webChromeClient = WebChromeClient()
            addJavascriptInterface(IrBridge(), "PhilipsIR")
        }
        setContentView(webView)
        webView.loadUrl(APP_URL)
    }

    private fun isTrustedUrl(uri: Uri): Boolean =
        uri.scheme == "https" && uri.host == APP_HOST

    inner class IrBridge {
        @JavascriptInterface
        fun getStatus(): String {
            val manager = ir
            val available = manager?.hasIrEmitter() == true
            val ranges = manager?.carrierFrequencies?.toList().orEmpty()
            val rangeJson = JSONArray()
            ranges.chunked(2).forEach { range ->
                if (range.size == 2) {
                    rangeJson.put(JSONArray().put(range[0]).put(range[1]))
                }
            }
            val supports36kHz = ranges.chunked(2).any { range ->
                range.size == 2 && 36000 in range[0]..range[1]
            }
            return JSONObject()
                .put("available", available)
                .put("profile", MODEL)
                .put("profileConfigured", commands.isNotEmpty())
                .put("supports36kHz", supports36kHz)
                .put("carrierRangesHz", rangeJson)
                .put("message", when {
                    !available -> "Emissor infravermelho não detectado pela API Android."
                    !supports36kHz -> "Emissor IR detectado, mas 36 kHz não consta entre as frequências suportadas."
                    commands.isEmpty() -> "Emissor IR detectado e 36 kHz suportado. Códigos da TV ainda precisam ser validados."
                    else -> "Emissor IR disponível."
                }).toString()
        }

        @JavascriptInterface
        fun send(command: String): String {
            val manager = ir ?: return result(false, "API infravermelha indisponível.")
            if (!manager.hasIrEmitter()) return result(false, "Este aparelho não disponibiliza emissor IR pela API Android.")
            val pattern = commands[command.uppercase()]
                ?: return result(false, "Comando sem código validado para $MODEL.")
            val carrierHz = 36000
            val supportsCarrier = manager.carrierFrequencies?.any {
                carrierHz.toDouble() >= it.minFrequency && carrierHz.toDouble() <= it.maxFrequency
            } == true
            if (!supportsCarrier) return result(false, "Frequência de 36 kHz não suportada pelo aparelho.")
            return try {
                manager.transmit(carrierHz, pattern)
                result(true, "Sinal transmitido pelo Android; recepção da TV não confirmada.")
            } catch (e: Exception) {
                result(false, "Falha na transmissão: ${e.message ?: "erro desconhecido"}")
            }
        }

        private fun result(ok: Boolean, message: String) =
            JSONObject().put("ok", ok).put("message", message).toString()
    }

    companion object {
        private const val APP_URL = "https://philips-pocket-zapper.lovable.app"
        private const val APP_HOST = "philips-pocket-zapper.lovable.app"
        private const val MODEL = "Philips 50PUG6654/78"
    }
}
