import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  ActivityIndicator
} from "react-native";
import { COLORS } from "../theme/colors";
import { JarvisApi } from "../services/api";

export function CapabilitiesScreen({ onBack }) {
  const [capabilities, setCapabilities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("all"); // all, companion_pc, mobile_device

  useEffect(() => {
    fetchCapabilities();
  }, []);

  const fetchCapabilities = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await JarvisApi.getCapabilities();
      if (data.success && data.capabilities) {
        setCapabilities(data.capabilities);
      } else {
        setError("Unable to load tools registry from companion.");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredData = capabilities.filter((item) => {
    if (filter === "all") return true;
    return item.location === filter;
  });

  const renderItem = ({ item }) => {
    const isHighImpact = item.safety === "high_impact";
    const isMobile = item.location === "mobile_device";

    return (
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Text style={styles.toolName}>{item.name}</Text>
          <View style={styles.badgeRow}>
            <View
              style={[
                styles.badge,
                { backgroundColor: isMobile ? "rgba(0, 255, 210, 0.15)" : "rgba(0, 242, 254, 0.15)" }
              ]}
            >
              <Text
                style={[
                  styles.badgeText,
                  { color: isMobile ? COLORS.accentAqua : COLORS.accentCyan }
                ]}
              >
                {isMobile ? "📱 Phone Native" : "💻 Companion PC"}
              </Text>
            </View>

            {isHighImpact ? (
              <View style={[styles.badge, styles.dangerBadge]}>
                <Text style={styles.dangerBadgeText}>⚠️ High Impact</Text>
              </View>
            ) : null}
          </View>
        </View>

        <Text style={styles.category}>{item.category}</Text>
        <Text style={styles.description}>{item.description}</Text>
      </View>
    );
  };

  return (
    <View style={styles.screen}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <Text style={styles.backText}>← Back to HUD</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Jarvis Capabilities</Text>
        <TouchableOpacity onPress={fetchCapabilities} style={styles.refreshButton}>
          <Text style={styles.refreshText}>🔄</Text>
        </TouchableOpacity>
      </View>

      {/* Filter Tabs */}
      <View style={styles.tabRow}>
        <TouchableOpacity
          onPress={() => setFilter("all")}
          style={[styles.tab, filter === "all" && styles.activeTab]}
        >
          <Text style={[styles.tabText, filter === "all" && styles.activeTabText]}>
            All ({capabilities.length})
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => setFilter("companion_pc")}
          style={[styles.tab, filter === "companion_pc" && styles.activeTab]}
        >
          <Text style={[styles.tabText, filter === "companion_pc" && styles.activeTabText]}>
            PC Tools
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => setFilter("mobile_device")}
          style={[styles.tab, filter === "mobile_device" && styles.activeTab]}
        >
          <Text style={[styles.tabText, filter === "mobile_device" && styles.activeTabText]}>
            Mobile Native
          </Text>
        </TouchableOpacity>
      </View>

      {/* Content */}
      {loading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator color={COLORS.accentCyan} size="large" />
          <Text style={styles.loadingText}>Fetching companion capability registry...</Text>
        </View>
      ) : error ? (
        <View style={styles.centerContainer}>
          <Text style={styles.errorText}>⚠️ {error}</Text>
          <TouchableOpacity onPress={fetchCapabilities} style={styles.retryButton}>
            <Text style={styles.retryButtonText}>Retry</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={filteredData}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
        />
      )}
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
  refreshButton: {
    padding: 6
  },
  refreshText: {
    fontSize: 16
  },
  tabRow: {
    flexDirection: "row",
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.borderSubtle
  },
  tab: {
    paddingVertical: 6,
    paddingHorizontal: 14,
    borderRadius: 20,
    marginRight: 8,
    backgroundColor: "rgba(255, 255, 255, 0.05)"
  },
  activeTab: {
    backgroundColor: "rgba(0, 242, 254, 0.2)",
    borderWidth: 1,
    borderColor: COLORS.accentCyan
  },
  tabText: {
    fontSize: 12,
    fontWeight: "600",
    color: COLORS.textSecondary
  },
  activeTabText: {
    color: COLORS.accentCyan
  },
  listContent: {
    padding: 16,
    paddingBottom: 30
  },
  card: {
    backgroundColor: COLORS.bgCard,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: COLORS.borderSubtle
  },
  cardHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 4
  },
  toolName: {
    fontSize: 15,
    fontWeight: "700",
    color: COLORS.textPrimary,
    flex: 1
  },
  badgeRow: {
    flexDirection: "row"
  },
  badge: {
    paddingVertical: 3,
    paddingHorizontal: 8,
    borderRadius: 6,
    marginLeft: 6
  },
  badgeText: {
    fontSize: 10,
    fontWeight: "700"
  },
  dangerBadge: {
    backgroundColor: "rgba(255, 71, 87, 0.2)"
  },
  dangerBadgeText: {
    color: COLORS.danger,
    fontSize: 10,
    fontWeight: "700"
  },
  category: {
    fontSize: 11,
    fontWeight: "600",
    color: COLORS.accentCyan,
    letterSpacing: 0.8,
    marginBottom: 6
  },
  description: {
    fontSize: 13,
    color: COLORS.textSecondary,
    lineHeight: 18
  },
  centerContainer: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    padding: 30
  },
  loadingText: {
    marginTop: 14,
    color: COLORS.textSecondary,
    fontSize: 13
  },
  errorText: {
    color: COLORS.danger,
    fontSize: 14,
    textAlign: "center",
    marginBottom: 14
  },
  retryButton: {
    backgroundColor: "rgba(0, 242, 254, 0.15)",
    paddingVertical: 8,
    paddingHorizontal: 20,
    borderRadius: 8
  },
  retryButtonText: {
    color: COLORS.accentCyan,
    fontWeight: "700"
  }
});
