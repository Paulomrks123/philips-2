"""Generate a standalone Android Studio source project in /tmp; never modifies the web app."""
from pathlib import Path
from PIL import Image
import urllib.request

ROOT = Path('/tmp/philips-native/PhilipsRemote')
FILES = {}
FILES['settings.gradle.kts'] = '''pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "PhilipsRemote"
include(":app")
'''
FILES['build.gradle.kts'] = '''plugins {
    id("com.android.application") version "8.9.2" apply false
    id("org.jetbrains.kotlin.android") version "2.1.20" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.1.20" apply false
}
'''
FILES['gradle.properties'] = '''org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
'''
FILES['.gitignore'] = '''.gradle/
.idea/
local.properties
**/build/
*.iml
*.jks
*.keystore
'''
FILES['app/build.gradle.kts'] = '''plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}
android {
    namespace = "com.philipsremote"
    compileSdk = 35
    defaultConfig {
        applicationId = "com.philipsremote"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { compose = true }
}
dependencies {
    implementation(platform("androidx.compose:compose-bom:2025.04.01"))
    implementation("androidx.activity:activity-compose:1.10.1")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.9.0")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.9.0")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.9.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.10.2")
    testImplementation("junit:junit:4.13.2")
}
'''
FILES['app/src/main/AndroidManifest.xml'] = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.TRANSMIT_IR" />
    <uses-feature android:name="android.hardware.consumerir" android:required="false" />
    <application android:allowBackup="false" android:label="@string/app_name"
        android:icon="@mipmap/ic_launcher" android:roundIcon="@mipmap/ic_launcher"
        android:theme="@style/Theme.PhilipsRemote" android:supportsRtl="true">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
'''
FILES['app/src/main/res/values/strings.xml'] = '<resources><string name="app_name">Philips Remote</string></resources>\n'
FILES['app/src/main/res/values/themes.xml'] = '''<resources>
    <style name="Theme.PhilipsRemote" parent="android:style/Theme.Material.NoActionBar">
        <item name="android:fontFamily">sans</item>
        <item name="android:windowLightStatusBar">false</item>
        <item name="android:windowLightNavigationBar">false</item>
        <item name="android:windowBackground">#303030</item>
        <item name="android:colorAccent">#2388EF</item>
    </style>
</resources>
'''
FILES['app/src/main/java/com/philipsremote/ir/IrCore.kt'] = '''package com.philipsremote.ir

const val TARGET_MODEL = "26PFL3404"
enum class RemoteCommand(val label: String) {
    POWER("Ligar / desligar"), CHANNEL_UP("Canal +"), CHANNEL_DOWN("Canal −"),
    VOLUME_UP("Volume +"), VOLUME_DOWN("Volume −"), MUTE("Mudo"), FAVORITES("Favoritos"),
    UP("Cima"), DOWN("Baixo"), LEFT("Esquerda"), RIGHT("Direita"), OK("OK"),
    MENU("Menu"), BACK("Voltar"), EXIT("Sair"), SOURCE("Entrada"), TV("TV"), AV("AV"),
    HDMI("HDMI"), INFO("Informações"), GUIDE("Guia"), PICTURE("Imagem"), SOUND("Som"), SLEEP("Sleep"),
    NUM_0("0"), NUM_1("1"), NUM_2("2"), NUM_3("3"), NUM_4("4"), NUM_5("5"),
    NUM_6("6"), NUM_7("7"), NUM_8("8"), NUM_9("9")
}
data class FrequencyRange(val minHz: Int, val maxHz: Int) {
    fun contains(hz: Int) = minHz > 0 && maxHz >= minHz && hz in minHz..maxHz
}
data class IrDiagnostic(
    val featureDeclared: Boolean = false, val serviceAvailable: Boolean = false,
    val emitterPresent: Boolean = false, val ranges: List<FrequencyRange> = emptyList(),
    val error: String? = null
) {
    val ready get() = featureDeclared && serviceAvailable && emitterPresent &&
        ranges.isNotEmpty() && ranges.all { it.minHz > 0 && it.maxHz >= it.minHz } && error == null
}
/** Captured ON/OFF durations in microseconds, starting ON. Ordered frames can alternate
 * a verified protocol's toggle bit on successive presses. No guessed RC5/RC6 encoder. */
