package br.com.philips.pocketzapper

import android.app.Activity
import android.content.Context
import android.hardware.ConsumerIrManager
import android.net.Uri
import android.os.Bundle
import android.view.KeyEvent
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.net.ServerSocket
import java.net.InetAddress
import java.net.Socket
import java.io.InputStream
import java.io.OutputStream
import java.nio.charset.StandardCharsets

class MainActivity : Activity() {
    // IR pulse patterns remain empty until verified for this exact TV model.
    private val commands = emptyMap<String, IntArray>()
    private var ir: ConsumerIrManager? = null
    private var tvHost: String? = null
    private var tvApiVersion: Int = 6
    private lateinit var webView: WebView
    @Volatile private var localServer: ServerSocket? = null
    @Volatile private var serverRunning = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        ir = getSystemService(Context.CONSUMER_IR_SERVICE) as? ConsumerIrManager
        startLocalBridgeServer()

        webView = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            settings.javaScriptCanOpenWindowsAutomatically = false
            settings.setSupportMultipleWindows(false)
            webViewClient = object : WebViewClient() {
                override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean =
                    !isTrustedUrl(request.url)

                @Suppress("DEPRECATION")
                override fun shouldOverrideUrlLoading(view: WebView, url: String): Boolean =
                    !isTrustedUrl(Uri.parse(url))
            }
            webChromeClient = WebChromeClient()
            addJavascriptInterface(IrBridge(), "PhilipsIR")
        }
        setContentView(webView)
        webView.loadUrl(APP_URL)
    }

    // Physical volume keys work while this Android companion is in the foreground.
    // Android does not let a background app intercept keys owned by Chrome.
    override fun dispatchKeyEvent(event: KeyEvent): Boolean {
        if (event.action == KeyEvent.ACTION_DOWN && event.repeatCount == 0) {
            when (event.keyCode) {
                KeyEvent.KEYCODE_VOLUME_UP -> { IrBridge().send("VOLUME_UP"); return true }
                KeyEvent.KEYCODE_VOLUME_DOWN -> { IrBridge().send("VOLUME_DOWN"); return true }
            }
        }
        return super.dispatchKeyEvent(event)
    }

    override fun onDestroy() {
        serverRunning = false
        try { localServer?.close() } catch (_: Exception) { }
        localServer = null
        super.onDestroy()
    }

    // Local companion bridge for the PWA opened separately in Chrome.
    private fun startLocalBridgeServer() {
        if (serverRunning) return
        serverRunning = true
        Thread({
            try {
                val server = ServerSocket(8765, 20, InetAddress.getByName("127.0.0.1"))
                localServer = server
                while (serverRunning) {
                    val client = try { server.accept() } catch (_: Exception) { break }
                    Thread({ handleLocalRequest(client) }, "philips-local-client").start()
                }
            } catch (_: Exception) {
                serverRunning = false
            }
        }, "philips-local-bridge").start()
    }

    private fun readHttpLine(input: InputStream): String? {
        val bytes = java.io.ByteArrayOutputStream()
        while (true) {
            val value = input.read()
            if (value == -1) return if (bytes.size() == 0) null else bytes.toString("UTF-8")
            if (value == 10) break
            if (value != 13) bytes.write(value)
            if (bytes.size() > 8192) return null
        }
        return bytes.toString("UTF-8")
    }

    private fun handleLocalRequest(socket: Socket) {
        socket.use { client ->
            try {
                client.soTimeout = 5000
                val input = client.getInputStream()
                val request = readHttpLine(input) ?: return
                val parts = request.split(" ")
                val method = parts.getOrNull(0) ?: ""
                val path = parts.getOrNull(1)?.substringBefore("?") ?: ""
                val headers = mutableMapOf<String, String>()
                while (true) {
                    val line = readHttpLine(input) ?: break
                    if (line.isEmpty()) break
                    val split = line.indexOf(":")
                    if (split > 0) headers[line.substring(0, split).trim().lowercase()] = line.substring(split + 1).trim()
                }
                if (headers["origin"] != "https://philips-pocket-zapper.lovable.app") {
                    val denied = "HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
                    client.getOutputStream().use { it.write(denied.toByteArray(StandardCharsets.US_ASCII)) }
                    return
                }
                val length = (headers["content-length"] ?: "0").toIntOrNull()?.coerceIn(0, 8192) ?: 0
                val bodyBytes = ByteArray(length)
                var offset = 0
                while (offset < length) {
                    val count = input.read(bodyBytes, offset, length - offset)
                    if (count <= 0) break
                    offset += count
                }
                val body = String(bodyBytes, 0, offset, StandardCharsets.UTF_8)
                val validPath = (method == "GET" && path == "/status") || (method == "POST" && path in listOf("/connect", "/send"))
                val result = when {
                    method == "OPTIONS" -> ""
                    method == "GET" && path == "/status" -> IrBridge().getStatus()
                    method == "POST" && path == "/connect" -> IrBridge().connectNetwork(JSONObject(body).optString("ip"))
                    method == "POST" && path == "/send" -> IrBridge().send(JSONObject(body).optString("command"))
                    else -> JSONObject().put("ok", false).put("message", "Endpoint local desconhecido.").toString()
                }
                val status = when {
                    method == "OPTIONS" -> "204 No Content"
                    validPath -> "200 OK"
                    else -> "404 Not Found"
                }
                val bytes = result.toByteArray(StandardCharsets.UTF_8)
                val output: OutputStream = client.getOutputStream()
                val responseHeaders = "HTTP/1.1 $status\r\n" +
                    "Access-Control-Allow-Origin: https://philips-pocket-zapper.lovable.app\r\n" +
                    "Vary: Origin\r\n" +
                    "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n" +
                    "Access-Control-Allow-Headers: Content-Type\r\n" +
                    "Access-Control-Allow-Private-Network: true\r\n" +
                    "Content-Type: application/json; charset=utf-8\r\n" +
                    "Content-Length: " + (if (method == "OPTIONS") 0 else bytes.size) + "\r\n" +
                    "Connection: close\r\n\r\n"
                output.write(responseHeaders.toByteArray(StandardCharsets.US_ASCII))
                if (method != "OPTIONS") output.write(bytes)
                output.flush()
            } catch (_: Exception) { }
        }
    }

    private fun isTrustedUrl(uri: Uri): Boolean =
        uri.scheme == "https" && uri.host == APP_HOST

    inner class IrBridge {
        @JavascriptInterface
        fun getStatus(): String {
            val manager = ir
            val available = manager?.hasIrEmitter() == true
            return JSONObject()
                .put("available", available)
                .put("profile", MODEL)
                .put("profileConfigured", commands.isNotEmpty())
                .put("networkConnected", tvHost != null)
                .put("message", when {
                    tvHost != null -> "TV conectada pela rede Wi-Fi."
                    available -> "Emissor IR detectado. Sincronize pela rede ou aguarde códigos IR validados."
                    else -> "Conecte o celular e a TV à mesma rede Wi-Fi para sincronizar."
                }).toString()
        }

        @JavascriptInterface
        fun connectNetwork(ip: String): String {
            val host = ip.trim()
            if (!IPV4.matches(host)) {
                return result(false, "Digite um endereço IPv4 válido da TV, por exemplo 192.168.1.50.")
            }
            val versions = listOf(6, 5, 1)
            for (version in versions) {
                var connection: HttpURLConnection? = null
                try {
                    connection = URL("http://$host:1925/$version/system").openConnection() as HttpURLConnection
                    connection.requestMethod = "GET"
                    connection.connectTimeout = 2500
                    connection.readTimeout = 2500
                    connection.setRequestProperty("Accept", "application/json")
                    val code = connection.responseCode
                    if (code == HttpURLConnection.HTTP_OK) {
                        val body = connection.inputStream.bufferedReader().use { it.readText() }
                        val json = JSONObject(body)
                        if (json.has("api_version") || json.has("system") || json.has("name")) {
                            tvHost = host
                            tvApiVersion = version
                            return JSONObject()
                                .put("ok", true)
                                .put("message", "TV Philips encontrada na rede. API SAPHI v$version respondeu.")
                                .put("ip", host)
                                .put("apiVersion", version)
                                .toString()
                        }
                    }
                } catch (_: Exception) {
                    // Try the next known SAPHI API version.
                } finally {
                    connection?.disconnect()
                }
            }
            return result(false, "Não encontrei a API SAPHI nesse IP. Confira se a TV está ligada, na mesma rede Wi-Fi e se o IP está correto.")
        }

        @JavascriptInterface
        fun send(command: String): String {
            val networkKey = networkKey(command.uppercase())
            val host = tvHost
            if (host != null && networkKey != null) {
                var connection: HttpURLConnection? = null
                return try {
                    connection = URL("http://$host:1925/$tvApiVersion/input/key").openConnection() as HttpURLConnection
                    connection.requestMethod = "POST"
                    connection.connectTimeout = 2500
                    connection.readTimeout = 2500
                    connection.doOutput = true
                    connection.setRequestProperty("Content-Type", "application/json")
                    connection.outputStream.use {
                        it.write(JSONObject().put("key", networkKey).toString().toByteArray(Charsets.UTF_8))
                    }
                    val code = connection.responseCode
                    if (code in 200..299) {
                        result(true, "Comando enviado à TV pela rede Wi-Fi.")
                    } else {
                        result(false, "A TV respondeu com HTTP $code. Tente sincronizar novamente.")
                    }
                } catch (e: Exception) {
                    result(false, "Falha ao enviar comando pela rede: ${e.message ?: "erro de conexão"}.")
                } finally {
                    connection?.disconnect()
                }
            }

            val manager = ir ?: return result(false, "API infravermelha indisponível.")
            if (!manager.hasIrEmitter()) return result(false, "Sincronize a TV pela mesma rede Wi-Fi ou use um celular com emissor IR.")
            val pattern = commands[command.uppercase()]
                ?: return result(false, "A TV ainda não está sincronizada e não há código IR validado para $MODEL.")
            return try {
                manager.transmit(36000, pattern)
                result(true, "Sinal IR transmitido; recepção da TV não confirmada.")
            } catch (e: Exception) {
                result(false, "Falha na transmissão IR: ${e.message ?: "erro desconhecido"}")
            }
        }

        private fun networkKey(command: String): String? {
            if (command.startsWith("NUM_")) {
                val digit = command.removePrefix("NUM_")
                if (digit.length == 1 && digit[0] in '0'..'9') return "Digit$digit"
            }
            return when (command) {
                "POWER" -> "Standby"
                "UP" -> "CursorUp"
                "DOWN" -> "CursorDown"
                "LEFT" -> "CursorLeft"
                "RIGHT" -> "CursorRight"
                "OK" -> "Confirm"
                "BACK", "EXIT" -> "Back"
                "MENU" -> "Home"
                "SOURCE", "AV", "HDMI" -> "Source"
                "TV" -> "WatchTV"
                "MUTE" -> "Mute"
                "VOLUME_UP" -> "VolumeUp"
                "VOLUME_DOWN" -> "VolumeDown"
                "CHANNEL_UP" -> "ChannelStepUp"
                "CHANNEL_DOWN" -> "ChannelStepDown"
                "INFO" -> "Info"
                else -> null
            }
        }

        private fun result(ok: Boolean, message: String) =
            JSONObject().put("ok", ok).put("message", message).toString()
    }

    companion object {
        private const val APP_URL = "https://philips-pocket-zapper.lovable.app"
        private const val APP_HOST = "philips-pocket-zapper.lovable.app"
        private const val MODEL = "Philips 50PUG6654/78"
        private val IPV4 = Regex("^(?:25[0-5]|2[0-4]\\d|1?\\d?\\d)(?:\\.(?:25[0-5]|2[0-4]\\d|1?\\d?\\d)){3}$")
    }
}
