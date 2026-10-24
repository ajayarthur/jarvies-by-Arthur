import React, { useState, useEffect, useRef } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Alert
} from "react-native";
import { COLORS } from "../theme/colors";
import { ArcReactor } from "../components/ArcReactor";
import { AudioWaveform } from "../components/AudioWaveform";
import { ConnectionBadge } from "../components/ConnectionBadge";
import { ConfirmationModal } from "../components/ConfirmationModal";
import { JarvisApi } from "../services/api";
import { SpeechService } from "../services/speech";
import { StorageService } from "../services/storage";
import { DeepLinkService } from "../services/deepLinks";

export function MainAssistantScreen({ onNavigateSettings, onNavigateCapabilities }) {
  // Connection & Core States
  const [connectionStatus, setConnectionStatus] = useState("connecting");
  const [companionHost, setCompanionHost] = useState("PC");
  const [assistantState, setAssistantState] = useState("idle"); // idle, listening, processing, speaking, offline

  // Query & Response
  const [transcript, setTranscript] = useState("");
  const [responseMessage, setResponseMessage] = useState("Jarvies Core Ready. Tap the Arc Reactor to speak.");
  const [lastExecutedTool, setLastExecutedTool] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [textInput, setTextInput] = useState("");

  // High-Impact Security Confirmation Modal
  const [confirmModalVisible, setConfirmModalVisible] = useState(false);
  const [pendingAction, setPendingAction] = useState(null);

  const scrollViewRef = useRef(null);

  // Initialize & Monitor Companion Health
  useEffect(() => {
    checkCompanionHealth();
    const interval = setInterval(checkCompanionHealth, 12000);
    return () => clearInterval(interval);
  }, []);

  const checkCompanionHealth = async () => {
    try {
      const health = await JarvisApi.checkHealth();
      if (health.status === "healthy") {
        setConnectionStatus("online");
        setCompanionHost(health.hostname || "PC Companion");
      } else {
        setConnectionStatus("offline");
      }
    } catch {
      setConnectionStatus("offline");
    }
  };

  // Handle Voice Interaction
  const handleArcReactorPress = async () => {
    await SpeechService.triggerHaptic("medium");

    // If already speaking, stop playback
    if (assistantState === "speaking") {
      await SpeechService.stopAudio();
      setAssistantState("idle");
      return;
    }

    if (assistantState === "listening") {
      // User finished speaking: stop recording and transcribe!
      setAssistantState("processing");
      setResponseMessage("Transcribing voice audio...");

      const transcribed = await SpeechService.stopVoiceRecordingAndTranscribe();
      if (transcribed && transcribed.trim()) {
        setTranscript(transcribed);
        await submitCommand(transcribed);
      } else {
        setAssistantState("idle");
        setResponseMessage("No speech detected, sir. Please try speaking again.");
      }
    } else {
      // Start recording voice input
      const started = await SpeechService.startVoiceRecording();
      if (started) {
        setAssistantState("listening");
        setTranscript("");
        setResponseMessage("Listening to you, sir... Speak your command, then tap the Arc Reactor to execute.");
        setLastExecutedTool(null);
      } else {
        Alert.alert(
          "Microphone Permission Required",
          "Jarvis needs access to your microphone to capture voice commands."
        );
        setAssistantState("idle");
      }
    }
  };

  // Submit Command to Companion Engine
  const submitCommand = async (commandText) => {
    const clean = commandText.trim();
    if (!clean) return;

    setAssistantState("processing");
    setTranscript(clean);
    setResponseMessage("Processing query and consulting Jarvis tools...");

    try {
      const prefs = await StorageService.getPreferences();
      const res = await JarvisApi.sendCommand(clean, prefs.voicePref);

      // 1. Check if high-impact confirmation required
      if (res.requires_confirmation && res.pending_action_id) {
        setPendingAction({
          id: res.pending_action_id,
          type: res.action_type,
          description: res.action_description || res.reply
        });
        setConfirmModalVisible(true);
        setAssistantState("idle");
        setResponseMessage(res.reply);
        return;
      }

      // 2. Normal execution result
      setResponseMessage(res.reply || "Task completed.");
      setLastExecutedTool(res.tool_executed);

      // 3. Check for mobile deep linking actions
      if (res.tool_executed && res.tool_executed.startsWith("open_")) {
        const appKey = res.tool_executed.replace("open_", "");
        await DeepLinkService.openApp(appKey);
      }

      // 4. Voice playback of response
      if (res.audio_url) {
        setAudioUrl(res.audio_url);
        setAssistantState("speaking");
        await SpeechService.playAudioUrl(res.audio_url, () => {
          setAssistantState("idle");
        });
      } else if (prefs.audioFeedback && res.reply) {
        setAssistantState("speaking");
        await SpeechService.speakLocalText(res.reply, () => {
          setAssistantState("idle");
        });
      } else {
        setAssistantState("idle");
      }

      // Save to conversation history
      const history = await StorageService.getHistory();
      history.push({ role: "user", text: clean, timestamp: Date.now() });
      history.push({ role: "assistant", text: res.reply, tool: res.tool_executed, timestamp: Date.now() });
      await StorageService.saveHistory(history);

    } catch (err) {
      setAssistantState("idle");
      setResponseMessage(`Error: ${err.message}`);
      await SpeechService.triggerHaptic("warning");
    }
  };

  // Confirm High-Impact Action
  const handleAuthorizeAction = async () => {
    if (!pendingAction) return;
    setConfirmModalVisible(false);
    setAssistantState("processing");
    setResponseMessage(`Authorizing ${pendingAction.description}...`);

    try {
      const res = await JarvisApi.confirmAction(pendingAction.id, true);
      setResponseMessage(res.result || res.message || "Action executed successfully.");
      setAssistantState("idle");
      setPendingAction(null);
    } catch (err) {
      setResponseMessage(`Action failed: ${err.message}`);
      setAssistantState("idle");
      setPendingAction(null);
    }
  };

  // Cancel High-Impact Action
  const handleCancelAction = async () => {
    if (pendingAction) {
      await JarvisApi.confirmAction(pendingAction.id, false);
    }
    setConfirmModalVisible(false);
    setPendingAction(null);
    setResponseMessage("Operation cancelled by user.");
    setAssistantState("idle");
  };

  const handleStopActive = async () => {
    await SpeechService.stopAudio();
    setAssistantState("idle");
    setResponseMessage("Jarvies Core Ready.");
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      style={styles.screen}
    >
      {/* Top Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onNavigateCapabilities} style={styles.navButton}>
          <Text style={styles.navIcon}>⚡</Text>
          <Text style={styles.navLabel}>Tools</Text>
        </TouchableOpacity>

        <ConnectionBadge
          status={connectionStatus}
          hostname={companionHost}
          onPress={checkCompanionHealth}
        />

        <TouchableOpacity onPress={onNavigateSettings} style={styles.navButton}>
          <Text style={styles.navIcon}>⚙️</Text>
          <Text style={styles.navLabel}>Setup</Text>
        </TouchableOpacity>
      </View>

      <ScrollView
        ref={scrollViewRef}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Arc Reactor Holographic Center */}
        <View style={styles.reactorSection}>
          <ArcReactor state={assistantState} onPress={handleArcReactorPress} />
          <Text style={styles.stateSubtitle}>
            {assistantState === "listening"
              ? "LISTENING (SPEAK NOW)"
              : assistantState === "speaking"
              ? "SPEAKING NEURAL VOICE"
              : assistantState === "processing"
              ? "THINKING & ROUTING TOOLS"
              : "JARVIES HOLOGRAPHIC CORE"}
          </Text>
        </View>

        {/* Realtime Waveform Visualizer */}
        <AudioWaveform
          isActive={assistantState === "listening" || assistantState === "speaking"}
          color={assistantState === "listening" ? COLORS.accentAqua : COLORS.accentCyan}
        />

        {/* Live Speech Transcript Bubble */}
        {transcript ? (
          <View style={styles.transcriptCard}>
            <Text style={styles.speakerTag}>YOU</Text>
            <Text style={styles.transcriptText}>"{transcript}"</Text>
          </View>
        ) : null}

        {/* AI Response Card */}
        <View style={styles.responseCard}>
          <View style={styles.responseHeader}>
            <Text style={styles.assistantTag}>JARVIES 4.0</Text>
            {lastExecutedTool ? (
              <View style={styles.toolBadge}>
                <Text style={styles.toolBadgeText}>🔧 {lastExecutedTool}</Text>
              </View>
            ) : null}
          </View>

          <Text style={styles.responseText}>{responseMessage}</Text>

          {audioUrl && assistantState !== "speaking" ? (
            <TouchableOpacity
              onPress={() => {
                setAssistantState("speaking");
                SpeechService.playAudioUrl(audioUrl, () => setAssistantState("idle"));
              }}
              style={styles.replayButton}
            >
              <Text style={styles.replayButtonText}>🔊 Replay Voice</Text>
            </TouchableOpacity>
          ) : null}
        </View>

        {/* Stop / Cancel Active Button */}
        {assistantState !== "idle" ? (
          <TouchableOpacity onPress={handleStopActive} style={styles.stopButton}>
            <Text style={styles.stopButtonText}>⏹ Stop Active Operation</Text>
          </TouchableOpacity>
        ) : null}
      </ScrollView>

      {/* Quick Text Input Alternative */}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.textInput}
          placeholder="Type a voice command or question..."
          placeholderTextColor={COLORS.textMuted}
          value={textInput}
          onChangeText={setTextInput}
          onSubmitEditing={() => {
            if (textInput.trim()) {
              const cmd = textInput;
              setTextInput("");
              submitCommand(cmd);
            }
          }}
        />
        <TouchableOpacity
          style={styles.sendButton}
          onPress={() => {
            if (textInput.trim()) {
              const cmd = textInput;
              setTextInput("");
              submitCommand(cmd);
            }
          }}
        >
          <Text style={styles.sendButtonText}>Send</Text>
        </TouchableOpacity>
      </View>

      {/* High-Impact Security Confirmation Gate Modal */}
      <ConfirmationModal
        visible={confirmModalVisible}
        title="Security Confirmation"
        description={pendingAction?.description}
        onConfirm={handleAuthorizeAction}
        onCancel={handleCancelAction}
      />
    </KeyboardAvoidingView>
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
    paddingBottom: 10,
    backgroundColor: "rgba(6, 11, 25, 0.95)"
  },
  navButton: {
    alignItems: "center",
    padding: 6
  },
  navIcon: {
    fontSize: 20
  },
  navLabel: {
    fontSize: 10,
    color: COLORS.textSecondary,
    fontWeight: "600",
    marginTop: 2
  },
  scrollContent: {
    alignItems: "center",
    paddingHorizontal: 20,
    paddingBottom: 24
  },
  reactorSection: {
    alignItems: "center",
    marginTop: 16,
    marginBottom: 8
  },
  stateSubtitle: {
    marginTop: 12,
    fontSize: 11,
    letterSpacing: 1.5,
    fontWeight: "700",
    color: COLORS.accentCyan
  },
  transcriptCard: {
    width: "100%",
    backgroundColor: "rgba(255, 255, 255, 0.05)",
    borderRadius: 12,
    padding: 14,
    marginVertical: 8,
    borderLeftWidth: 3,
    borderLeftColor: COLORS.accentAqua
  },
  speakerTag: {
    fontSize: 10,
    fontWeight: "700",
    color: COLORS.accentAqua,
    letterSpacing: 1,
    marginBottom: 4
  },
  transcriptText: {
    fontSize: 15,
    color: COLORS.textPrimary,
    fontStyle: "italic"
  },
  responseCard: {
    width: "100%",
    backgroundColor: COLORS.bgCard,
    borderRadius: 16,
    padding: 18,
    marginVertical: 10,
    borderWidth: 1,
    borderColor: COLORS.borderGlow,
    shadowColor: COLORS.accentCyan,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.25,
    shadowRadius: 10,
    elevation: 6
  },
  responseHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 10
  },
  assistantTag: {
    fontSize: 11,
    fontWeight: "800",
    color: COLORS.accentCyan,
    letterSpacing: 1.2
  },
  toolBadge: {
    backgroundColor: "rgba(0, 242, 254, 0.12)",
    paddingVertical: 3,
    paddingHorizontal: 8,
    borderRadius: 6
  },
  toolBadgeText: {
    fontSize: 11,
    color: COLORS.accentCyan,
    fontWeight: "600"
  },
  responseText: {
    fontSize: 15,
    color: COLORS.textPrimary,
    lineHeight: 22
  },
  replayButton: {
    alignSelf: "flex-start",
    marginTop: 12,
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 8,
    backgroundColor: "rgba(0, 242, 254, 0.15)"
  },
  replayButtonText: {
    fontSize: 12,
    color: COLORS.accentCyan,
    fontWeight: "600"
  },
  stopButton: {
    backgroundColor: "rgba(255, 71, 87, 0.15)",
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 20,
    marginTop: 10,
    borderWidth: 1,
    borderColor: COLORS.danger
  },
  stopButtonText: {
    color: COLORS.danger,
    fontWeight: "700",
    fontSize: 13
  },
  inputContainer: {
    flexDirection: "row",
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: COLORS.bgSecondary,
    borderTopWidth: 1,
    borderTopColor: COLORS.borderSubtle
  },
  textInput: {
    flex: 1,
    height: 44,
    backgroundColor: COLORS.bgCard,
    borderRadius: 10,
    paddingHorizontal: 14,
    color: COLORS.textPrimary,
    fontSize: 14,
    borderWidth: 1,
    borderColor: COLORS.borderSubtle
  },
  sendButton: {
    backgroundColor: COLORS.accentCyan,
    marginLeft: 10,
    paddingHorizontal: 16,
    borderRadius: 10,
    alignItems: "center",
    justifyContent: "center"
  },
  sendButtonText: {
    color: COLORS.bgPrimary,
    fontWeight: "700",
    fontSize: 14
  }
});