data class ConfirmedSignal(
    val model: String, val source: String, val confirmedOnDevice: Boolean,
    val carrierHz: Int, val frames: List<List<Int>>
)
object PhilipsProfile {
    // No code qualifies as confirmed for 26PFL3404. Keep the whole map empty.
    val signals: Map<RemoteCommand, ConfirmedSignal> = emptyMap()
}
sealed interface SendResult {
    data class Blocked(val reason: String) : SendResult
    data class Failed(val reason: String) : SendResult
    data object Transmitted : SendResult
}
interface IrBackend {
    fun diagnose(): IrDiagnostic
    fun transmit(carrierHz: Int, patternMicros: IntArray)
}
fun validationError(signal: ConfirmedSignal?, diagnostic: IrDiagnostic): String? {
    if (signal == null) return "Código não configurado: sem confirmação para Philips $TARGET_MODEL."
    if (signal.model != TARGET_MODEL || !signal.confirmedOnDevice || signal.source.isBlank())
        return "Código sem confirmação documentada para este modelo."
    if (!diagnostic.ready) return "Emissor IR indisponível ou diagnóstico incompleto."
    if (!diagnostic.ranges.any { it.contains(signal.carrierHz) }) return "Frequência não suportada pelo emissor."
    if (signal.frames.isEmpty()) return "Sequência IR ausente."
    // Validate ALL toggle frames, not only the first one displayed by the UI.
    for (pattern in signal.frames) {
        if (pattern.isEmpty() || pattern.any { it <= 0 }) return "Durações IR inválidas."
        if (pattern.sumOf { it.toLong() } >= 2_000_000L) return "Sequência IR deve durar menos de 2 segundos."
    }
    return null
}
class IrController(
    private val backend: IrBackend,
    signals: Map<RemoteCommand, ConfirmedSignal> = PhilipsProfile.signals,
    private val nowMillis: () -> Long,
) {
    private val signals = signals.mapValues { (_, signal) -> signal.copy(frames = signal.frames.map { it.toList() }) }
    private val frameIndex = mutableMapOf<RemoteCommand, Int>()
    private var lastSend: Long? = null
    fun diagnose(): IrDiagnostic = try { backend.diagnose() }
        catch (e: RuntimeException) { IrDiagnostic(error = "Falha no diagnóstico: ${e.javaClass.simpleName}") }
    fun blockReason(command: RemoteCommand, diagnostic: IrDiagnostic): String? = validationError(signals[command], diagnostic)
    @Synchronized
    fun send(command: RemoteCommand): SendResult {
        val signal = signals[command]
        val invalid = validationError(signal, diagnose())
        if (invalid != null) return SendResult.Blocked(invalid)
        if (signal == null) return SendResult.Blocked("Código não configurado.")
        val now = nowMillis()
        val previous = lastSend
        if (previous != null && now - previous < 150L) return SendResult.Blocked("Aguarde antes do próximo comando.")
        lastSend = now
        val index = frameIndex[command] ?: 0
        return try {
            backend.transmit(signal.carrierHz, signal.frames[index].toIntArray())
            frameIndex[command] = (index + 1) % signal.frames.size
            SendResult.Transmitted
        } catch (e: RuntimeException) { SendResult.Failed("Falha na transmissão IR: ${e.javaClass.simpleName}") }
    }
}
'''
FILES['app/src/main/java/com/philipsremote/ir/AndroidIrBackend.kt'] = '''package com.philipsremote.ir
import android.content.Context
import android.content.pm.PackageManager
import android.hardware.ConsumerIrManager

class AndroidIrBackend(context: Context) : IrBackend {
    private val context = context.applicationContext
    private val manager get() = context.getSystemService(ConsumerIrManager::class.java)
    override fun diagnose(): IrDiagnostic {
        val declared = context.packageManager.hasSystemFeature(PackageManager.FEATURE_CONSUMER_IR)
        val service = manager ?: return IrDiagnostic(featureDeclared = declared)
        return try {
            val emitter = service.hasIrEmitter()
            val ranges = if (emitter) service.carrierFrequencies?.map {
                FrequencyRange(it.minFrequency, it.maxFrequency)
            }.orEmpty() else emptyList()
            IrDiagnostic(declared, true, emitter, ranges,
                if (emitter && ranges.isEmpty()) "O serviço não informou frequências válidas." else null)
        } catch (e: RuntimeException) { IrDiagnostic(declared, true, error = "Serviço IR: ${e.javaClass.simpleName}") }
    }
    override fun transmit(carrierHz: Int, patternMicros: IntArray) {
        val service = manager ?: throw IllegalStateException("Serviço IR ausente")
        if (!service.hasIrEmitter()) throw IllegalStateException("Emissor IR ausente")
        service.transmit(carrierHz, patternMicros.copyOf())
    }
}
'''
FILES['app/src/main/java/com/philipsremote/ui/RemoteViewModel.kt'] = '''package com.philipsremote.ui
import android.app.Application
import android.os.SystemClock
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.philipsremote.ir.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

