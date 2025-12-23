import { useThemeColor } from "@/hooks/use-theme-color";
import { StyleSheet } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { ThemedView } from "./themed-view";

type Props = { children: React.ReactNode };

export default function Screen({ children }: Props) {
  const bg = useThemeColor({}, "background");
  const insets = useSafeAreaInsets();

  return (
    <ThemedView
      style={[
        styles.screen,
        {
          backgroundColor: bg,
          paddingTop: insets.top,
          paddingBottom: insets.bottom + 16,
          paddingHorizontal: 16,
        },
      ]}
    >
      {children}
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: "#F8FAFC",
    paddingHorizontal: 16,
    paddingVertical: 20,
    gap: 16,
  },
});
