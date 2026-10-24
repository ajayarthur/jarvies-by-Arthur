import React from "react";
import {
  Modal,
  View,
  Text,
  TouchableOpacity,
  StyleSheet
} from "react-native";
import { COLORS } from "../theme/colors";

export function ConfirmationModal({
  visible = false,
  title = "Security Authorization Required",
  description = "This action will affect the host computer.",
  onConfirm,
  onCancel
}) {
  return (
    <Modal
      transparent
      animationType="fade"
      visible={visible}
      onRequestClose={onCancel}
    >
      <View style={styles.overlay}>
        <View style={styles.card}>
          <View style={styles.header}>
            <View style={styles.warningIconBadge}>
              <Text style={styles.warningIconText}>⚠️</Text>
            </View>
            <Text style={styles.title}>{title}</Text>
          </View>

          <Text style={styles.description}>{description}</Text>

          <View style={styles.infoBox}>
            <Text style={styles.infoText}>
              Security Policy Gate: High-impact desktop commands require explicit mobile authorization.
            </Text>
          </View>

          <View style={styles.buttonRow}>
            <TouchableOpacity
              activeOpacity={0.8}
              onPress={onCancel}
              style={[styles.button, styles.cancelButton]}
            >
              <Text style={styles.cancelText}>Cancel</Text>
            </TouchableOpacity>

            <TouchableOpacity
              activeOpacity={0.8}
              onPress={onConfirm}
              style={[styles.button, styles.confirmButton]}
            >
              <Text style={styles.confirmText}>Authorize Action</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: "rgba(4, 7, 15, 0.88)",
    justifyContent: "center",
    alignItems: "center",
    padding: 24
  },
  card: {
    width: "100%",
    maxWidth: 380,
    backgroundColor: COLORS.bgCard,
    borderRadius: 16,
    padding: 22,
    borderWidth: 1.5,
    borderColor: COLORS.danger,
    shadowColor: COLORS.danger,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 16,
    elevation: 20
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 14
  },
  warningIconBadge: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: "rgba(255, 71, 87, 0.2)",
    alignItems: "center",
    justifyContent: "center",
    marginRight: 12
  },
  warningIconText: {
    fontSize: 18
  },
  title: {
    flex: 1,
    fontSize: 16,
    fontWeight: "700",
    color: COLORS.textPrimary,
    letterSpacing: 0.3
  },
  description: {
    fontSize: 14,
    color: COLORS.textSecondary,
    lineHeight: 20,
    marginBottom: 14
  },
  infoBox: {
    backgroundColor: "rgba(0, 242, 254, 0.08)",
    padding: 10,
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: COLORS.accentCyan,
    marginBottom: 20
  },
  infoText: {
    fontSize: 12,
    color: COLORS.accentCyan,
    lineHeight: 16
  },
  buttonRow: {
    flexDirection: "row",
    justifyContent: "space-between"
  },
  button: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: "center",
    justifyContent: "center"
  },
  cancelButton: {
    backgroundColor: "rgba(255, 255, 255, 0.1)",
    marginRight: 10
  },
  cancelText: {
    color: COLORS.textSecondary,
    fontWeight: "600",
    fontSize: 14
  },
  confirmButton: {
    backgroundColor: COLORS.danger,
    marginLeft: 10
  },
  confirmText: {
    color: "#FFFFFF",
    fontWeight: "700",
    fontSize: 14
  }
});