data class RemoteState(val diagnostic: IrDiagnostic = IrDiagnostic(), val checking: Boolean = true,
    val sending: Boolean = false, val message: String = "Nenhum código confirmado para este modelo.")
class RemoteViewModel(application: Application) : AndroidViewModel(application) {
    private val controller = IrController(AndroidIrBackend(application), nowMillis = SystemClock::elapsedRealtime)
    private val mutableState = MutableStateFlow(RemoteState())
    val state = mutableState.asStateFlow()
    private var diagnosticInFlight = false
    init { refreshDiagnostic() }
    fun refreshDiagnostic() {
        if (mutableState.value.sending || diagnosticInFlight) return
        diagnosticInFlight = true
        mutableState.value = mutableState.value.copy(checking = true)
        viewModelScope.launch {
            try {
                val diagnostic = withContext(Dispatchers.IO) { controller.diagnose() }
                mutableState.value = mutableState.value.copy(diagnostic = diagnostic, checking = false)
            } finally { diagnosticInFlight = false }
        }
    }
    fun enabled(command: RemoteCommand) = !mutableState.value.checking && !mutableState.value.sending &&
        controller.blockReason(command, mutableState.value.diagnostic) == null
    fun send(command: RemoteCommand) {
        if (mutableState.value.sending || mutableState.value.checking) return
        mutableState.value = mutableState.value.copy(sending = true)
        viewModelScope.launch {
            val result = withContext(Dispatchers.IO) { controller.send(command) }
            val message = when (result) {
                is SendResult.Blocked -> result.reason
                is SendResult.Failed -> result.reason
                SendResult.Transmitted -> "IR enviado: ${command.label}. Resposta da TV não verificada."
            }
            mutableState.value = mutableState.value.copy(sending = false, message = message)
        }
    }
}
'''
FILES['app/src/main/java/com/philipsremote/MainActivity.kt'] = '''package com.philipsremote
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.philipsremote.ui.PhilipsTheme
import com.philipsremote.ui.RemoteScreen
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent { PhilipsTheme { RemoteScreen() } }
    }
}
'''
FILES['app/src/main/java/com/philipsremote/ui/Theme.kt'] = '''package com.philipsremote.ui
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
object RemoteColors {
    val Background = Color(0xFF303030)
    val Surface = Color(0xFF404040)
    val Foreground = Color(0xFFF5F5F5)
    val Muted = Color(0xFFB8B8B8)
    val Primary = Color(0xFF2388EF)
    val Power = Color(0xFFF04A4A)
    val Pad = Color(0xFFF5F5F5)
    val PadInk = Color(0xFF555555)
}
@Composable fun PhilipsTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = darkColorScheme(primary = RemoteColors.Primary,
        background = RemoteColors.Background, surface = RemoteColors.Surface,
        onSurface = RemoteColors.Foreground, onBackground = RemoteColors.Foreground,
        error = RemoteColors.Power, onSurfaceVariant = RemoteColors.Muted), content = content)
}
'''
FILES['app/src/main/java/com/philipsremote/ui/RemoteScreen.kt'] = '''package com.philipsremote.ui
import android.os.Build
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LifecycleEventEffect
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.philipsremote.R
import com.philipsremote.ir.*

