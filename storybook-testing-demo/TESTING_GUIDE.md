# Testing Guide - Ejemplos Prácticos

Esta guía proporciona ejemplos concretos de cada tipo de testing implementado en este proyecto.

## Índice

1. [Vitest Addon](#1-vitest-addon)
2. [Interaction Testing](#2-interaction-testing)
3. [Accessibility Testing](#3-accessibility-testing)
4. [Visual Testing](#4-visual-testing)
5. [Snapshot Testing](#5-snapshot-testing)
6. [Test Coverage](#6-test-coverage)
7. [CI/CD Pipeline](#7-cicd-pipeline)
8. [End-to-End Testing](#8-end-to-end-testing)
9. [Unit Testing](#9-unit-testing)
10. [Test Runner](#10-test-runner)

---

## 1. Vitest Addon

**¿Qué es?** El addon de Vitest para Storybook permite ejecutar tests de tus stories directamente.

### Configuración

**Archivo**: `vite.config.ts`

```typescript
import { storybookTest } from '@storybook/addon-vitest/vitest-plugin';

export default defineConfig({
  test: {
    projects: [{
      plugins: [
        storybookTest({
          configDir: path.join(dirname, '.storybook')
        })
      ],
      test: {
        name: 'storybook',
        browser: {
          enabled: true,
          provider: playwright({}),
        },
      }
    }]
  }
});
```

### Ejemplo Práctico

**Archivo**: `src/components/Button/Button.stories.tsx`

```typescript
export const WithInteractionTest: Story = {
  args: {
    variant: 'primary',
    label: 'Click Me',
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button');

    // Test que se ejecuta con Vitest addon
    await expect(button).toBeInTheDocument();
    await userEvent.click(button);
    await expect(args.onClick).toHaveBeenCalledTimes(1);
  },
};
```

### Ejecutar

```bash
npm run test:storybook
```

**Resultado esperado**:
```
✓ src/components/Button/Button.stories.tsx > Button > WithInteractionTest
✓ src/components/Card/Card.stories.tsx > Card > ClickableCardTest
✓ src/components/Form/Form.stories.tsx > Form > SuccessfulSubmission
```

---

## 2. Interaction Testing

**¿Qué es?** Simula interacciones reales del usuario (clicks, typing, keyboard navigation).

### Ejemplo: Test de Click en Button

**Archivo**: `src/components/Button/Button.stories.tsx`

```typescript
export const WithInteractionTest: Story = {
  args: {
    variant: 'primary',
    label: 'Click Me',
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button');

    // Simula click del usuario
    await userEvent.click(button);

    // Verifica que se llamó el callback
    await expect(args.onClick).toHaveBeenCalledTimes(1);
  },
};
```

### Ejemplo: Test de Formulario Complejo

**Archivo**: `src/components/Form/Form.stories.tsx`

```typescript
export const SuccessfulSubmission: Story = {
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);

    // Encuentra los elementos
    const emailInput = canvas.getByLabelText('Email');
    const passwordInput = canvas.getByLabelText('Password');
    const submitButton = canvas.getByRole('button', { name: /sign in/i });

    // Simula usuario llenando el formulario
    await userEvent.type(emailInput, 'user@example.com');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(submitButton);

    // Verifica el resultado
    await waitFor(() =>
      expect(args.onSubmit).toHaveBeenCalledWith({
        email: 'user@example.com',
        password: 'password123',
        rememberMe: false,
      })
    );
  },
};
```

### Ejemplo: Test de Navegación con Teclado

**Archivo**: `src/components/Form/Form.stories.tsx`

```typescript
export const KeyboardNavigation: Story = {
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);

    // Simula navegación con Tab
    await userEvent.tab();
    await expect(canvas.getByLabelText('Email')).toHaveFocus();

    await userEvent.keyboard('user@example.com');
    await userEvent.tab();
    await expect(canvas.getByLabelText('Password')).toHaveFocus();

    await userEvent.keyboard('password123');
    await userEvent.tab();
    await userEvent.tab();

    // Submit con Enter
    await userEvent.keyboard('{Enter}');
    await waitFor(() => expect(args.onSubmit).toHaveBeenCalled());
  },
};
```

### Ver en Acción

1. Ejecuta Storybook: `npm run storybook`
2. Navega a la story
3. Ve a la pestaña "Interactions"
4. Observa cada paso del test ejecutándose

---

## 3. Accessibility Testing

**¿Qué es?** Verifica que los componentes cumplan con estándares de accesibilidad (WCAG).

### Configuración Automática

**Archivo**: `src/components/Button/Button.stories.tsx`

```typescript
const meta = {
  title: 'Components/Button',
  component: Button,
  parameters: {
    a11y: {
      config: {
        rules: [
          { id: 'color-contrast', enabled: true },
          { id: 'button-name', enabled: true },
        ],
      },
    },
  },
} satisfies Meta<typeof Button>;
```

### Ejemplo: Verificación de ARIA Attributes

**Archivo**: `src/components/Form/Form.stories.tsx`

```typescript
export const BlurValidation: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const emailInput = canvas.getByLabelText('Email');
    const submitButton = canvas.getByRole('button');

    // Trigger validation
    emailInput.focus();
    emailInput.blur();

    await waitFor(() => {
      // Verifica que aria-invalid está presente
      expect(emailInput).toHaveAttribute('aria-invalid', 'true');

      // Verifica que aria-describedby apunta al error
      expect(emailInput).toHaveAttribute('aria-describedby', 'email-error');

      // Verifica que el error tiene role="alert"
      const error = canvas.getByText('Email is required');
      expect(error).toHaveAttribute('role', 'alert');
    });
  },
};
```

### Ejemplo: Test de Componente Accesible

**Archivo**: `src/components/Button/Button.tsx`

```typescript
<button
  type="button"
  disabled={disabled}
  onClick={onClick}
  aria-label={ariaLabel || label}  // ✅ ARIA label
  aria-disabled={disabled}          // ✅ Estado disabled
>
  {label}
</button>
```

### Ver Resultados

1. Ejecuta Storybook: `npm run storybook`
2. Abre cualquier story
3. Ve a la pestaña "Accessibility"
4. Revisa violaciones (debería estar en 0)

**Ejemplo de salida**:
```
✓ No accessibility violations found
✓ color-contrast: Passed
✓ button-name: Passed
✓ label: Passed
```

---

## 4. Visual Testing

**¿Qué es?** Detecta cambios visuales no deseados mediante screenshots.

### Ejemplo: Screenshot con Playwright

**Archivo**: `e2e/button.e2e.spec.ts`

```typescript
test('should take screenshot for visual regression', async ({ page }) => {
  await page.goto('/iframe.html?id=components-button--primary');

  // Toma screenshot y lo compara con baseline
  await expect(page).toHaveScreenshot('button-primary.png');
});
```

### Ejemplo: Screenshots de Estados

**Archivo**: `e2e/form.e2e.spec.ts`

```typescript
test('should take screenshot for visual regression', async ({ page }) => {
  await page.goto('/iframe.html?id=components-form--default');

  // Screenshot del estado default
  await expect(page).toHaveScreenshot('form-default.png');

  // Trigger errors
  await page.click('button[type="submit"]');

  // Screenshot con errores visibles
  await expect(page).toHaveScreenshot('form-with-errors.png');
});
```

### Actualizar Baseline

```bash
# Primera vez - crea screenshots base
npm run test:e2e

# Actualizar screenshots después de cambios intencionales
npm run test:e2e -- --update-snapshots
```

### Ver Diferencias

Cuando hay cambios visuales:
```
Expected: button-primary.png
Received: button-primary-actual.png
Diff: button-primary-diff.png
```

---

## 5. Snapshot Testing

**¿Qué es?** Guarda el HTML renderizado y detecta cambios no intencionales.

### Ejemplo Básico

**Archivo**: `src/components/Button/Button.test.tsx`

```typescript
describe('Snapshot Tests', () => {
  it('matches snapshot for primary variant', () => {
    const { container } = render(<Primary />);
    expect(container.firstChild).toMatchSnapshot();
  });

  it('matches snapshot for disabled state', () => {
    const { container } = render(<Disabled />);
    expect(container.firstChild).toMatchSnapshot();
  });
});
```

### Snapshot Generado

**Archivo**: `src/components/Button/__snapshots__/Button.test.tsx.snap`

```
// Vitest Snapshot v1

exports[\`Button Component > Snapshot Tests > matches snapshot for primary variant 1\`] = \`
<button
  aria-disabled="false"
  aria-label="Primary Button"
  class="btn btn--primary btn--medium"
  type="button"
>
  Primary Button
</button>
\`;
```

### Flujo de Trabajo

```bash
# 1. Ejecuta tests - crea snapshots
npm run test:unit

# 2. Cambias el componente
# 3. Test falla mostrando diff

# 4. Si el cambio es intencional, actualiza
npm run test:unit -- -u

# 5. Revisa los cambios en git
git diff src/components/**/__snapshots__
```

### Ejemplo de Diff

```diff
- <button class="btn btn--primary">
+ <button class="btn btn--primary btn--large">
```

---

## 6. Test Coverage

**¿Qué es?** Mide qué porcentaje del código está cubierto por tests.

### Configuración

**Archivo**: `vite.config.ts`

```typescript
coverage: {
  provider: 'v8',
  reporter: ['text', 'json', 'html', 'lcov'],
  exclude: [
    'node_modules/',
    '**/*.stories.tsx',
    '**/*.config.*',
  ],
  thresholds: {
    lines: 80,
    functions: 80,
    branches: 80,
    statements: 80,
  },
},
```

### Ejecutar

```bash
npm run test:coverage
```

### Ejemplo de Salida

```
 % Coverage report from v8
--------------------|---------|----------|---------|---------|
File                | % Stmts | % Branch | % Funcs | % Lines |
--------------------|---------|----------|---------|---------|
All files           |   85.23 |    82.14 |   87.50 |   85.67 |
 Button             |   92.30 |    88.88 |   91.66 |   92.30 |
  Button.tsx        |   92.30 |    88.88 |   91.66 |   92.30 |
 Card               |   85.71 |    80.00 |   85.71 |   85.71 |
  Card.tsx          |   85.71 |    80.00 |   85.71 |   85.71 |
 Form               |   81.25 |    78.26 |   83.33 |   81.25 |
  Form.tsx          |   81.25 |    78.26 |   83.33 |   81.25 |
--------------------|---------|----------|---------|---------|
```

### Ver Reporte HTML

```bash
npm run test:coverage
open coverage/index.html
```

El reporte HTML muestra:
- ✅ Líneas cubiertas en verde
- ❌ Líneas no cubiertas en rojo
- ⚠️ Branches no cubiertos en amarillo

---

## 7. CI/CD Pipeline

**¿Qué es?** Ejecuta todos los tests automáticamente en cada commit/PR.

### Pipeline Completo

**Archivo**: `.github/workflows/ci.yml`

```yaml
name: CI Testing Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  # Job 1: Unit Tests
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run test:unit -- --run

  # Job 2: Storybook Tests
  storybook-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: npm run test:storybook -- --run

  # Job 3: Coverage
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run test:coverage
      - uses: codecov/codecov-action@v5

  # Job 4: E2E Tests
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run test:e2e
```

### Ver Resultados en GitHub

1. Ve a la pestaña "Actions" en tu repo
2. Selecciona un workflow run
3. Ve los resultados de cada job
4. Descarga artifacts (coverage, screenshots)

### Ejemplo de Salida Exitosa

```
✓ unit-tests (2m 15s)
✓ storybook-tests (3m 42s)
✓ coverage (2m 31s)
✓ e2e-tests (4m 18s)
✓ lint (1m 5s)
✓ build-storybook (2m 48s)
```

---

## 8. End-to-End Testing

**¿Qué es?** Prueba flujos completos de usuario en un navegador real.

### Ejemplo: Flujo de Login

**Archivo**: `e2e/form.e2e.spec.ts`

```typescript
test('should successfully submit form with valid data', async ({ page }) => {
  // 1. Navega a la página
  await page.goto('/iframe.html?id=components-form--default');

  // 2. Usuario llena el formulario
  await page.fill('input[type="email"]', 'user@example.com');
  await page.fill('input[type="password"]', 'securePassword123');
  await page.check('input[type="checkbox"]');

  // 3. Usuario hace submit
  await page.click('button[type="submit"]');

  // 4. Verifica que no hay errores
  await expect(page.locator('[role="alert"]')).not.toBeVisible();
});
```

### Ejemplo: Test de Validación

**Archivo**: `e2e/form.e2e.spec.ts`

```typescript
test('should show validation errors on invalid submission', async ({ page }) => {
  await page.goto('/iframe.html?id=components-form--default');

  // Submit formulario vacío
  await page.click('button[type="submit"]');

  // Verifica que aparecen los errores
  await expect(page.locator('text=Email is required')).toBeVisible();
  await expect(page.locator('text=Password is required')).toBeVisible();

  // Completa el email con formato inválido
  await page.fill('input[type="email"]', 'invalid-email');
  await page.click('button[type="submit"]');

  // Verifica error de validación
  await expect(
    page.locator('text=Please enter a valid email')
  ).toBeVisible();
});
```

### Ejemplo: Test Multi-Browser

**Archivo**: `playwright.config.ts`

```typescript
projects: [
  {
    name: 'chromium',
    use: { ...devices['Desktop Chrome'] },
  },
  {
    name: 'firefox',
    use: { ...devices['Desktop Firefox'] },
  },
  {
    name: 'webkit',
    use: { ...devices['Desktop Safari'] },
  },
],
```

### Ejecutar

```bash
# Todos los browsers
npm run test:e2e

# Un browser específico
npm run test:e2e -- --project=chromium

# Con UI para debugging
npm run test:e2e:ui

# Modo debug
npm run test:e2e:debug
```

---

## 9. Unit Testing

**¿Qué es?** Prueba funciones y componentes individuales de forma aislada.

### Ejemplo: Test de Props

**Archivo**: `src/components/Button/Button.test.tsx`

```typescript
describe('Unit Tests', () => {
  it('renders with correct label', () => {
    render(<Button label="Test Button" />);
    expect(screen.getByRole('button')).toHaveTextContent('Test Button');
  });

  it('handles click events', () => {
    const handleClick = vi.fn();
    render(<Button label="Click Me" onClick={handleClick} />);

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('renders with correct variant class', () => {
    render(<Button label="Primary" variant="primary" />);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('btn--primary');
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button label="Disabled" disabled={true} />);
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });
});
```

### Ejemplo: Test de Validación

**Archivo**: `src/components/Form/Form.test.tsx`

```typescript
describe('Validation Tests', () => {
  it('shows email required error when submitted empty', async () => {
    render(<Form onSubmit={onSubmitMock} />);

    const submitButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Email is required')).toBeInTheDocument();
    });
    expect(onSubmitMock).not.toHaveBeenCalled();
  });

  it('shows invalid email error', async () => {
    render(<Form onSubmit={onSubmitMock} />);

    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText('Please enter a valid email')
      ).toBeInTheDocument();
    });
  });
});
```

### Ejemplo: Test con Mocks

```typescript
import { vi } from 'vitest';

it('calls onClick handler when clicked', () => {
  const handleClick = vi.fn();
  render(<Button label="Click" onClick={handleClick} />);

  fireEvent.click(screen.getByRole('button'));

  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

---

## 10. Test Runner

**¿Qué es?** Automatiza la ejecución de todos los tests.

### Scripts Disponibles

```json
{
  "scripts": {
    "test": "vitest",
    "test:unit": "vitest --project=unit",
    "test:storybook": "vitest --project=storybook",
    "test:e2e": "playwright test",
    "test:coverage": "vitest run --coverage",
    "test:all": "npm run test:unit && npm run test:storybook && npm run test:e2e",
    "test:ci": "vitest run --coverage && playwright test"
  }
}
```

### Modo Watch (Desarrollo)

```bash
# Auto-ejecuta tests cuando cambias archivos
npm test

# Solo unit tests en watch
npm run test:unit
```

**Salida**:
```
 DEV  v4.0.16

 ✓ src/components/Button/Button.test.tsx (12 tests) 125ms
 ✓ src/components/Card/Card.test.tsx (15 tests) 156ms
 ✓ src/components/Form/Form.test.tsx (18 tests) 234ms

 Test Files  3 passed (3)
      Tests  45 passed (45)
   Start at  14:32:15
   Duration  1.23s (transform 48ms, setup 0ms, collect 892ms, tests 515ms)

 PASS  Waiting for file changes...
```

### Modo CI (Una sola ejecución)

```bash
# Ejecuta todos los tests una vez
npm run test:ci
```

### Test Runner con UI

```bash
# Vitest UI - interfaz gráfica para unit tests
npm run test:ui

# Playwright UI - interfaz gráfica para E2E
npm run test:e2e:ui
```

### Filtrar Tests

```bash
# Run solo tests de Button
npm run test:unit -- Button

# Run solo un test específico
npm run test:unit -- -t "handles click events"

# Run tests que matchean un patrón
npm run test:unit -- --grep "validation"
```

### Ejecutar Tests en Paralelo

```bash
# Vitest ejecuta en paralelo por default
npm run test:unit

# Playwright - especifica workers
npm run test:e2e -- --workers=4
```

---

## Resumen de Comandos

```bash
# 🚀 Quick Start
npm run storybook              # Ver componentes y accessibility
npm test                       # Unit tests en watch mode
npm run test:coverage          # Ver coverage
npm run test:e2e:ui           # E2E tests con UI

# 📊 Test Suites
npm run test:unit             # Unit + Integration tests
npm run test:storybook        # Interaction tests en Storybook
npm run test:e2e              # End-to-end tests
npm run test:all              # Todos los tests secuencialmente

# 🔍 Coverage y Reporting
npm run test:coverage         # Coverage report
open coverage/index.html      # Ver reporte HTML

# 🐛 Debugging
npm run test:ui               # Vitest UI
npm run test:e2e:ui          # Playwright UI
npm run test:e2e:debug       # Debug mode

# 📸 Snapshots
npm run test:unit -- -u       # Update snapshots
npm run test:e2e -- --update-snapshots  # Update visual snapshots

# 🔄 CI/CD
npm run test:ci               # Modo CI (una ejecución)
```

---

## Mejores Prácticas

### ✅ DO

- Escribe tests antes o junto con el código
- Usa nombres descriptivos para tests
- Mantén tests simples y enfocados
- Verifica comportamiento, no implementación
- Usa mocks para dependencias externas
- Ejecuta tests frecuentemente

### ❌ DON'T

- No testees detalles de implementación
- No copies código del componente al test
- No hagas tests demasiado complejos
- No ignores tests que fallan
- No confíes solo en snapshots
- No omitas tests de accesibilidad

---

## Debugging Tips

### Test Falla pero no Sabes Por Qué

```typescript
import { screen } from '@testing-library/react';

// Imprime el DOM actual
screen.debug();

// Imprime un elemento específico
screen.debug(screen.getByRole('button'));
```

### Ver Estado del Componente

```typescript
const { container } = render(<Button label="Test" />);
console.log(container.innerHTML);
```

### Pausar Ejecución

```typescript
import { pause } from '@storybook/test';

play: async ({ canvasElement }) => {
  await pause();  // Pausa aquí para inspeccionar
  // ...resto del test
}
```

---

¡Feliz Testing! 🎉
