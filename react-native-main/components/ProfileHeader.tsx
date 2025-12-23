import { useThemeColor } from "@/hooks/use-theme-color";
import { StyleSheet, View } from "react-native/";
import { ThemedText } from "./themed-text";

export default function ProfileHeader({
  name,
  role,
}: {
  name: string;
  role: string;
}) {
  const card = useThemeColor({}, "surface");
  const primary = useThemeColor({}, "primary");
  const onPrimary = useThemeColor({}, "onPrimary");
  const initials = name
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <View style={[styles.card, { backgroundColor: card }]}>
      <View style={[styles.avatar, { backgroundColor: primary }]}>
        <ThemedText style={styles.avatarTxt}>{initials}</ThemedText>
      </View>
      <View style={{ gap: 4 }}>
        <ThemedText style={styles.name}>{name}</ThemedText>
        <ThemedText style={styles.role}>{role}</ThemedText>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    alignItems: "center",
    padding: 16,
    borderRadius: 14,
    gap: 12,
  },
  avatar: {
    width: 56,
    height: 56,
    borderRadius: 28,
    alignItems: "center",
    justifyContent: "center",
  },
  avatarTxt: { fontWeight: "700", fontSize: 18, color: "#fff" },
  name: { fontSize: 18, fontWeight: "700" },
  role: { fontSize: 12 },
});