@Composable fun RemoteScreen(vm: RemoteViewModel = viewModel()) {
    val state by vm.state.collectAsStateWithLifecycle()
    var panel by rememberSaveable { mutableStateOf<String?>(null) }
    LifecycleEventEffect(Lifecycle.Event.ON_RESUME) { vm.refreshDiagnostic() }
    val enabled: (RemoteCommand) -> Boolean = { vm.enabled(it) }
    val send: (RemoteCommand) -> Unit = { vm.send(it) }
    Scaffold(containerColor = RemoteColors.Background) { insets ->
        Column(Modifier.fillMaxSize().padding(insets).windowInsetsPadding(WindowInsets.safeDrawing.only(WindowInsetsSides.Horizontal))) {
            Row(Modifier.fillMaxWidth().background(RemoteColors.Primary).padding(horizontal = 12.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                Image(painterResource(R.drawable.remote_logo), null, Modifier.size(32.dp))
                Text("Philips TV 26PFL3404", Modifier.weight(1f).padding(horizontal = 8.dp), style = MaterialTheme.typography.titleMedium)
                IconButton(onClick = { panel = "diagnostic" }) { Icon(Icons.Default.Settings, "Diagnóstico IR") }
            }
            Column(Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState()), horizontalAlignment = Alignment.CenterHorizontally) {
                Text(if (state.checking) "Verificando emissor IR…" else if (state.diagnostic.ready)
                    "Emissor IR detectado" else "Emissor IR indisponível • abra o diagnóstico",
                    Modifier.padding(12.dp), style = MaterialTheme.typography.bodySmall, color = RemoteColors.Muted)
                Text("${PhilipsProfile.signals.size}/${RemoteCommand.entries.size} códigos confirmados • comandos não configurados ficam desativados",
                    Modifier.padding(horizontal = 16.dp), style = MaterialTheme.typography.bodySmall, color = RemoteColors.Muted)
                BoxWithConstraints(Modifier.fillMaxWidth().padding(16.dp)) {
                    if (maxWidth >= 600.dp) {
                        Row(horizontalArrangement = Arrangement.spacedBy(24.dp), verticalAlignment = Alignment.CenterVertically) {
                            Column(Modifier.weight(1f), horizontalAlignment = Alignment.CenterHorizontally) {
                                TopControls(enabled, send)
                                Spacer(Modifier.height(16.dp))
                                MenuControls(enabled, send)
                            }
                            NavigationControls(enabled, send, Modifier.weight(1f))
                        }
                    } else {
                        Column(Modifier.widthIn(max = 420.dp).align(Alignment.TopCenter), horizontalAlignment = Alignment.CenterHorizontally) {
                            TopControls(enabled, send)
                            Spacer(Modifier.height(20.dp))
                            NavigationControls(enabled, send)
                            Spacer(Modifier.height(20.dp))
                            MenuControls(enabled, send)
                        }
                    }
                }
                Row(Modifier.widthIn(max = 420.dp).fillMaxWidth().padding(16.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                    FilledTonalButton(onClick = { panel = "digits" }, shape = CircleShape, contentPadding = PaddingValues(0.dp), modifier = Modifier.size(56.dp)) { Text("123") }
                    RemoteKey(RemoteCommand.EXIT, enabled, send)
                    FilledTonalIconButton(onClick = { panel = "more" }, modifier = Modifier.size(56.dp)) { Icon(Icons.Default.MoreHoriz, "Mais opções") }
                }
                Text(state.message, Modifier.padding(horizontal = 20.dp, vertical = 12.dp).semantics { liveRegion = LiveRegionMode.Polite },
                    color = RemoteColors.Muted, style = MaterialTheme.typography.bodySmall)
            }
        }
    }
    when (panel) {
        "diagnostic" -> DiagnosticDialog(state, vm::refreshDiagnostic) { panel = null }
        "digits", "more" -> {
            val numeric = panel == "digits"
            val commands = if (numeric) listOf(RemoteCommand.NUM_1, RemoteCommand.NUM_2, RemoteCommand.NUM_3,
                RemoteCommand.NUM_4, RemoteCommand.NUM_5, RemoteCommand.NUM_6, RemoteCommand.NUM_7,
                RemoteCommand.NUM_8, RemoteCommand.NUM_9, RemoteCommand.NUM_0) else listOf(
                RemoteCommand.SOURCE, RemoteCommand.TV, RemoteCommand.AV, RemoteCommand.HDMI,
                RemoteCommand.INFO, RemoteCommand.GUIDE, RemoteCommand.PICTURE, RemoteCommand.SOUND, RemoteCommand.SLEEP)
            AlertDialog(onDismissRequest = { panel = null }, title = { Text(if (numeric) "Teclado numérico" else "Funções") },
                text = {
                    Column(Modifier.verticalScroll(rememberScrollState())) {
                        Text("Códigos não configurados ficam desativados.", color = RemoteColors.Muted)
                        commands.chunked(3).forEach { group ->
                            Row(Modifier.fillMaxWidth().padding(top = 8.dp)) {
                                group.forEach { command ->
                                    OutlinedButton(onClick = { send(command) }, enabled = enabled(command), modifier = Modifier.weight(1f).padding(2.dp), contentPadding = PaddingValues(4.dp)) {
                                        Text(command.label, style = MaterialTheme.typography.labelSmall)
                                    }
                                }
                            }
                        }
                    }
                }, confirmButton = { TextButton(onClick = { panel = null }) { Text("Fechar") } })
        }
    }
}
@Composable private fun TopControls(enabled: (RemoteCommand) -> Boolean, send: (RemoteCommand) -> Unit) {
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
        Rocker("CH", RemoteCommand.CHANNEL_UP, RemoteCommand.CHANNEL_DOWN, Icons.Default.KeyboardArrowUp, Icons.Default.KeyboardArrowDown, enabled, send)
        RemoteKey(RemoteCommand.FAVORITES, enabled, send, Icons.Default.Star, RemoteColors.Primary, 80)
        RemoteKey(RemoteCommand.POWER, enabled, send, Icons.Default.PowerSettingsNew, RemoteColors.Power)
    }
}
@Composable private fun NavigationControls(enabled: (RemoteCommand) -> Boolean, send: (RemoteCommand) -> Unit, modifier: Modifier = Modifier) {
    Row(modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.CenterVertically) {
        Box(Modifier.weight(1f).aspectRatio(1f).background(RemoteColors.Pad, CircleShape)) {
            Direction(RemoteCommand.UP, Icons.Default.KeyboardArrowUp, Alignment.TopCenter, enabled, send)
            Direction(RemoteCommand.DOWN, Icons.Default.KeyboardArrowDown, Alignment.BottomCenter, enabled, send)
            Direction(RemoteCommand.LEFT, Icons.Default.KeyboardArrowLeft, Alignment.CenterStart, enabled, send)
            Direction(RemoteCommand.RIGHT, Icons.Default.KeyboardArrowRight, Alignment.CenterEnd, enabled, send)
            TextButton(onClick = { send(RemoteCommand.OK) }, enabled = enabled(RemoteCommand.OK), modifier = Modifier.align(Alignment.Center).size(64.dp),
                colors = ButtonDefaults.textButtonColors(contentColor = RemoteColors.PadInk, disabledContentColor = RemoteColors.PadInk.copy(alpha = .55f))) { Text("OK") }
        }
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Rocker("VOL", RemoteCommand.VOLUME_UP, RemoteCommand.VOLUME_DOWN, Icons.Default.Add, Icons.Default.Remove, enabled, send)
            RemoteKey(RemoteCommand.MUTE, enabled, send, Icons.Default.VolumeOff)
        }
    }
}
@Composable private fun BoxScope.Direction(command: RemoteCommand, icon: ImageVector, alignment: Alignment, enabled: (RemoteCommand) -> Boolean, send: (RemoteCommand) -> Unit) {
    IconButton(onClick = { send(command) }, enabled = enabled(command), modifier = Modifier.align(alignment).size(56.dp),
        colors = IconButtonDefaults.iconButtonColors(contentColor = RemoteColors.PadInk, disabledContentColor = RemoteColors.PadInk.copy(alpha = .55f))) { Icon(icon, command.label) }
}
@Composable private fun MenuControls(enabled: (RemoteCommand) -> Boolean, send: (RemoteCommand) -> Unit) {
    Row(horizontalArrangement = Arrangement.spacedBy(40.dp)) {
        RemoteKey(RemoteCommand.MENU, enabled, send)
        RemoteKey(RemoteCommand.BACK, enabled, send, Icons.Default.Undo)
    }
}
@Composable private fun Rocker(label: String, up: RemoteCommand, down: RemoteCommand, upIcon: ImageVector, downIcon: ImageVector, enabled: (RemoteCommand) -> Boolean, send: (RemoteCommand) -> Unit) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        IconButton(onClick = { send(up) }, enabled = enabled(up)) { Icon(upIcon, up.label) }
        HorizontalDivider(Modifier.width(24.dp))
        Text(label, Modifier.padding(vertical = 8.dp), color = RemoteColors.Muted)
        HorizontalDivider(Modifier.width(24.dp))
        IconButton(onClick = { send(down) }, enabled = enabled(down)) { Icon(downIcon, down.label) }
    }
}
@Composable private fun RemoteKey(command: RemoteCommand, enabled: (RemoteCommand) -> Boolean, send: (RemoteCommand) -> Unit,
    icon: ImageVector? = null, color: Color = RemoteColors.Foreground, size: Int = 56) {
    FilledTonalButton(onClick = { send(command) }, enabled = enabled(command), modifier = Modifier.size(size.dp), shape = CircleShape,
        contentPadding = PaddingValues(0.dp), colors = ButtonDefaults.filledTonalButtonColors(containerColor = RemoteColors.Surface,
            contentColor = color, disabledContainerColor = RemoteColors.Surface, disabledContentColor = color.copy(alpha = .45f))) {
        if (icon != null) Icon(icon, command.label, Modifier.size(if (size > 56) 36.dp else 26.dp)) else Text(command.label)
    }
}
@Composable private fun DiagnosticDialog(state: RemoteState, onRefresh: () -> Unit, onClose: () -> Unit) {
    val d = state.diagnostic
    AlertDialog(onDismissRequest = onClose, title = { Text("Diagnóstico infravermelho") }, text = {
        Column(Modifier.verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("${Build.MANUFACTURER} ${Build.MODEL} • Android ${Build.VERSION.RELEASE}")
            Text("Recurso consumer IR: ${if (d.featureDeclared) "declarado" else "não declarado"}")
            Text("Serviço Android IR: ${if (d.serviceAvailable) "disponível" else "ausente"}")
            Text("Emissor: ${if (d.emitterPresent) "detectado" else "não detectado"}")
            Text("Frequências (Hz): ${d.ranges.joinToString { "${it.minHz}–${it.maxHz}" }.ifBlank { "não informadas" }}")
            d.error?.let { Text(it, color = RemoteColors.Power) }
            Text("Códigos confirmados: ${PhilipsProfile.signals.size}/${RemoteCommand.entries.size}")
            Text("Sem códigos confirmados, nenhum sinal é emitido. Este diagnóstico consulta o Android; não comprova a resposta da TV nem mede a emissão óptica.")
            Text("Celulares sem emissor integrado não transmitem pelo ConsumerIrManager. Wi-Fi, Bluetooth e câmera não substituem o emissor.")
        }
    }, confirmButton = { TextButton(onClick = onClose) { Text("Fechar") } }, dismissButton = {
        TextButton(onClick = onRefresh, enabled = !state.checking && !state.sending) { Text(if (state.checking) "Verificando…" else "Verificar novamente") }
    })
}
'''
FILES['app/src/test/java/com/philipsremote/ir/IrControllerTest.kt'] = '''package com.philipsremote.ir
import org.junit.Assert.*
import org.junit.Test

