import React, { useEffect, useRef } from "react";
import {
  View,
  TouchableOpacity,
  StyleSheet,
  Animated,
  Easing
} from "react-native";
import { COLORS } from "../theme/colors";

export function ArcReactor({ state = "idle", onPress }) {
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const rotateAnim = useRef(new Animated.Value(0)).current;
  const glowAnim = useRef(new Animated.Value(0.4)).current;

  useEffect(() => {
    // Continuous rotation of the outer technological ring
    const rotateLoop = Animated.loop(
      Animated.timing(rotateAnim, {
        toValue: 1,
        duration: state === "processing" ? 3000 : 12000,
        easing: Easing.linear,
        useNativeDriver: true
      })
    );
    rotateLoop.start();

    // Pulse animation based on active state
    let pulseDuration = 2400;
    let minScale = 0.96;
    let maxScale = 1.04;

    if (state === "listening") {
      pulseDuration = 900;
      minScale = 0.92;
      maxScale = 1.12;
    } else if (state === "speaking") {
      pulseDuration = 1200;
      minScale = 0.95;
      maxScale = 1.08;
    } else if (state === "processing") {
      pulseDuration = 700;
      minScale = 0.97;
      maxScale = 1.03;
    }

    const pulseLoop = Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: maxScale,
          duration: pulseDuration / 2,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true
        }),
        Animated.timing(pulseAnim, {
          toValue: minScale,
          duration: pulseDuration / 2,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true
        })
      ])
    );
    pulseLoop.start();

    return () => {
      rotateLoop.stop();
      pulseLoop.stop();
    };
  }, [state]);

  const spin = rotateAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ["0deg", "360deg"]
  });

  const getCoreColor = () => {
    switch (state) {
      case "listening":
        return COLORS.accentAqua;
      case "speaking":
        return COLORS.accentCyan;
      case "processing":
        return COLORS.accentPurple;
      case "offline":
        return COLORS.textMuted;
      default:
        return COLORS.accentCyan;
    }
  };

  return (
    <View style={styles.container}>
      <Animated.View
        style={[
          styles.outerHalo,
          {
            borderColor: getCoreColor(),
            transform: [{ scale: pulseAnim }]
          }
        ]}
      />

      <Animated.View
        style={[
          styles.segmentedRing,
          {
            borderColor: getCoreColor(),
            transform: [{ rotate: spin }]
          }
        ]}
      />

      <TouchableOpacity
        activeOpacity={0.85}
        onPress={onPress}
        style={styles.touchArea}
      >
        <Animated.View
          style={[
            styles.coreCircle,
            {
              backgroundColor: COLORS.bgCard,
              borderColor: getCoreColor(),
              shadowColor: getCoreColor(),
              transform: [{ scale: pulseAnim }]
            }
          ]}
        >
          <View style={[styles.innerCore, { backgroundColor: getCoreColor() }]} />
        </Animated.View>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: 200,
    height: 200,
    alignItems: "center",
    justifyContent: "center"
  },
  touchArea: {
    width: 140,
    height: 140,
    alignItems: "center",
    justifyContent: "center"
  },
  outerHalo: {
    position: "absolute",
    width: 190,
    height: 190,
    borderRadius: 95,
    borderWidth: 1.5,
    opacity: 0.25
  },
  segmentedRing: {
    position: "absolute",
    width: 165,
    height: 165,
    borderRadius: 82.5,
    borderWidth: 2,
    borderStyle: "dashed",
    opacity: 0.6
  },
  coreCircle: {
    width: 130,
    height: 130,
    borderRadius: 65,
    borderWidth: 3,
    alignItems: "center",
    justifyContent: "center",
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.8,
    shadowRadius: 18,
    elevation: 12
  },
  innerCore: {
    width: 50,
    height: 50,
    borderRadius: 25,
    opacity: 0.95
  }
});
