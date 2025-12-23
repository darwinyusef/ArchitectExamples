import { useThemeColor } from "@/hooks/use-theme-color";
import { Pressable, StyleSheet, ViewStyle } from "react-native";
import { ThemedText } from "./themed-text";

type Props = {
  title: string;
  onPress: () => void;
  disabled?: boolean;
  style?: ViewStyle | ViewStyle[];
};

export default function PrimaryButton({
  title,
  onPress,
  disabled,
  style,
}: Props) {
  const bg = useThemeColor({}, "primary");
  const onBg = useThemeColor({}, "onPrimary");
  const border = useThemeColor({}, "border");

  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={title}
      disabled={disabled}
      onPress={onPress}
      style={({ pressed }) => [
        styles.base,
        { backgroundColor: bg, opacity: disabled ? 0.6 : pressed ? 0.9 : 1 },
        { borderColor: border },
        style as any,
        pressed && { transform: [{ scale: 0.98 }], elevation: 2 },
      ]}
    >
      <ThemedText>{title}</ThemedText>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    minHeight: 44,
    minWidth: 44,
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
  },
  label: { fontWeight: "700" },
});