class IrControllerTest {
    // Synthetic timings only for unit tests; never loaded by the app profile.
    private val signal = ConfirmedSignal(TARGET_MODEL, "Synthetic fixture, not a TV code", true, 38000, listOf(listOf(100, 200)))
    private class FakeBackend : IrBackend {
        var state = IrDiagnostic(true, true, true, listOf(FrequencyRange(36000, 40000)))
        val sent = mutableListOf<List<Int>>()
        var fail = false
        override fun diagnose() = state
        override fun transmit(carrierHz: Int, patternMicros: IntArray) {
            if (fail) throw SecurityException("Test service failure")
            sent.add(patternMicros.toList())
        }
    }
    @Test fun everyUnconfirmedCommandIsBlocked() {
        assertEquals(34, RemoteCommand.entries.size)
        assertTrue(PhilipsProfile.signals.isEmpty())
        val backend = FakeBackend()
        val controller = IrController(backend, nowMillis = { 0L })
        RemoteCommand.entries.forEach { assertTrue(controller.send(it) is SendResult.Blocked) }
        assertTrue(backend.sent.isEmpty())
    }
    @Test fun noEmitterBlocksConfiguredSignal() {
        val backend = FakeBackend().apply { state = state.copy(emitterPresent = false) }
        val controller = IrController(backend, mapOf(RemoteCommand.POWER to signal)) { 0L }
        assertTrue(controller.send(RemoteCommand.POWER) is SendResult.Blocked)
        assertTrue(backend.sent.isEmpty())
    }
    @Test fun unknownFrequenciesBlockSending() {
        val backend = FakeBackend().apply { state = state.copy(ranges = emptyList()) }
        assertNotNull(validationError(signal, backend.state))
    }
    @Test fun incompatibleFrequencyIsBlocked() {
        assertNotNull(validationError(signal.copy(carrierHz = 50000), FakeBackend().state))
    }
    @Test fun wrongModelIsBlocked() { assertNotNull(validationError(signal.copy(model = "OTHER"), FakeBackend().state)) }
    @Test fun missingEvidenceIsBlocked() { assertNotNull(validationError(signal.copy(source = ""), FakeBackend().state)) }
    @Test fun unconfirmedEvidenceIsBlocked() { assertNotNull(validationError(signal.copy(confirmedOnDevice = false), FakeBackend().state)) }
    @Test fun twoSecondPatternIsBlocked() {
        assertNotNull(validationError(signal.copy(frames = listOf(listOf(1_000_000, 1_000_000))), FakeBackend().state))
    }
    @Test fun zeroDurationIsBlocked() {
        assertNotNull(validationError(signal.copy(frames = listOf(listOf(100, 0))), FakeBackend().state))
    }
    @Test fun invalidSecondToggleFrameIsBlocked() {
        assertNotNull(validationError(signal.copy(frames = listOf(listOf(100, 200), listOf(-1, 200))), FakeBackend().state))
    }
    @Test fun confirmedSyntheticSignalReachesBackend() {
        val backend = FakeBackend()
        val controller = IrController(backend, mapOf(RemoteCommand.POWER to signal)) { 0L }
        assertEquals(SendResult.Transmitted, controller.send(RemoteCommand.POWER))
        assertEquals(listOf(listOf(100, 200)), backend.sent)
    }
    @Test fun rateLimitBlocksRapidTaps() {
        val backend = FakeBackend(); var clock = 1000L
        val controller = IrController(backend, mapOf(RemoteCommand.POWER to signal)) { clock }
        assertEquals(SendResult.Transmitted, controller.send(RemoteCommand.POWER))
        clock = 1149L
        assertTrue(controller.send(RemoteCommand.POWER) is SendResult.Blocked)
        clock = 1150L
        assertEquals(SendResult.Transmitted, controller.send(RemoteCommand.POWER))
        assertEquals(2, backend.sent.size)
    }
    @Test fun serviceFailureDoesNotReportSuccess() {
        val backend = FakeBackend().apply { fail = true }
        val controller = IrController(backend, mapOf(RemoteCommand.POWER to signal)) { 0L }
        assertTrue(controller.send(RemoteCommand.POWER) is SendResult.Failed)
        assertTrue(backend.sent.isEmpty())
    }
    @Test fun successfulPressAlternatesCapturedFrames() {
        val backend = FakeBackend(); var clock = 0L
        val controller = IrController(backend, mapOf(RemoteCommand.POWER to signal.copy(frames = listOf(listOf(100,200), listOf(300,400))))) { clock }
        repeat(3) { assertEquals(SendResult.Transmitted, controller.send(RemoteCommand.POWER)); clock += 150L }
        assertEquals(listOf(listOf(100,200), listOf(300,400), listOf(100,200)), backend.sent)
    }
}
'''
FILES['README.md'] = '''# Philips Remote — Android nativo

