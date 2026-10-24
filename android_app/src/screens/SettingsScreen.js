import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Switch,
  Alert,
  ActivityIndicator
} from "react-native";
import { COLORS } from "../theme/colors";
import { StorageService } from "../services/storage";
import { JarvisApi } from "../services/api";
import { SpeechService } from "../services/speech";

export function SettingsScreen({ onBack }) {
  const [hostUrl, setHostUrl] = useState("");
  const [pairingCode, setPairingCode] = useState("");
  const [authToken, setAuthToken] = useState(null);
  const [assistantName, setAssistantName] = useState("Jarvies");
  const [voicePref, setVoicePref] = useState("en-IN-PrabhatNeural");
  const [audioFeedback, setAudioFeedback] = useState(true);
  const [hapticFeedback, setHapticFeedback] = useState(true);

  const [testingConnection, setTestingConnection] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [pairingLoading, setPairingLoading] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    const url = await StorageService.getHostUrl();
    const token = await StorageService.getAuthToken();
    const name = await StorageService.getAssistantName();
    const prefs = await StorageService.getPreferences();

    setHostUrl(url);
    setAuthToken(token);
    setAssistantName(name);
    setVoicePref(prefs.voicePref);
    setAudioFeedback(prefs.audioFeedback);
    setHapticFeedback(prefs.hapticFeedback);
  };

  const handleSaveHost = async () => {
    if (!hostUrl.trim()) return;
    await StorageService.setHostUrl(hostUrl.trim());
    await SpeechService.triggerHaptic("success");
    Alert.alert("Saved", "Companion URL updated.");
  };

  const handlePairDevice = async () => {
    if (!pairingCode.trim()) {
      Alert.alert("Pairing Code Required", "Enter the 6-digit code shown in the PC console.");
      return;
    }

    setPairingLoading(true);
    setTestResult(null);

    try {
      await StorageService.setHostUrl(hostUrl.trim());
      const res = await JarvisApi.pairDevice(pairingCode.trim(), "Android Device");
      setAuthToken(res.token);
      setPairingCode("");
      await SpeechService.triggerHaptic("success");
      Alert.alert("Pairing Successful", `Paired with ${res.server_name} (${res.hostname})!`);
    } catch (err) {
      await SpeechService.triggerHaptic("warning");
      Alert.alert("Pairing Error", err.message);
    } finally {
      setPairingLoading(false);
    }
  };

  const handleUnpair = async () => {
    await StorageService.unpair();
    setAuthToken(null);
    await SpeechService.triggerHaptic("light");
    Alert.alert("Unpaired", "This phone is no longer paired with the PC companion.");
  };

  const handleTestConnection = async () => {
    setTestingConnection(true);
    setTestResult(null);
    const start = Date.now();

    try {
      const health = await JarvisApi.checkHealth(hostUrl.trim());
      const latency = Date.now() - start;

      if (health.status === "healthy") {
        setTestResult({
          success: true,
          message: `Connected! ${health.hostname} (v${health.version}) in ${latency}ms.`
        });
        await SpeechService.triggerHaptic("success");
      } else {
        setTestResult({
          success: false,
          message: `Companion unreachable: ${health.error || "Offline"}`
        });
      }
    } catch (err) {
      setTestResult({ success: false, message: err.message });
    } finally {
      setTestingConnection(false);
    }
  };

  const handleToggleAudio = async (val) => {
    setAudioFeedback(val);
    await StorageService.savePreferences({ audioFeedback: val });
  };

  const handleToggleHaptic = async (val) => {
    setHapticFeedback(val);
    await StorageService.savePreferences({ hapticFeedback: val });
  };

  const handleClearHistory = async () => {
    await StorageService.clearHistory();
    Alert.alert("Cleared", "Conversation history cleared.");
  };

  return (
    <View style={styles.screen}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <Text style={styles.backText}>← Back to HUD</Text>
        </TouchableOpacity>
        <Text style={styles.title}>System Setup</Text>
        <View style={{ width: 60 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {/* Companion Connection Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>COMPANION COMPUTER LINK</Text>
          <Text style={styles.cardSubtitle}>
            Specify your Windows PC's local IP or Cloudflare tunnel address:
          </Text>

          <TextInput
            style={styles.input}
            value={hostUrl}
            onChangeText={setHostUrl}
            placeholder="http://192.168.1.100:7777"
            placeholderTextColor={COLORS.textMuted}
            autoCapitalize="none"
          />

          <View style={styles.buttonRow}>
            <TouchableOpacity onPress={handleSaveHost} style={styles.secondaryButton}>
              <Text style={styles.secondaryButtonText}>Save URL</Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={handleTestConnection}
              disabled={testingConnection}
              style={styles.primaryButton}
            >
              {testingConnection ? (
                <ActivityIndicator color={COLORS.bgPrimary} size="small" />
              ) : (
                <Text style={styles.primaryButtonText}>Test Connection</Text>
              )}
            </TouchableOpacity>
          </View>

          {testResult ? (
            <View
              style={[
                styles.resultBadge,
                { backgroundColor: testResult.success ? "rgba(46, 213, 115, 0.15)" : "rgba(255, 71, 87, 0.15)" }
              ]}
            >
              <Text
                style={[
                  styles.resultText,
                  { color: testResult.success ? COLORS.success : COLORS.danger }
                ]}
              >
                {testResult.message}
              </Text>
            </View>
          ) : null}
        </View>

        {/* Pairing & Security Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>DEVICE PAIRING & AUTHENTICATION</Text>
          <Text style={styles.cardSubtitle}>
            Check your PC console or web dashboard for the 6-digit one-time code:
          </Text>

          {authToken ? (
            <View style={styles.pairedStatusBox}>
              <Text style={styles.pairedText}>🔒 Device Authenticated & Paired</Text>
              <Text style={styles.tokenText}>
                Token: {authToken.substring(0, 14)}•••••••••••••
              </Text>
              <TouchableOpacity onPress={handleUnpair} style={styles.unpairButton}>
                <Text style={styles.unpairText}>Unpair Device</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <>
              <TextInput
                style={[styles.input, styles.codeInput]}
                value={pairingCode}
                onChangeText={setPairingCode}
                placeholder="Enter 6-Digit Code (e.g. 749201)"
                placeholderTextColor={COLORS.textMuted}
                keyboardType="numeric"
                maxLength={6}
              />

              <TouchableOpacity
                onPress={handlePairDevice}
                disabled={pairingLoading}
                style={[styles.primaryButton, { width: "100%", marginTop: 8 }]}
              >
                {pairingLoading ? (
                  <ActivityIndicator color={COLORS.bgPrimary} size="small" />
                ) : (
                  <Text style={styles.primaryButtonText}>Pair with Jarvis Core</Text>
                )}
              </TouchableOpacity>
            </>
          )}
        </View>

        {/* Voice & Speech Preferences */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>VOICE & AUDIO SETTINGS</Text>

          <View style={styles.settingRow}>
            <Text style={styles.settingLabel}>Audio Spoken Feedback</Text>
            <Switch
              value={audioFeedback}
              onValueChange={handleToggleAudio}
              trackColor={{ false: COLORS.bgCardHover, true: COLORS.accentCyan }}
            />
          </View>

          <View style={styles.settingRow}>
            <Text style={styles.settingLabel}>Haptic Touch Vibrations</Text>
            <Switch
              value={hapticFeedback}
              onValueChange={handleToggleHaptic}
              trackColor={{ false: COLORS.bgCardHover, true: COLORS.accentAqua }}
            />
          </View>
        </View>

        {/* Maintenance */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>DATA & PRIVACY</Text>
          <TouchableOpacity onPress={handleClearHistory} style={styles.dangerButton}>
            <Text style={styles.dangerButtonText}>Clear Conversation History</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: COLORS.bgPrimary
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 16,
    paddingTop: 48,
    paddingBottom: 14,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.borderSubtle
  },
  backButton: {
    paddingVertical: 6,
    paddingHorizontal: 8
  },
  backText: {
    color: COLORS.accentCyan,
    fontSize: 14,
    fontWeight: "600"
  },
  title: {
    fontSize: 16,
    fontWeight: "700",
    color: COLORS.textPrimary,
    letterSpacing: 0.5
  },
  content: {
    padding: 18,
    paddingBottom: 40
  },
  card: {
    backgroundColor: COLORS.bgCard,
    borderRadius: 14,
    padding: 18,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: COLORS.borderSubtle
  },
  cardTitle: {
    fontSize: 11,
    fontWeight: "800",
    color: COLORS.accentCyan,
    letterSpacing: 1.2,
    marginBottom: 6
  },
  cardSubtitle: {
    fontSize: 13,
    color: COLORS.textSecondary,
    lineHeight: 18,
    marginBottom: 12
  },
  input: {
    backgroundColor: COLORS.bgSecondary,
    borderWidth: 1,
    borderColor: COLORS.borderSubtle,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    color: COLORS.textPrimary,
    fontSize: 14,
    marginBottom: 12
  },
  codeInput: {
    fontSize: 18,
    letterSpacing: 4,
    textAlign: "center"
  },
  buttonRow: {
    flexDirection: "row",
    justifyContent: "space-between"
  },
  primaryButton: {
    flex: 1,
    backgroundColor: COLORS.accentCyan,
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: "center",
    justifyContent: "center",
    marginLeft: 6
  },
  primaryButtonText: {
    color: COLORS.bgPrimary,
    fontWeight: "700",
    fontSize: 14
  },
  secondaryButton: {
    flex: 1,
    backgroundColor: "rgba(255, 255, 255, 0.08)",
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 6
  },
  secondaryButtonText: {
    color: COLORS.textPrimary,
    fontWeight: "600",
    fontSize: 14
  },
  resultBadge: {
    marginTop: 12,
    padding: 10,
    borderRadius: 8
  },
  resultText: {
    fontSize: 12,
    fontWeight: "600"
  },
  pairedStatusBox: {
    backgroundColor: "rgba(0, 255, 210, 0.08)",
    padding: 14,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: COLORS.accentAqua,
    alignItems: "center"
  },
  pairedText: {
    color: COLORS.accentAqua,
    fontWeight: "700",
    fontSize: 14,
    marginBottom: 4
  },
  tokenText: {
    color: COLORS.textSecondary,
    fontSize: 12,
    marginBottom: 10
  },
  unpairButton: {
    backgroundColor: "rgba(255, 71, 87, 0.15)",
    paddingVertical: 6,
    paddingHorizontal: 14,
    borderRadius: 8
  },
  unpairText: {
    color: COLORS.danger,
    fontSize: 12,
    fontWeight: "700"
  },
  settingRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.borderSubtle
  },
  settingLabel: {
    color: COLORS.textPrimary,
    fontSize: 14,
    fontWeight: "500"
  },
  dangerButton: {
    backgroundColor: "rgba(255, 71, 87, 0.12)",
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "rgba(255, 71, 87, 0.3)"
  },
  dangerButtonText: {
    color: COLORS.danger,
    fontSize: 13,
    fontWeight: "700"
  }
});
