import React, { useEffect, useRef } from "react";
import { View, StyleSheet, Animated } from "react-native";
import { COLORS } from "../theme/colors";

const BAR_COUNT = 20;

export function AudioWaveform({ isActive = false, color = COLORS.accentAqua }) {
  const animatedValues = useRef(
    Array.from({ length: BAR_COUNT }, () => new Animated.Value(4))
  ).current;

  useEffect(() => {
    let interval = null;

    if (isActive) {
      interval = setInterval(() => {
        animatedValues.forEach((val, i) => {
          // Dynamic height generation simulating voice frequencies
          const targetHeight = Math.floor(Math.random() * 38) + 6;
          Animated.timing(val, {
            toValue: targetHeight,
            duration: 90,
            useNativeDriver: false
          }).start();
        });
      }, 100);
    } else {
      // Idle wave reset
      animatedValues.forEach((val) => {
        Animated.timing(val, {
          toValue: 4,
          duration: 300,
          useNativeDriver: false
        }).start();
      });
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isActive]);

  return (
    <View style={styles.container}>
      {animatedValues.map((anim, index) => (
        <Animated.View
          key={index}
          style={[
            styles.bar,
            {
              height: anim,
              backgroundColor: color,
              shadowColor: color
            }
          ]}
        />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    height: 48,
    marginVertical: 10
  },
  bar: {
    width: 3.5,
    marginHorizontal: 2.5,
    borderRadius: 2,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.6,
    shadowRadius: 5,
    elevation: 4
  }
});