Projeto-fonte Kotlin / Jetpack Compose para Philips 26PFL3404. O PWA existente permanece separado.

## Estado da entrega
- Interface nativa em português, com controles circulares, navegação, canal, volume, teclado e funções extras.
- Diagnóstico real usando PackageManager e ConsumerIrManager, refeito ao voltar para o app.
- Envio síncrono via ConsumerIrManager fora da thread da interface, serializado e com proteção entre toques.
- **0 de 34 comandos configurados.** Nenhum código deste modelo foi confirmado na pesquisa; todos permanecem desativados.
- Não é um APK: sincronização Gradle, compilação Android/Compose e execução em aparelho real não foram verificadas neste ambiente.
- Os 14 testes do núcleo IR foram compilados com Kotlin 2.1.20/JVM 17 e executados com JUnit 4.13.2; todos passaram. Isso não substitui a compilação Android nem valida a aparência da tela Compose.
- O diagnóstico detecta o serviço/hardware declarado; não prova emissão óptica nem resposta da TV. Não há confirmação de recebimento no IR.

## Abrir e compilar
1. Extraia o ZIP e abra a pasta PhilipsRemote no Android Studio compatível com AGP 8.9.2 (Meerkat ou superior).
2. Configure o Gradle JDK 17 e instale Android SDK Platform 35. Permita sincronizar dependências via internet.
3. Execute os testes: `./gradlew testDebugUnitTest` (Windows: `gradlew.bat testDebugUnitTest`).
4. Gere o APK: `./gradlew assembleDebug`. Resultado: `app/build/outputs/apk/debug/app-debug.apk`.
5. Instale no Android 8.0 ou superior e abra Diagnóstico IR no botão de configurações.

