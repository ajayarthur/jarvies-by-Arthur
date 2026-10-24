import * as Speech from "expo-speech";
import { Audio } from "expo-av";
import * as Haptics from "expo-haptics";
import { StorageService } from "./storage";

let soundObject = null;
let activeRecording = null;

export const SpeechService = {
  async triggerHaptic(type = "light") {
    try {
      const prefs = await StorageService.getPreferences();
      if (!prefs.hapticFeedback) return;

      if (type === "medium") {
        await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      } else if (type === "success") {
        await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      } else if (type === "warning") {
        await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
      } else {
        await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      }
    } catch {}
  },

  async requestMicPermissions() {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      return status === "granted";
    } catch {
      return false;
    }
  },

  async startVoiceRecording() {
    try {
      const granted = await this.requestMicPermissions();
      if (!granted) return false;

      await this.stopAudio();

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
        shouldDuckAndroid: true,
        playThroughEarpieceAndroid: false
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      activeRecording = recording;
      return true;
    } catch (err) {
      console.warn("Start voice recording error:", err);
      activeRecording = null;
      return false;
    }
  },

  async stopVoiceRecordingAndTranscribe() {
    try {
      if (!activeRecording) return "";

      await activeRecording.stopAndUnloadAsync();
      const uri = activeRecording.getURI();
      activeRecording = null;

      if (!uri) return "";

      const baseUrl = await StorageService.getHostUrl();
      const token = await StorageService.getAuthToken();

      const formData = new FormData();
      formData.append("file", {
        uri: uri,
        type: "audio/wav",
        name: "mobile_voice.wav"
      });

      const headers = {};
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
        headers["X-Jarvis-Token"] = token;
      }

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 12000);

      const res = await fetch(`${baseUrl}/api/voice/transcribe`, {
        method: "POST",
        headers,
        body: formData,
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (!res.ok) return "";
      const data = await res.json();
      return data.transcript || "";
    } catch (err) {
      console.warn("Transcribe voice error:", err);
      return "";
    }
  },

  async playAudioUrl(audioUrl, onFinish = null) {
    try {
      await this.stopAudio();

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
        playsInSilentModeIOS: true,
        staysActiveInBackground: false,
        shouldDuckAndroid: true,
        playThroughEarpieceAndroid: false
      });

      const baseUrl = await StorageService.getHostUrl();
      const fullUrl = audioUrl.startsWith("http") ? audioUrl : `${baseUrl}${audioUrl}`;

      const { sound } = await Audio.Sound.createAsync(
        { uri: fullUrl },
        { shouldPlay: true }
      );

      soundObject = sound;

      sound.setOnPlaybackStatusUpdate((status) => {
        if (status.didJustFinish) {
          if (onFinish) onFinish();
          sound.unloadAsync();
          soundObject = null;
        }
      });
    } catch (err) {
      console.warn("Audio playback error, falling back to local TTS:", err);
      if (onFinish) onFinish();
    }
  },

  async speakLocalText(text, onFinish = null) {
    try {
      await this.stopAudio();
      const prefs = await StorageService.getPreferences();

      Speech.speak(text, {
        language: "en-IN",
        pitch: 1.0,
        rate: prefs.speechRate || 1.0,
        onDone: () => {
          if (onFinish) onFinish();
        },
        onError: () => {
          if (onFinish) onFinish();
        }
      });
    } catch {
      if (onFinish) onFinish();
    }
  },

  async stopAudio() {
    try {
      Speech.stop();
      if (soundObject) {
        await soundObject.stopAsync();
        await soundObject.unloadAsync();
        soundObject = null;
      }
      if (activeRecording) {
        await activeRecording.stopAndUnloadAsync();
        activeRecording = null;
      }
    } catch {}
  }
};
