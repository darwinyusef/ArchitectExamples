# JavaScript Frontend Workshop
## 27 de Diciembre, 2025

Bienvenido al taller de JavaScript Frontend! En este workshop aprenderás los fundamentos de JavaScript para desarrollo web.

---

## 🎯 GUÍA PASO A PASO - CÓMO USAR ESTE WORKSHOP

### ✅ Paso 1: Preparación Inicial
1. **Crea un archivo HTML**: `workshop.html` en tu carpeta de trabajo
2. **Copia esta plantilla básica**:
```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Workshop JavaScript</title>
</head>
<body>
  <h1>Mi Workshop</h1>

  <!-- Aquí vas a agregar tu HTML según la tarea -->

  <script>
    // Aquí vas a escribir tu código JavaScript
  </script>
</body>
</html>
```

### ✅ Paso 2: Iniciar el Goal
- Click en ▶️ (Play button) al lado del goal "DOM Manipulation Basics"
- Esto activará la primera tarea

### ✅ Paso 3: Leer la Tarea
- Mira el panel **"Current Task Instructions"** (derecha abajo)
- Lee **cuidadosamente** la descripción
- Revisa el **ejemplo de código** proporcionado
- Entiende qué se te pide hacer

### ✅ Paso 4: Escribir el Código
**Para la Tarea 1 (ejemplo):**
```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Tarea 1 - Button Click</title>
</head>
<body>
  <h1>Tarea 1: Botón con Evento Click</h1>

  <!-- Agrega el botón con id='myButton' -->
  <button id="myButton">Click Me!</button>

  <script>
    // Escribe tu código aquí
    const btn = document.getElementById('myButton');
    btn.addEventListener('click', () => {
      alert('Hello World!');
    });
  </script>
</body>
</html>
```

### ✅ Paso 5: Ejecutar y Validar
1. **Guarda** tu archivo (`Cmd+S` o `Ctrl+S`)
2. Click en ▶️ (Run button) en el goal
3. **Se abrirá un terminal** ejecutando tu código
4. **ChatGPT validará** automáticamente:
   - ✅ **SI PASA**: Verás "✅ Task completed!" y avanza a la siguiente tarea
   - ❌ **SI FALLA**: Verás feedback con sugerencias específicas

### ✅ Paso 6: Si Falla la Validación
- **Lee el mensaje de error** cuidadosamente
- **Revisa las sugerencias** que te da ChatGPT
- **Corrige tu código**
- **Vuelve a ejecutar** (paso 5)

### ✅ Paso 7: Siguiente Tarea
- Cuando completes una tarea, automáticamente pasa a la siguiente
- El panel "Current Task Instructions" se actualiza
- Repite desde el Paso 3

---

## 📚 Objetivos del Workshop

1. **Manipulación del DOM**: Aprender a interactuar con elementos HTML usando JavaScript
2. **Eventos**: Manejar eventos del usuario (clicks, submit, etc.)
3. **Arrays**: Dominar los métodos de arrays (map, filter, reduce)
4. **Funciones**: Crear funciones reutilizables y eficientes

---

## 🎯 Goal 1: DOM Manipulation Basics

### ¿Qué es el DOM?

El **Document Object Model (DOM)** es una representación en forma de árbol de tu documento HTML. JavaScript puede acceder y modificar este árbol para hacer páginas dinámicas.

### Seleccionar Elementos

```javascript
// Por ID
const elemento = document.getElementById('miId');

// Por clase
const elementos = document.getElementsByClassName('miClase');

// Por selector CSS
const elemento = document.querySelector('.miClase');
const todos = document.querySelectorAll('div.item');
```

### Modificar Contenido

```javascript
elemento.textContent = 'Nuevo texto';
elemento.innerHTML = '<strong>Texto en negrita</strong>';
```

### Event Listeners

```javascript
const boton = document.getElementById('miBoton');

boton.addEventListener('click', function() {
  console.log('¡Click detectado!');
});

// Versión con arrow function
boton.addEventListener('click', () => {
  console.log('¡Click detectado!');
});
```

### Ejemplo Completo: Formulario

```html
<!DOCTYPE html>
<html>
<body>
  <form id="myForm">
    <input type="text" id="nameInput" placeholder="Tu nombre">
    <button type="submit">Enviar</button>
  </form>
  <div id="result"></div>

  <script>
    const form = document.getElementById('myForm');

    form.addEventListener('submit', (e) => {
      e.preventDefault(); // Evita que la página se recargue
      const name = document.getElementById('nameInput').value;
      document.getElementById('result').textContent = `Hola, ${name}!`;
    });
  </script>
</body>
</html>
```

---

## 🎯 Goal 2: JavaScript Arrays and Iteration

### Arrays en JavaScript

Un array es una colección ordenada de elementos.

```javascript
const frutas = ['manzana', 'banana', 'naranja'];
const numeros = [1, 2, 3, 4, 5];
const mixto = [1, 'texto', true, { nombre: 'Juan' }];
```

