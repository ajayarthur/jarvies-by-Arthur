import AsyncStorage from "@react-native-async-storage/async-storage";

const KEYS = {
  HOST_URL: "@jarvis_host_url",
  AUTH_TOKEN: "@jarvis_auth_token",
  ASSISTANT_NAME: "@jarvis_assistant_name",
  VOICE_PREF: "@jarvis_voice_pref",
  SPEECH_RATE: "@jarvis_speech_rate",
  CHAT_HISTORY: "@jarvis_chat_history",
  AUDIO_FEEDBACK: "@jarvis_audio_feedback",
  HAPTIC_FEEDBACK: "@jarvis_haptic_feedback"
};

export const DEFAULT_CONFIG = {
  hostUrl: "http://192.168.1.100:7777",
  assistantName: "Jarvies",
  voicePref: "en-IN-PrabhatNeural",
  speechRate: 1.0,
  audioFeedback: true,
  hapticFeedback: true
};

export const StorageService = {
  async getHostUrl() {
    const val = await AsyncStorage.getItem(KEYS.HOST_URL);
    return val || DEFAULT_CONFIG.hostUrl;
  },

  async setHostUrl(url) {
    const clean = url.trim().replace(/\/+$/, "");
    await AsyncStorage.setItem(KEYS.HOST_URL, clean);
  },

  async getAuthToken() {
    return await AsyncStorage.getItem(KEYS.AUTH_TOKEN);
  },

  async setAuthToken(token) {
    if (token) {
      await AsyncStorage.setItem(KEYS.AUTH_TOKEN, token);
    } else {
      await AsyncStorage.removeItem(KEYS.AUTH_TOKEN);
    }
  },

  async getAssistantName() {
    const name = await AsyncStorage.getItem(KEYS.ASSISTANT_NAME);
    return name || DEFAULT_CONFIG.assistantName;
  },

  async setAssistantName(name) {
    await AsyncStorage.setItem(KEYS.ASSISTANT_NAME, name.trim());
  },

  async getPreferences() {
    try {
      const voice = (await AsyncStorage.getItem(KEYS.VOICE_PREF)) || DEFAULT_CONFIG.voicePref;
      const rateStr = await AsyncStorage.getItem(KEYS.SPEECH_RATE);
      const audio = await AsyncStorage.getItem(KEYS.AUDIO_FEEDBACK);
      const haptic = await AsyncStorage.getItem(KEYS.HAPTIC_FEEDBACK);

      return {
        voicePref: voice,
        speechRate: rateStr ? parseFloat(rateStr) : DEFAULT_CONFIG.speechRate,
        audioFeedback: audio !== null ? audio === "true" : DEFAULT_CONFIG.audioFeedback,
        hapticFeedback: haptic !== null ? haptic === "true" : DEFAULT_CONFIG.hapticFeedback
      };
    } catch {
      return DEFAULT_CONFIG;
    }
  },

  async savePreferences(prefs) {
    if (prefs.voicePref) await AsyncStorage.setItem(KEYS.VOICE_PREF, prefs.voicePref);
    if (prefs.speechRate) await AsyncStorage.setItem(KEYS.SPEECH_RATE, prefs.speechRate.toString());
    if (prefs.audioFeedback !== undefined) await AsyncStorage.setItem(KEYS.AUDIO_FEEDBACK, String(prefs.audioFeedback));
    if (prefs.hapticFeedback !== undefined) await AsyncStorage.setItem(KEYS.HAPTIC_FEEDBACK, String(prefs.hapticFeedback));
  },

  async getHistory() {
    try {
      const raw = await AsyncStorage.getItem(KEYS.CHAT_HISTORY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  },

  async saveHistory(messages) {
    try {
      // Keep most recent 50 messages to save space
      const capped = messages.slice(-50);
      await AsyncStorage.setItem(KEYS.CHAT_HISTORY, JSON.stringify(capped));
    } catch {}
  },

  async clearHistory() {
    await AsyncStorage.removeItem(KEYS.CHAT_HISTORY);
  },

  async unpair() {
    await AsyncStorage.removeItem(KEYS.AUTH_TOKEN);
  }
};
