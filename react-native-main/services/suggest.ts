export type Suggestion = {
  id: string;
  title: string;
  subtitle?: string;
  emoji?: string;
  priority: "low" | "mid" | "high";
};

const CATALOG: Record<string, Omit<Suggestion, "id">> = {
  // Energía
  "energia-agua": {
    title: "Beber agua",
    subtitle: "250ml ahora",
    emoji: "💧",
    priority: "low",
  },
  "energia-caminar": {
    title: "Caminar 10 min",
    subtitle: "aire fresco",
    emoji: "🚶‍♀️",
    priority: "mid",
  },
  "energia-respirar": {
    title: "Respirar 1 min",
    subtitle: "técnica 4-7-8",
    emoji: "🌬️",
    priority: "low",
  },
  // Enfoque
  "enfoque-lectura": {
    title: "Leer 10 min",
    subtitle: "tema relevante",
    emoji: "📚",
    priority: "low",
  },
  "enfoque-pomodoro": {
    title: "Pomodoro 25",
    subtitle: "1 bloque profundo",
    emoji: "⏱️",
    priority: "mid",
  },
  "enfoque-notifs": {
    title: "Silencio 1 hora",
    subtitle: "sin notifs",
    emoji: "🔕",
    priority: "mid",
  },
};

export type CategoryKey = "energia" | "enfoque";

export async function suggestFor(category: CategoryKey) {
  await new Promise((r) => setTimeout(r, 400));
  const keys = Object.keys(CATALOG).filter((k) => k.startsWith(category));
  return keys.map((k, i) => ({ id: `${k}-${i}`, ...CATALOG[k] }));
}

export async function suggestViaAI(
  category: CategoryKey,
  context: { habitsCount: number; profileName?: string }
) {
  const endpoint = process.env.EXPO_PUBLIC_AI_SUGGEST_ENDPOINT;
  if (!endpoint) return suggestFor(category);
  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category, context }),
    });
    if (!res.ok) throw new Error("AI endpoint error");
    return (await res.json()) as Suggestion[];
  } catch (e) {
    console.warn("AI fallback:", e);
    return suggestFor(category);
  }
}