### Método: map()

**Propósito**: Transforma cada elemento del array.

```javascript
const numeros = [1, 2, 3, 4, 5];
const cuadrados = numeros.map(n => n * n);
// Resultado: [1, 4, 9, 16, 25]

const nombres = ['ana', 'luis', 'pedro'];
const mayusculas = nombres.map(n => n.toUpperCase());
// Resultado: ['ANA', 'LUIS', 'PEDRO']
```

### Método: filter()

**Propósito**: Filtra elementos que cumplan una condición.

```javascript
const edades = [12, 18, 25, 30, 15, 40];
const adultos = edades.filter(edad => edad >= 18);
// Resultado: [18, 25, 30, 40]

const palabras = ['hola', 'adiós', 'si', 'no', 'tal vez'];
const cortas = palabras.filter(p => p.length <= 3);
// Resultado: ['si', 'no']
```

### Método: reduce()

**Propósito**: Reduce el array a un solo valor.

```javascript
const numeros = [1, 2, 3, 4, 5];
const suma = numeros.reduce((acumulador, actual) => {
  return acumulador + actual;
}, 0); // 0 es el valor inicial
// Resultado: 15

// Encontrar el máximo
const max = numeros.reduce((max, n) => n > max ? n : max, 0);
// Resultado: 5
```

### Combinando Métodos

```javascript
const estudiantes = [
  { nombre: 'Ana', edad: 20, nota: 85 },
  { nombre: 'Luis', edad: 22, nota: 92 },
  { nombre: 'Pedro', edad: 19, nota: 78 },
  { nombre: 'María', edad: 21, nota: 95 }
];

// Obtener promedio de notas de estudiantes mayores de 20 años
const promedio = estudiantes
  .filter(e => e.edad > 20)
  .map(e => e.nota)
  .reduce((sum, nota) => sum + nota, 0) /
  estudiantes.filter(e => e.edad > 20).length;

console.log(promedio); // 93.5
```

---

## 💡 Tips y Mejores Prácticas

### 1. Usa const y let, no var

```javascript
// ✅ Bueno
const PI = 3.14159;
let contador = 0;

// ❌ Evitar
var miVariable = 10;
```

### 2. Arrow Functions

```javascript
// Tradicional
function sumar(a, b) {
  return a + b;
}

// Arrow function
const sumar = (a, b) => a + b;

// Con múltiples líneas
const saludar = (nombre) => {
  const mensaje = `Hola, ${nombre}!`;
  return mensaje;
};
```

### 3. Template Literals

```javascript
const nombre = 'Juan';
const edad = 25;

// ✅ Bueno - Template literals
const mensaje = `Mi nombre es ${nombre} y tengo ${edad} años`;

// ❌ Evitar - Concatenación
const mensaje = 'Mi nombre es ' + nombre + ' y tengo ' + edad + ' años';
```

### 4. Destructuring

```javascript
// Arrays
const [primero, segundo] = [1, 2, 3];

// Objetos
const persona = { nombre: 'Ana', edad: 30 };
const { nombre, edad } = persona;
```

---

## 🎥 Recursos Multimedia

### Video Tutorial - JavaScript DOM Manipulation

[youtube](dQw4w9WgXcQ)

### Imagen de Referencia - DOM Tree

![DOM Tree Structure](https://www.w3schools.com/js/pic_htmltree.gif)

### Diagrama de Arrays

![JavaScript Arrays](https://miro.medium.com/max/1400/1*6ahbWjp_g9hXJhFa2j4JCQ.png)

### Documentación Oficial

- [MDN Web Docs - JavaScript](https://developer.mozilla.org/es/docs/Web/JavaScript)
- [MDN - DOM](https://developer.mozilla.org/es/docs/Web/API/Document_Object_Model)
- [MDN - Array Methods](https://developer.mozilla.org/es/docs/Web/JavaScript/Reference/Global_Objects/Array)

### Herramientas

- **Console del navegador**: F12 para abrir las DevTools
- **console.log()**: Tu mejor amigo para debugging
- **debugger;**: Coloca puntos de interrupción en tu código

---

## ✅ Checklist de Aprendizaje

Al completar este workshop, deberías poder:

- [ ] Seleccionar elementos del DOM usando getElementById, querySelector
- [ ] Agregar event listeners a elementos
- [ ] Modificar el contenido de elementos (textContent, innerHTML)
- [ ] Prevenir comportamiento por defecto de formularios (e.preventDefault)
- [ ] Usar map() para transformar arrays
- [ ] Usar filter() para filtrar elementos
- [ ] Usar reduce() para agregar valores
- [ ] Combinar métodos de arrays
- [ ] Escribir código JavaScript limpio y legible

---

## 🚀 ¡Manos a la Obra!

Ahora que tienes la teoría, es momento de practicar. Completa cada tarea paso a paso y valida tu código con el botón de ejecución.

**¡Éxito en tu aprendizaje!** 🎉