O wrapper Gradle 8.11.1 está incluído com checksum da distribuição. Não há chaves, credenciais ou permissão de internet no app.
TRANSMIT_IR é uma permissão normal, não exige diálogo em tempo de execução. O recurso consumerir é opcional para permitir diagnóstico em aparelhos sem IR.

## Configurar somente após confirmar
O arquivo `app/src/main/java/com/philipsremote/ir/IrCore.kt` mantém `PhilipsProfile.signals` vazio.
Cada entrada futura exige modelo exato, referência documentada, confirmação no aparelho, frequência medida em Hz e durações ON/OFF positivas em microssegundos (iniciando ON), total inferior a 2 segundos por quadro.
A documentação oficial Philips para 26PFL3404/78 identifica o controle como tipo PF01L09B. Isso identifica o controle de referência, mas não fornece os pulsos IR nem confirma todos os códigos. Registre o sufixo completo da TV, o controle original e a metodologia na evidência `source` antes de confirmar compatibilidade. O alvo base é 26PFL3404; nenhum sufixo regional foi presumido.
`frames` aceita quadros alternados quando capturas verificadas exigirem toggle RC5/RC6; a alternância só avança após sucesso da API. Não há codificador inventado, varredura de códigos nem repetição automática por toque longo.
Os números sintéticos dos testes não são códigos Philips e nunca entram no perfil do aplicativo.

