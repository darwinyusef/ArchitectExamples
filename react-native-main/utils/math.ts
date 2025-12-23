export const sumar = (a: number, b: number) => a + b;

export const dobleDe = (n: number) => n * 2;

export function ejemploDestructuracionUsuario() {
  const usuario = { nombre: "Ana", edad: 30 };
  const { nombre, edad } = usuario; // desestructuración de objeto
  return `${nombre} tiene ${edad}`;
}
