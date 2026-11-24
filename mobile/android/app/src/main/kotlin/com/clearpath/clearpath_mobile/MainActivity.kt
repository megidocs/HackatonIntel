package com.clearpath.clearpath_mobile

import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import android.speech.tts.TextToSpeech
import java.util.Locale

class MainActivity : FlutterActivity() {
    private var speaker: TextToSpeech? = null
    private var ready = false

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        speaker = TextToSpeech(this) { status ->
            val language = speaker?.setLanguage(Locale.US)
            ready = status == TextToSpeech.SUCCESS && language != null && language >= 0
        }
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "clearpath/alerts")
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "speak" -> {
                        val sentence = call.arguments as? String
                        val spoken = ready && sentence != null &&
                            speaker?.speak(sentence, TextToSpeech.QUEUE_FLUSH, null, "clearpath-alert") ==
                            TextToSpeech.SUCCESS
                        if (spoken) result.success(null)
                        else result.error("speech_unavailable", "Android speech unavailable", null)
                    }
                    "stop" -> {
                        speaker?.stop()
                        result.success(null)
                    }
                    else -> result.notImplemented()
                }
            }
    }

    override fun onDestroy() {
        speaker?.shutdown()
        speaker = null
        ready = false
        super.onDestroy()
    }
}
