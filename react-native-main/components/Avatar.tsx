import { useThemeColor } from "@/hooks/use-theme-color";
import { Image, Pressable, StyleSheet, Text, View } from "react-native";

function initialsFrom(name: string) {
  const parts = name.trim().split(/\s+/).slice(0, 2);
  return parts.map((p) => p[0]?.toUpperCase() ?? "").join("");
}

type Props = {
  size?: number;
  name: string;
  uri?: string | null;
  onPress?: () => void;
};

export default function Avatar({ size = 72, name, uri, onPress }: Props) {
  const surface = useThemeColor({}, "surface");
  const border = useThemeColor({}, "border");
  const text = useThemeColor({}, "text");

  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="imagebutton"
      accessibilityLabel="Cambiar foto de perfil"
    >
      {uri ? (
        <Image
          source={{ uri }}
          style={{
            width: size,
            height: size,
            borderRadius: size / 2,
            borderWidth: 1,
            borderColor: border,
          }}
        />
      ) : (
        <View
          style={[
            styles.fallback,
            {
              width: size,
              height: size,
              borderRadius: size / 2,
              backgroundColor: surface,
              borderColor: border,
            },
          ]}
        >
          <Text
            style={[styles.initials, { color: text, fontSize: size * 0.34 }]}
          >
            {initialsFrom(name) || "🙂"}
          </Text>
        </View>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  fallback: { alignItems: "center", justifyContent: "center", borderWidth: 1 },
  initials: { fontWeight: "700" },
});
