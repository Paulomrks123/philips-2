package br.com.philips.pocketzapper

import android.app.Activity
import android.content.Context
import android.hardware.ConsumerIrManager
import android.os.Bundle
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import org.json.JSONObject

class MainActivity : Activity() {
    private lateinit var webView: WebView
    private val commands = emptyMap<String, IntArray>() // Populate only with verified model-specific pulse patterns.
    private var ir: ConsumerIrManager? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        ir = getSystemService(Context.CONSUMER_IR_SERVICE) as? ConsumerIrManager
        webView = WebView(this)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.webViewClient = WebViewClient()
        webView.webChromeClient = WebChromeClient()
        webView.addJavascriptInterface(IrBridge(), "PhilipsIR")
        setContentView(webView)
        webView.loadUrl("https://philips-pocket-zapper.lovable.app")
    }

    inner class IrBridge {
        @JavascriptInterface
        fun getStatus(): String {
            val manager = ir
            val available = manager?.hasIrEmitter() == true
            return JSONObject()
                .put("available", available)
                .put("profile", "Philips 26PFL3404")
                .put("profileConfigured", commands.isNotEmpty())
                .put("message", when {
                    !available -> "Este celular não disponibiliza emissor infravermelho pela API Android."
                    commands.isEmpty() -> "Emissor IR detectado; perfil de códigos Philips ainda não validado."
                    else -> "Emissor IR disponível."
                }).toString()
        }

        @JavascriptInterface
        fun send(command: String): String {
            val manager = ir ?: return result(false, "API infravermelha indisponível.")
            if (!manager.hasIrEmitter()) return result(false, "Este aparelho não possui emissor IR compatível.")
            val pattern = commands[command.uppercase()]
                ?: return result(false, "Comando sem código validado para Philips 26PFL3404.")
            val carrier = 36000
            if (carrier !in manager.carrierFrequencies.map { it.minFrequency..it.maxFrequency }.flatten()) {
                return result(false, "Frequência de 36 kHz não suportada pelo aparelho.")
            }
            return try {
                manager.transmit(carrier, pattern)
                result(true, "Sinal transmitido pelo Android; recepção da TV não confirmada.")
            } catch (e: Exception) {
                result(false, "Falha na transmissão: ${e.message ?: "erro desconhecido"}")
            }
        }

        private fun result(ok: Boolean, message: String) =
            JSONObject().put("ok", ok).put("message", message).toString()
    }
}
