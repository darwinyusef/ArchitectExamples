import ExploreCard from "@/components/ExploreCard";
import Screen from "@/components/Screen";
import { ThemedText } from "@/components/themed-text";
import { useHabits } from "@/context/HabitsContext";
import { useThemeColor } from "@/hooks/use-theme-color";
import { suggestFor, Suggestion } from "@/services/suggest";
import { useEffect, useState } from "react";
import { Alert, FlatList, StyleSheet, View } from "react-native";

export default function TabTwoScreen() {
  const { addHabit } = useHabits();
  const text = useThemeColor({}, "text");
  const muted = useThemeColor({}, "muted");

  const [energ, setEnerg] = useState<Suggestion[] | null>(null);
  const [focus, setFocus] = useState<Suggestion[] | null>(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const [a, b] = await Promise.all([
          suggestFor("energia"),
          suggestFor("enfoque"),
        ]);
        if (!mounted) return;
        setEnerg(a);
        setFocus(b);
      } catch (e) {
        console.warn("No se pudieron cargar sugerencias", e);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  const onPick = (s: Suggestion) => {
    addHabit(s.title, s.priority);
    Alert.alert("Añadido", `Se creó el hábito: ${s.title}`);
  };

  const renderItem = ({ item }: { item: Suggestion }) => (
    <ExploreCard
      emoji={item.emoji}
      title={item.title}
      subtitle={item.subtitle}
      onPress={() => onPick(item)}
    />
  );

  const keyExtractor = (item: Suggestion) => item.id;

  const Section = ({
    title,
    data,
  }: {
    title: string;
    data: Suggestion[] | null;
  }) => (
    <View style={{ gap: 8 }}>
      <ThemedText style={{ fontWeight: "700", fontSize: 18, color: text }}>
        {title}
      </ThemedText>
      {data ? (
        <FlatList
          data={data}
          keyExtractor={keyExtractor}
          renderItem={renderItem}
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={{ gap: 8, paddingRight: 8 }}
        />
      ) : (
        <View style={{ flexDirection: "row", gap: 8 }}>
          <ExploreCard title="Cargando…" subtitle="…" />
          <ExploreCard title="Cargando…" subtitle="…" />
          <ExploreCard title="Cargando…" subtitle="…" />
        </View>
      )}
    </View>
  );

  return (
    <Screen>
      <View>
        <ThemedText style={{ fontWeight: "700", fontSize: 18 }}>
          Sugerencias rápidas
        </ThemedText>
        <ThemedText>
          Desliza los chips y toca para crear el hábito al instante.
        </ThemedText>
        <Section title="Energia" data={energ}></Section>
        <Section title="Enfoque" data={focus}></Section>
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  headerImage: {
    color: "#808080",
    bottom: -90,
    left: -35,
    position: "absolute",
  },
  titleContainer: {
    flexDirection: "row",
    gap: 8,
  },
});
