package com.jarvies.ai;

import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.media.AudioManager;
import android.os.BatteryManager;
import android.os.Build;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.speech.tts.TextToSpeech;
import android.webkit.JavascriptInterface;
import android.widget.Toast;

import java.util.Locale;

public class AndroidJarvisBridge {
    private final MainActivity activity;
    private final Context context;
    private TextToSpeech tts;
    private boolean ttsReady = false;

    public AndroidJarvisBridge(MainActivity activity) {
        this.activity = activity;
        this.context = activity.getApplicationContext();

        try {
            tts = new TextToSpeech(context, status -> {
                if (status == TextToSpeech.SUCCESS) {
                    tts.setLanguage(new Locale("en", "IN"));
                    ttsReady = true;
                }
            });
        } catch (Exception ignored) {}
    }

    @JavascriptInterface
    public void vibrate(long ms) {
        try {
            Vibrator v = (Vibrator) context.getSystemService(Context.VIBRATOR_SERVICE);
            if (v != null && v.hasVibrator()) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    v.vibrate(VibrationEffect.createOneShot(ms, VibrationEffect.DEFAULT_AMPLITUDE));
                } else {
                    v.vibrate(ms);
                }
            }
        } catch (Exception ignored) {}
    }

    @JavascriptInterface
    public void volumeUp() {
        try {
            AudioManager am = (AudioManager) context.getSystemService(Context.AUDIO_SERVICE);
            if (am != null) {
                am.adjustStreamVolume(AudioManager.STREAM_MUSIC, AudioManager.ADJUST_RAISE, AudioManager.FLAG_SHOW_UI);
            }
        } catch (Exception ignored) {}
    }

    @JavascriptInterface
    public void volumeDown() {
        try {
            AudioManager am = (AudioManager) context.getSystemService(Context.AUDIO_SERVICE);
            if (am != null) {
                am.adjustStreamVolume(AudioManager.STREAM_MUSIC, AudioManager.ADJUST_LOWER, AudioManager.FLAG_SHOW_UI);
            }
        } catch (Exception ignored) {}
    }

    @JavascriptInterface
    public void setVolume(int percent) {
        try {
            AudioManager am = (AudioManager) context.getSystemService(Context.AUDIO_SERVICE);
            if (am != null) {
                int max = am.getStreamMaxVolume(AudioManager.STREAM_MUSIC);
                int target = (int) ((percent / 100.0f) * max);
                am.setStreamVolume(AudioManager.STREAM_MUSIC, target, AudioManager.FLAG_SHOW_UI);
            }
        } catch (Exception ignored) {}
    }

    @JavascriptInterface
    public int getBatteryPercent() {
        try {
            IntentFilter ifilter = new IntentFilter(Intent.ACTION_BATTERY_CHANGED);
            Intent batteryStatus = context.registerReceiver(null, ifilter);
            if (batteryStatus != null) {
                int level = batteryStatus.getIntExtra(BatteryManager.EXTRA_LEVEL, -1);
                int scale = batteryStatus.getIntExtra(BatteryManager.EXTRA_SCALE, -1);
                return (int) ((level / (float) scale) * 100);
            }
        } catch (Exception ignored) {}
        return 100;
    }

    @JavascriptInterface
    public boolean isBatteryCharging() {
        try {
            IntentFilter ifilter = new IntentFilter(Intent.ACTION_BATTERY_CHANGED);
            Intent batteryStatus = context.registerReceiver(null, ifilter);
            if (batteryStatus != null) {
                int status = batteryStatus.getIntExtra(BatteryManager.EXTRA_STATUS, -1);
                return status == BatteryManager.BATTERY_STATUS_CHARGING ||
                        status == BatteryManager.BATTERY_STATUS_FULL;
            }
        } catch (Exception ignored) {}
        return false;
    }

    @JavascriptInterface
    public void openApp(String appName) {
        activity.runOnUiThread(() -> {
            try {
                String pkg = null;
                String lower = appName.toLowerCase();
                if (lower.contains("youtube")) pkg = "com.google.android.youtube";
                else if (lower.contains("whatsapp")) pkg = "com.whatsapp";
                else if (lower.contains("spotify")) pkg = "com.spotify.music";
                else if (lower.contains("chrome")) pkg = "com.android.chrome";
                else if (lower.contains("calc")) pkg = "com.google.android.calculator";

                if (pkg != null) {
                    Intent launchIntent = context.getPackageManager().getLaunchIntentForPackage(pkg);
                    if (launchIntent != null) {
                        launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                        context.startActivity(launchIntent);
                        return;
                    }
                }
                showToast("Opening " + appName);
            } catch (Exception e) {
                showToast("App not found: " + appName);
            }
        });
    }

    @JavascriptInterface
    public void speakNative(String text) {
        if (ttsReady && tts != null) {
            tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "JARVIS_NATIVE_TTS");
        }
    }

    @JavascriptInterface
    public void showToast(String message) {
        activity.runOnUiThread(() -> 
            Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
        );
    }

    @JavascriptInterface
    public void openServerSettings() {
        activity.runOnUiThread(activity::showServerSettingsDialog);
    }
}
