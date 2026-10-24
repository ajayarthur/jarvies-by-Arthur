import React, { useState } from "react";
import { StatusBar } from "expo-status-bar";
import { SafeAreaView, StyleSheet } from "react-native";
import { COLORS } from "./src/theme/colors";
import { MainAssistantScreen } from "./src/screens/MainAssistantScreen";
import { SettingsScreen } from "./src/screens/SettingsScreen";
import { CapabilitiesScreen } from "./src/screens/CapabilitiesScreen";

export default function App() {
  const [currentScreen, setCurrentScreen] = useState("main"); // main, settings, capabilities

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" backgroundColor={COLORS.bgPrimary} />

      {currentScreen === "main" && (
        <MainAssistantScreen
          onNavigateSettings={() => setCurrentScreen("settings")}
          onNavigateCapabilities={() => setCurrentScreen("capabilities")}
        />
      )}

      {currentScreen === "settings" && (
        <SettingsScreen onBack={() => setCurrentScreen("main")} />
      )}

      {currentScreen === "capabilities" && (
        <CapabilitiesScreen onBack={() => setCurrentScreen("main")} />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.bgPrimary
  }
});
