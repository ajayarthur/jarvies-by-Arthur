import * as Speech from "expo-speech";
import { Audio } from "expo-av";
import * as Haptics from "expo-haptics";
import { StorageService } from "./storage";

let soundObject = null;

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

  async playAudioUrl(audioUrl, onFinish = null) {
    try {
      await this.stopAudio();

      await Audio.setAudioModeAsync({
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
    } catch {}
  }
};
