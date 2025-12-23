import { useThemeColor } from "@/hooks/use-theme-color";
import { Pressable, ScrollView, StyleSheet } from "react-native";
import { ThemedText } from "./themed-text";

const SUGERIDOS = [
  "Beber agua",
  "Leer 10 min",
  "Caminar 15 min",
  "Respirar 1 min",
  "Estiramientos",
];

export default function QuickAddChips({
  onPick,
}: {
  onPick: (title: string) => void;
}) {
  const surface = useThemeColor({}, "surface");
  const border = useThemeColor({}, "border");
  const text = useThemeColor({}, "text");
  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={{ paddingHorizontal: 4, gap: 8 }}
    >
      {SUGERIDOS.map((t) => (
        <Pressable
          key={t}
          onPress={() => onPick(t)}
          style={({ pressed }) => [
            styles.chip,
            {
              backgroundColor: surface,
              borderColor: border,
              opacity: pressed ? 0.9 : 1,
            },
          ]}
          android_ripple={{ color: border }}
        >
          <ThemedText>{t}</ThemedText>
        </Pressable>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  chip: {
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderWidth: 1,
  },
});
