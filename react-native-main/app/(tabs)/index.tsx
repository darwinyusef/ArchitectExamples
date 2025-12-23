import HabitCard from "@/components/HabitCard";
import HabitGreeting from "@/components/HabitGreeting";
import PrimaryButton from "@/components/PrimaryButton";
import ProfileHeader from "@/components/ProfileHeader";
import Screen from "@/components/Screen";
import { ThemedText } from "@/components/themed-text";
import { useCelebration } from "@/context/CelebrationProvider";
import { useHabits } from "@/context/HabitsContext";
import { useThemeColor } from "@/hooks/use-theme-color";
import { getMotivation } from "@/services/motivation";
import { useCallback, useMemo, useState } from "react";
import {
  FlatList,
  ListRenderItemInfo,
  StyleSheet,
  TextInput,
  View,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

type Habit = {
  id: string;
  title: string;
  streak: number;
  isCompleted: boolean;
  priority: "low" | "mid" | "high";
};

const INITIAL: Habit[] = [
  {
    id: "h1",
    title: "Beber agua",
    streak: 3,
    isCompleted: true,
    priority: "mid",
  },
  {
    id: "h2",
    title: "Leer 10 min",
    streak: 1,
    isCompleted: false,
    priority: "low",
  },
  {
    id: "h3",
    title: "Caminar 15 min",
    streak: 7,
    isCompleted: false,
    priority: "high",
  },
];

type HabitItem = ReturnType<typeof useHabits>["habits"][number];

export default function HomeScreen() {
  const { loading, habits, addHabit, toggleHabit } = useHabits();
  const [items, setItems] = useState<Habit[]>(INITIAL);
  const [nuevo, setNuevo] = useState("");
  const insets = useSafeAreaInsets();

  const { celebrate } = useCelebration();

  const border = useThemeColor({}, "border");
  const surface = useThemeColor({}, "surface");
  const text = useThemeColor({}, "text");

  const onAdd = useCallback(() => {
    const title = nuevo.trim();
    if (!title) return;
    addHabit(title, "low");
    setNuevo("");
  }, [nuevo, addHabit]);

  const total = items.length;
  const completados = useMemo(() => {
    const today = new Date().toDateString();
    return habits.filter(
      (h) => h.lastDoneAt && new Date(h.lastDoneAt).toDateString() === today
    ).length;
  }, [habits]);

  async function onToggleWithCelebration(item: HabitItem) {
    const wasToday = item.lastDoneAt
      ? isSameDay(item.lastDoneAt, Date.now())
      : false;
    toggleHabit(item.id);
    if (!wasToday) {
      const msg = await getMotivation("Ana", item.title);
      celebrate(msg);
    }
  }

  const keyExtractor = useCallback((item: Habit) => item.id, []);
  const renderItem = ({ item }: ListRenderItemInfo<HabitItem>) => {
    const isToday = item.lastDoneAt
      ? new Date(item.lastDoneAt).toDateString() === new Date().toDateString()
      : false;
    return (
      <HabitCard
        title={item.title}
        streak={item.streak}
        isCompleted={isToday}
        priority={item.priority}
        onToggle={() => onToggleWithCelebration(item)}
      />
    );
  };

  const ItemSeparator = () => <View style={{ height: 12 }} />;

  const Empty = () => (
    <View style={{ paddingVertical: 32, alignItems: "center", gap: 8 }}>
      <ThemedText>Aún no tienes hábitos. Crea el primero 👇</ThemedText>
    </View>
  );

  if (loading) {
    return (
      <Screen>
        <ThemedText>Cargando tus hábitos…</ThemedText>
      </Screen>
    );
  }

  const isSameDay = (a: string | number | Date, b: string | number | Date) =>
    new Date(a).toDateString() === new Date(b).toDateString();

  return (
    <Screen>
      <ProfileHeader name="Alison Melisa" role="dev" />
      <HabitGreeting nombre="Ada" />
      <View style={[styles.row, { alignItems: "center" }]}>
        {/* <Pressable
          onPress={async () => {
            try {
              await AsyncStorage.clear();
            } catch (e) {
              console.warn(e);
            }
          }}
          style={{ padding: 12, borderRadius: 8, backgroundColor: "black" }}
        >
          <Text style={{ color: "white" }}>Resetear app</Text>
        </Pressable> */}
        <TextInput
          value={nuevo}
          onChangeText={setNuevo}
          placeholder="Nuevo habito (ej Meditar)"
          onSubmitEditing={onAdd}
          style={[
            styles.input,
            { backgroundColor: surface, borderColor: border, color: text },
          ]}
        />
        <PrimaryButton title="Añadir" onPress={onAdd}></PrimaryButton>
      </View>
      <FlatList
        data={habits}
        renderItem={renderItem}
        ItemSeparatorComponent={ItemSeparator}
        ListEmptyComponent={Empty}
        contentContainerStyle={{
          paddingVertical: 16,
          paddingBottom: insets.bottom + 16,
        }}
        initialNumToRender={8}
        windowSize={10}
        showsVerticalScrollIndicator={false}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  titleContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  stepContainer: {
    gap: 8,
    marginBottom: 8,
  },
  reactLogo: {
    height: 178,
    width: 290,
    bottom: 0,
    left: 0,
    position: "absolute",
  },
  container: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#F2F6FF",
    padding: 24,
    gap: 8,
  },
  title: {
    fontSize: 22,
    fontWeight: "700",
    color: "#0F172A",
  },
  subtitle: {
    fontSize: 14,
    color: "#334155",
  },
  row: { flexDirection: "row", gap: 8 },
  input: {
    flex: 1,
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  addBtn: {
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
  },
});
