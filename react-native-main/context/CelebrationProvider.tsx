import { ThemedText } from "@/components/themed-text";
import * as Haptics from "expo-haptics";
import React from "react";
import {
  AccessibilityInfo,
  Animated,
  Easing,
  StyleSheet,
  useWindowDimensions,
  View,
} from "react-native";
import ConfettiCannon from "react-native-confetti-cannon";

type Ctx = { celebrate: (message?: string) => void };
const CelebrationContext = React.createContext<Ctx>({ celebrate: () => {} });
export const useCelebration = () => React.useContext(CelebrationContext);

export function CelebrationProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [visible, setVisible] = React.useState(false);
  const [message, setMessage] = React.useState<string | undefined>();
  const opacity = React.useRef(new Animated.Value(0)).current;
  const lockRef = React.useRef(false);
  const { width } = useWindowDimensions();

  const celebrate = React.useCallback(
    async (msg?: string) => {
      if (lockRef.current) return;
      lockRef.current = true;
      setMessage(msg);
      setVisible(true);

      // feedback háptico + accesibilidad (si falla, ignora)
      try {
        await Haptics.notificationAsync(
          Haptics.NotificationFeedbackType.Success
        );
      } catch {}
      try {
        AccessibilityInfo.announceForAccessibility?.(
          msg || "¡Hábito completado!"
        );
      } catch {}

      // fade‑in
      Animated.timing(opacity, {
        toValue: 1,
        duration: 180,
        easing: Easing.out(Easing.quad),
        useNativeDriver: true,
      }).start();

      // auto‑hide
      setTimeout(() => {
        Animated.timing(opacity, {
          toValue: 0,
          duration: 220,
          easing: Easing.in(Easing.quad),
          useNativeDriver: true,
        }).start(({ finished }) => {
          if (finished) {
            setVisible(false);
            setMessage(undefined);
            lockRef.current = false;
          }
        });
      }, 1400);
    },
    [opacity]
  );

  return (
    <CelebrationContext.Provider value={{ celebrate }}>
      {children}
      {visible && (
        <Animated.View
          pointerEvents="none"
          style={[StyleSheet.absoluteFillObject, styles.overlay, { opacity }]}
        >
          {/* confetti desde esquinas superiores */}
          <ConfettiCannon
            count={60}
            origin={{ x: 0, y: 0 }}
            fadeOut
            autoStart
          />
          <ConfettiCannon
            count={60}
            origin={{ x: width, y: 0 }}
            fadeOut
            autoStart
          />
          {/* toast motivacional */}
          <View style={styles.toast}>
            <ThemedText style={styles.toastText}>
              {message || "¡Hábito completado!"}
            </ThemedText>
          </View>
        </Animated.View>
      )}
    </CelebrationContext.Provider>
  );
}

const styles = StyleSheet.create({
  overlay: { justifyContent: "center", alignItems: "center" },
  toast: {
    position: "absolute",
    bottom: 80,
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 14,
    backgroundColor: "rgba(0,0,0,0.70)",
  },
  toastText: { color: "#fff", fontWeight: "700" },
});