## Validação física pendente
- Aparelho sem IR: diagnóstico indica indisponibilidade e nenhuma transmissão ocorre.
- Aparelho com IR: verificar recurso, serviço, emissor e faixas suportadas.
- Capturar e documentar sinais do controle original ou fonte específica do modelo; confirmar cada comando na TV.
- Só então cadastrar os comandos confirmados e testar emissor real, toques sucessivos, orientação, fonte ampliada, retorno ao app e falhas do serviço.

## Fontes consultadas
- https://developer.android.com/reference/kotlin/android/hardware/ConsumerIrManager
- https://developer.android.com/reference/android/hardware/ConsumerIrManager.CarrierFrequencyRange
- https://www.documents.philips.com/assets/20230222/10359af7374d449d9998afb100ad343b.pdf
- https://sbprojects.net/knowledge/ir/rc5.php
- https://raw.githubusercontent.com/Lucaslhm/Flipper-IRDB/refs/heads/main/TVs/Philips/Philips_TV_Universal.ir

As fontes Philips genéricas/RC5/RC6 não confirmam códigos específicos para 26PFL3404; portanto não foram incorporadas. A ficha técnica Philips não fornece uma tabela de pulsos IR.
'''

def generate():
    for relative, content in FILES.items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
    logo = Image.open(Path(__file__).resolve().parents[1] / 'public/apple-touch-icon.png')
    res = ROOT / 'app/src/main/res'
    for density, size in [('mdpi',48),('hdpi',72),('xhdpi',96),('xxhdpi',144),('xxxhdpi',192)]:
        path = res / f'mipmap-{density}/ic_launcher.png'
        path.parent.mkdir(parents=True, exist_ok=True)
        logo.resize((size,size), Image.Resampling.LANCZOS).save(path)
    (res / 'drawable').mkdir(exist_ok=True)
    logo.save(res / 'drawable/remote_logo.png')
    base = 'https://raw.githubusercontent.com/gradle/gradle/v8.11.1/'
    for relative in ['gradlew','gradlew.bat','gradle/wrapper/gradle-wrapper.jar']:
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(base+relative, timeout=30) as response:
            path.write_bytes(response.read())
    (ROOT / 'gradlew').chmod(0o755)
    with urllib.request.urlopen('https://services.gradle.org/distributions/gradle-8.11.1-bin.zip.sha256', timeout=30) as response:
        sha = response.read().decode().strip()
    assert len(sha) == 64 and all(c in '0123456789abcdef' for c in sha)
    (ROOT/'gradle/wrapper/gradle-wrapper.properties').write_text('distributionBase=GRADLE_USER_HOME\ndistributionPath=wrapper/dists\ndistributionUrl=https\\://services.gradle.org/distributions/gradle-8.11.1-bin.zip\nnetworkTimeout=10000\nvalidateDistributionUrl=true\nzipStoreBase=GRADLE_USER_HOME\nzipStorePath=wrapper/dists\ndistributionSha256Sum='+sha+'\n')
    print(f'Generated source: {ROOT}')

if __name__ == '__main__':
    generate()
