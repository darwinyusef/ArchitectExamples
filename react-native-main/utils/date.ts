export const startOfDay = (d: Date) => {
  const x = new Date(d);
  x.setHours(0, 0, 0, 0);
  return x;
};

export const isSameDay = (a: Date, b: Date) =>
  startOfDay(a).getTime() === startOfDay(b).getTime();

export const isYesterday = (ref: Date, candidate: Date) => {
  const y = startOfDay(ref);
  y.setDate(y.getDate() - 1);
  return isSameDay(y, candidate);
};

export const toISO = (d: Date) => startOfDay(d).toISOString();
