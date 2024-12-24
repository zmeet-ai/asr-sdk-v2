import kotlinx.coroutines.*
import kotlinx.serialization.*
import kotlinx.serialization.json.*
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import okio.ByteString
import java.io.File
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.TimeoutException
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec

val timePerChunk = 0.1 // seconds
val numChannel = 1
val numQuantify = 16
val sampleRate = 16000
val bytesPerChunk = (sampleRate * numQuantify * timePerChunk * numChannel / 8).toInt()

val apiUrl = "wss://asr-dev.abcpen.com"

fun generateSignature(appId: String, apiKey: String): Pair<String, String> {
    val ts = (System.currentTimeMillis() / 1000).toString()
    val tt = (appId + ts).toByteArray(Charsets.UTF_8)
    val md5 = MessageDigest.getInstance("MD5")
    val baseString = md5.digest(tt).joinToString("") { "%02x".format(it) }
    val apiKeyBytes = apiKey.toByteArray(Charsets.UTF_8)
    val hmacSha1 = Mac.getInstance("HmacSHA1")
    hmacSha1.init(SecretKeySpec(apiKeyBytes, "HmacSHA1"))
    val signa = hmacSha1.doFinal(baseString.toByteArray(Charsets.UTF_8)).encodeBase64()
    return Pair(signa, ts)
}

suspend fun sendAudioData(websocket: WebSocket) {
    val filename = "../dataset/test.wav"
    val fileData = File(filename).readBytes()
    val waveFileSampleRate = 16000 // Assuming a constant sample rate
    val numSamples = fileData.size / 2 // Assuming 16-bit samples
    val chunkSize = (timePerChunk * waveFileSampleRate * 2).toInt()

    var start = 0
    while (start < numSamples * 2) {
        val end = minOf(start + chunkSize, numSamples * 2)
        val chunk = fileData.copyOfRange(start, end)
        websocket.send(ByteString.of(*chunk))
        start = end
        delay(30) // Sleep for 30 milliseconds
    }
}

suspend fun receiveRecognitionResult(websocket: WebSocket) {
    var segSentence = 0

    suspend fun waitForMessage(): String {
        val result = CompletableDeferred<String>()
        websocket.listener = object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                result.complete(text)
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                result.completeExceptionally(Exception("Connection closed"))
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: okhttp3.Response?) {
                result.completeExceptionally(t)
            }
        }
        return result.await()
    }

    try {
        while (true) {
            val result = waitForMessage()
            val asrText = Json.decodeFromString<AsrText>(result)
            val asr = asrText.asr
            val asrPunc = asrText.asr_punc ?: ""
            val segId = asrText.seg_id
            val isFinal = asrText.is_final
            val translate = asrText.translate ?: ""

            if (isFinal) {
                println("$segSentence:$asrPunc -> $translate")
                segSentence++
            } else {
                print("$segSentence:$asr -> $translate")
            }
        }
    } catch (err: Exception) {
        println("receiveRecognitionResult error: $err")
    }
}

suspend fun connectToServer() {
    val appId = "test1"
    val appSecret = "2258ACC4-199B-4DCB-B6F3-C2485C63E85A"

    val (signa, ts) = generateSignature(appId, appSecret)

    val baseUrl = "$apiUrl/v2/asr/ws"
    val urlAsrApply = "$baseUrl?appid=$appId&ts=$ts&signa=${signa.encodeURIComponent()}&asr_type=2&trans_mode=1&target_lang=ru&pd=court"

    val client = OkHttpClient()
    val request = Request.Builder().url(urlAsrApply).build()

    val latch = CountDownLatch(1)

    val websocket = client.newWebSocket(request, object : WebSocketListener() {
        override fun onOpen(webSocket: WebSocket, response: okhttp3.Response) {
            GlobalScope.launch {
                try {
                    sendAudioData(webSocket)
                } catch (e: Exception) {
                    println("sendAudioData error: $e")
                }
            }
        }

        override fun onMessage(webSocket: WebSocket, text: String) {
            GlobalScope.launch {
                receiveRecognitionResult(webSocket)
            }
        }

        override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
            latch.countDown()
        }

        override fun onFailure(webSocket: WebSocket, t: Throwable, response: okhttp3.Response?) {
            println("WebSocket error: $t")
            latch.countDown()
        }
    })

    latch.await()
}

fun main() {
    try {
        runBlocking {
            connectToServer()
        }
    } catch (err: Exception) {
        println("connectToServer error: $err")
    }
}

fun String.encodeURIComponent(): String {
    return URLEncoder.encode(this, "UTF-8")
}

fun String.decodeBase64(): ByteArray {
    return Base64.getDecoder().decode(this)
}

fun ByteArray.encodeBase64(): String {
    return Base64.getEncoder().encodeToString(this)
}

data class AsrText(
    val asr: String,
    val asr_punc: String? = null,
    val seg_id: String,
    val is_final: Boolean,
    val translate: String? = null
)
