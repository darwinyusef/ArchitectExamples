function randomSeed(name: string) {
  return `${name || "Usuario"}-${Date.now().toString(36)}-${Math.random()
    .toString(36)
    .slice(2, 8)}`;
}

function pick<T>(arr: T[]) {
  return arr[Math.floor(Math.random() * arr.length)];
}

const STYLES = [
  "avataaars",
  "lorelei",
  "notionists",
  "adventurer",
  "bottts-neutral",
];

const BGS = ["b6e3f4", "c0aede", "ffd5dc", "d1d4f9", "e2f0cb", "f1e5ff"];

export async function generateAvatarAI(name: string) {
  const style = pick(STYLES);
  const seed = encodeURIComponent(randomSeed(name));
  const bg = pick(BGS);

  const url = `https://api.dicebear.com/9.x/${style}/png?seed=${seed}&radius=50&backgroundColor=${bg}&size=512&v=${Date.now()}`;

  return url;
}
