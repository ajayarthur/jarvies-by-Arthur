import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { COLORS } from "../theme/colors";

export function ConnectionBadge({ status = "connecting", hostname = "PC", onPress }) {
  const getStatusColor = () => {
    switch (status) {
      case "online":
        return COLORS.statusOnline;
      case "offline":
        return COLORS.statusOffline;
      default:
        return COLORS.statusConnecting;
    }
  };

  const getStatusLabel = () => {
    switch (status) {
      case "online":
        return `Companion Online (${hostname})`;
      case "offline":
        return "Companion Offline (Tap to Reconnect)";
      default:
        return "Connecting to Companion...";
    }
  };

  return (
    <TouchableOpacity activeOpacity={0.7} onPress={onPress} style={styles.badge}>
      <View style={[styles.dot, { backgroundColor: getStatusColor() }]} />
      <Text style={[styles.text, { color: getStatusColor() }]}>{getStatusLabel()}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "rgba(13, 21, 39, 0.85)",
    paddingVertical: 6,
    paddingHorizontal: 14,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "rgba(0, 242, 254, 0.2)",
    alignSelf: "center",
    marginTop: 8
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8
  },
  text: {
    fontSize: 12,
    fontWeight: "600",
    letterSpacing: 0.4
  }
});
