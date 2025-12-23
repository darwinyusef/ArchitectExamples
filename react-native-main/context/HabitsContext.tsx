import AsyncStorage from "@react-native-async-storage/async-storage";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useReducer,
  useRef,
} from "react";
import { Habit, Priority } from "../types/habit";
import { isSameDay, isYesterday, toISO } from "../utils/date";

// --- Estado y acciones ---
type State = {
  loading: boolean;
  habits: Habit[];
};

type Action =
  | { type: "HYDRATE"; payload: Habit[] }
  | { type: "ADD"; title: string; priority?: Priority }
  | { type: "TOGGLE"; id: string; today: Date };

const STORAGE_KEY = "habits:v1";

const initialState: State = { loading: true, habits: [] };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "HYDRATE":
      return { loading: false, habits: action.payload };
    case "ADD": {
      const now = new Date();
      const newHabit: Habit = {
        id: `h${Date.now()}`,
        title: action.title,
        priority: action.priority ?? "low",
        createdAt: toISO(now),
        lastDoneAt: null,
        streak: 0,
      };
      return { ...state, habits: [newHabit, ...state.habits] };
    }
    case "TOGGLE": {
      const { id, today } = action;
      const todayISO = toISO(today);
      const updated = state.habits.map((h) => {
        if (h.id !== id) return h;

        const last = h.lastDoneAt ? new Date(h.lastDoneAt) : null;
        const yaHechoHoy = last ? isSameDay(today, last) : false;

        // Si estaba marcado HOY → desmarcar: restar 1 (mín 0) y limpiar lastDoneAt
        if (yaHechoHoy) {
          return {
            ...h,
            streak: Math.max(0, h.streak - 1),
            lastDoneAt: null,
          };
        }

        // Si NO estaba marcado hoy → marcar
        let newStreak = 1;
        if (last && isYesterday(today, last)) {
          newStreak = h.streak + 1; // venías de ayer → cadena continúa
        } else {
          newStreak = 1; // reinicia (hoy es el primer día)
        }

        return {
          ...h,
          streak: newStreak,
          lastDoneAt: todayISO,
        };
      });
      return { ...state, habits: updated };
    }
    default:
      return state;
  }
}

type HabitsCtx = {
  loading: boolean;
  habits: Habit[];
  addHabit: (title: string, priority?: Priority) => void;
  toggleHabit: (id: string) => void;
};

const HabitsContext = createContext<HabitsCtx | null>(null);

export function HabitsProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  // Cargar del storage al montar
  useEffect(() => {
    (async () => {
      try {
        const raw = await AsyncStorage.getItem(STORAGE_KEY);
        if (raw) {
          const parsed: Habit[] = JSON.parse(raw);
          dispatch({ type: "HYDRATE", payload: parsed });
        } else {
          dispatch({ type: "HYDRATE", payload: [] });
        }
      } catch (e) {
        console.warn("No se pudo cargar hábitos", e);
        dispatch({ type: "HYDRATE", payload: [] });
      }
    })();
  }, []);

  // Guardar con pequeño debounce cuando cambie la lista (ya no loading)
  const saveTimer = useRef<number | null>(null);
  useEffect(() => {
    if (state.loading) return;
    if (saveTimer.current) clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(async () => {
      try {
        await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(state.habits));
      } catch (e) {
        console.warn("No se pudo guardar hábitos", e);
      }
    }, 250);
    return () => {
      if (saveTimer.current) clearTimeout(saveTimer.current);
    };
  }, [state.habits, state.loading]);

  const addHabit = useCallback((title: string, priority?: Priority) => {
    const clean = title.trim();
    if (!clean) return;
    dispatch({ type: "ADD", title: clean, priority });
  }, []);

  const toggleHabit = useCallback((id: string) => {
    dispatch({ type: "TOGGLE", id, today: new Date() });
  }, []);

  const value = useMemo<HabitsCtx>(
    () => ({
      loading: state.loading,
      habits: state.habits,
      addHabit,
      toggleHabit,
    }),
    [state.loading, state.habits, addHabit, toggleHabit]
  );

  return (
    <HabitsContext.Provider value={value}>{children}</HabitsContext.Provider>
  );
}

export function useHabits() {
  const ctx = useContext(HabitsContext);
  if (!ctx) throw new Error("useHabits debe usarse dentro de HabitsProvider");
  return ctx;
}
