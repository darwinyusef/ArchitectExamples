export type Priority = "low" | "mid" | "high";

export type Habit = {
  id: string;
  title: string;
  priority: Priority;
  createdAt: string; // ISO (día)
  lastDoneAt: string | null; // ISO (día) si se completó hoy (o la última vez)
  streak: number; // días consecutivos
};
