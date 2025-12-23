# Quick Start Guide

Guía rápida para empezar a usar este proyecto de testing con Storybook.

## Instalación

```bash
npm install
npx playwright install
```

## Comandos Esenciales

### Ver Componentes en Storybook

```bash
npm run storybook
```

Abre http://localhost:6006 y explora:
- 📚 Componentes (Button, Card, Form)
- ♿ Pestaña "Accessibility" para tests a11y
- 🎭 Pestaña "Interactions" para ver tests ejecutándose

### Ejecutar Tests

```bash
# Tests unitarios (rápidos)
npm run test:unit

# Tests de interacción en Storybook
npm run test:storybook

# Tests E2E con Playwright
npm run test:e2e

# Coverage completo
npm run test:coverage
```

## Probar Cada Tipo de Testing

### 1. Unit Testing ✅

```bash
npm run test:unit -- Button.test
```

**Ver**: `src/components/Button/Button.test.tsx`

### 2. Interaction Testing 🎭

```bash
npm run storybook
# Navega a Button > WithInteractionTest
# Ve a la pestaña "Interactions"
```

**Ver**: `src/components/Button/Button.stories.tsx` líneas 92-105

### 3. Accessibility Testing ♿

```bash
npm run storybook
# Abre cualquier story
# Ve a la pestaña "Accessibility"
# Debería mostrar 0 violaciones
```

### 4. Visual Testing 📸

```bash
npm run test:e2e
# Verifica screenshots en test-results/
```

**Ver**: `e2e/button.e2e.spec.ts` línea 52

### 5. Snapshot Testing 📷

```bash
npm run test:unit
# Snapshots están en __snapshots__/
```

**Ver**: `src/components/Button/Button.test.tsx` líneas 70-79

### 6. Test Coverage 📊

```bash
npm run test:coverage
open coverage/index.html
```

Verás reporte con líneas cubiertas/no cubiertas.

### 7. E2E Testing 🌐

```bash
npm run test:e2e:ui
# Se abre interfaz gráfica
# Ejecuta tests en diferentes browsers
```

**Ver**: `e2e/form.e2e.spec.ts`

### 8. CI/CD Testing 🔄

El archivo `.github/workflows/ci.yml` ejecuta todos los tests automáticamente.

### 9. Test Runner 🏃

```bash
# Modo watch (recomendado para desarrollo)
npm test

# Con UI
npm run test:ui
```

### 10. Vitest Addon 🔧

Ya configurado! Los tests de stories se ejecutan con:

```bash
npm run test:storybook
```

## Estructura del Proyecto

```
src/components/
├── Button/
│   ├── Button.tsx           ← Componente
│   ├── Button.test.tsx      ← Unit tests
│   └── Button.stories.tsx   ← Storybook + Interaction tests
├── Card/
│   └── ... (misma estructura)
└── Form/
    └── ... (misma estructura)

e2e/
├── button.e2e.spec.ts       ← E2E tests
└── form.e2e.spec.ts         ← E2E tests
```

## Ejemplos de Código

### Crear un Unit Test

```typescript
// src/components/MyComponent/MyComponent.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MyComponent } from './MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent label="Test" />);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });
});
```

### Crear un Interaction Test

```typescript
// src/components/MyComponent/MyComponent.stories.tsx
export const WithTest: Story = {
  args: { label: 'Click Me' },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button');
    await userEvent.click(button);
    await expect(button).toHaveTextContent('Clicked!');
  },
};
```

### Crear un E2E Test

```typescript
// e2e/mycomponent.e2e.spec.ts
import { test, expect } from '@playwright/test';

test('user can interact with component', async ({ page }) => {
  await page.goto('/iframe.html?id=components-mycomponent--default');
  await page.click('button');
  await expect(page.locator('.result')).toBeVisible();
});
```

## Tips de Desarrollo

### Modo Watch para Unit Tests

```bash
npm test
# Auto-rerun cuando cambias archivos
```

### Debug E2E Tests

```bash
npm run test:e2e:debug
# Pausa en cada paso, inspecciona en browser
```

### Ver Coverage de un Componente Específico

```bash
npm run test:coverage -- Button
```

### Actualizar Snapshots

```bash
npm run test:unit -- -u
```

### Ver Playwright Trace

```bash
npx playwright show-report
```

## Troubleshooting

### Tests de Storybook Fallan

```bash
# Reinstala Playwright browsers
npx playwright install chromium
```

### Coverage Muy Bajo

Revisa qué archivos no están cubiertos:
```bash
npm run test:coverage
# Ve el reporte en coverage/index.html
```

### E2E Tests Timeout

Aumenta timeout en `playwright.config.ts`:
```typescript
timeout: 60000, // 60 segundos
```

## Recursos

- 📖 [README.md](./README.md) - Documentación completa
- 📝 [TESTING_GUIDE.md](./TESTING_GUIDE.md) - Guía detallada de testing
- 🌐 [Storybook Docs](https://storybook.js.org/docs)
- ⚡ [Vitest Docs](https://vitest.dev/)
- 🎭 [Playwright Docs](https://playwright.dev/)

## Siguientes Pasos

1. ✅ Explora los componentes en Storybook
2. ✅ Ejecuta los tests existentes
3. ✅ Modifica un componente y ve cómo fallan los tests
4. ✅ Crea tu propio componente con tests
5. ✅ Configura el CI/CD en tu repo

¡Listo para testear! 🚀
