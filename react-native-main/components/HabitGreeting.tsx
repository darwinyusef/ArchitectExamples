import { StyleSheet, View } from "react-native";
import { ThemedText } from "./themed-text";

export default function HabitGreeting({ nombre = "Hola" }) {
  const fecha = new Date();
  const h = fecha.getHours();
  const saludo =
    h < 12 ? "Buenos días" : h < 18 ? "Buenas tardes" : "Buenas noches";

  return (
    <View style={styles.container}>
      <ThemedText style={styles.title}>
        {saludo}
        {nombre ? `, ${nombre}` : ""}
      </ThemedText>
      <ThemedText type="link" style={[styles.subtitle]}>
        Hoy es {fecha.toLocaleDateString()} — {fecha.toLocaleTimeString()}
      </ThemedText>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { gap: 4, marginBottom: 16 },
  title: { fontSize: 22, fontWeight: "700" },
  subtitle: { fontSize: 12, color: "#475569" },
});
