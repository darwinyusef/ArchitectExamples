# Storybook Testing Demo

A comprehensive demonstration of testing strategies in a React + TypeScript project using Storybook, Vitest, and Playwright.

## Table of Contents

- [Overview](#overview)
- [Testing Types Implemented](#testing-types-implemented)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Running Tests](#running-tests)
- [Testing Examples](#testing-examples)
- [CI/CD Pipeline](#cicd-pipeline)
- [Best Practices](#best-practices)

## Overview

This project demonstrates 10 different types of testing in a modern React application:

1. **Unit Testing** - Testing individual components and functions
2. **Interaction Testing** - Simulating user interactions in Storybook
3. **Accessibility Testing** - Ensuring components meet WCAG standards
4. **Visual Testing** - Detecting visual regressions
5. **Snapshot Testing** - Catching unexpected UI changes
6. **Test Coverage** - Measuring code coverage
7. **CI/CD Integration** - Automated testing in GitHub Actions
8. **End-to-End Testing** - Testing complete user workflows
9. **Integration Testing** - Testing component composition
10. **Test Automation** - Automated test execution

## Testing Types Implemented

### 1. Unit Testing with Vitest

Unit tests verify individual components work correctly in isolation.

**Location**: `src/components/**/*.test.tsx`

**Example**:
```typescript
// src/components/Button/Button.test.tsx
it('handles click events', () => {
  const handleClick = vi.fn();
  render(<Button label="Click Me" onClick={handleClick} />);

  const button = screen.getByRole('button');
  fireEvent.click(button);

  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

**Run**:
```bash
npm run test:unit
```

### 2. Interaction Testing in Storybook

Interaction tests simulate user behavior directly in Storybook stories.

**Location**: `src/components/**/*.stories.tsx`

**Example**:
```typescript
// src/components/Button/Button.stories.tsx
export const WithInteractionTest: Story = {
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button');

    await userEvent.click(button);
    await expect(args.onClick).toHaveBeenCalledTimes(1);
  },
};
```

**Run**:
```bash
npm run test:storybook
```

### 3. Accessibility Testing (a11y)

Automated accessibility testing using the a11y addon.

**Configuration**: `.storybook/main.ts`

**Example**:
```typescript
// Stories are automatically tested for accessibility
meta = {
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
};
```

**View**: Run Storybook and check the "Accessibility" tab

### 4. Visual Testing

Visual regression testing using Playwright screenshots.

**Location**: `e2e/**/*.e2e.spec.ts`

**Example**:
```typescript
test('should take screenshot for visual regression', async ({ page }) => {
  await page.goto('/iframe.html?id=components-button--primary');
  await expect(page).toHaveScreenshot('button-primary.png');
});
```

**Run**:
```bash
npm run test:e2e
```

### 5. Snapshot Testing

Snapshot tests catch unexpected changes in component output.

**Location**: `src/components/**/*.test.tsx`

**Example**:
```typescript
it('matches snapshot for primary variant', () => {
  const { container } = render(<Primary />);
  expect(container.firstChild).toMatchSnapshot();
});
```

**Update snapshots**:
```bash
npm run test:unit -- -u
```

### 6. Test Coverage

Measures how much of your code is covered by tests.

**Configuration**: `vite.config.ts`

**Coverage Thresholds**:
- Lines: 80%
- Functions: 80%
- Branches: 80%
- Statements: 80%

**Run**:
```bash
npm run test:coverage
```

**View Report**:
Open `coverage/index.html` in your browser

### 7. CI/CD Integration

Automated testing in GitHub Actions.

**Location**: `.github/workflows/ci.yml`

**Pipeline Jobs**:
- Unit Tests
- Storybook Tests (Interaction + Accessibility)
- Coverage Analysis
- E2E Tests
- Linting
- Storybook Build

**Triggers**: Push to main/develop, Pull Requests

### 8. End-to-End Testing with Playwright

Tests complete user workflows in a real browser.

**Location**: `e2e/**/*.e2e.spec.ts`

**Example**:
```typescript
test('should successfully submit form with valid data', async ({ page }) => {
  await page.goto('/iframe.html?id=components-form--default');

  await page.fill('input[type="email"]', 'user@example.com');
  await page.fill('input[type="password"]', 'securePassword123');
  await page.click('button[type="submit"]');

  await expect(page.locator('[role="alert"]')).not.toBeVisible();
});
```

**Run**:
```bash
npm run test:e2e
npm run test:e2e:ui  # UI mode
npm run test:e2e:debug  # Debug mode
```

### 9. Integration Testing

Tests how components work together.

**Example**:
```typescript
// Form.test.tsx tests integration of inputs, validation, and submission
it('submits form with valid data', async () => {
  render(<Form onSubmit={onSubmitMock} />);

  // Fill multiple fields
  fireEvent.change(emailInput, { target: { value: 'user@example.com' } });
  fireEvent.change(passwordInput, { target: { value: 'password123' } });
  fireEvent.click(submitButton);

  // Verify integration worked
  await waitFor(() => {
    expect(onSubmitMock).toHaveBeenCalledWith({
      email: 'user@example.com',
      password: 'password123',
      rememberMe: false,
    });
  });
});
```

### 10. Test Automation

All tests can be run automatically via npm scripts.

**Available Commands**:
```bash
npm test                # Run all tests in watch mode
npm run test:unit       # Run unit tests only
npm run test:storybook  # Run Storybook interaction tests
npm run test:e2e        # Run E2E tests
npm run test:coverage   # Run tests with coverage
npm run test:all        # Run all test suites sequentially
npm run test:ci         # Run tests in CI mode
```

## Project Structure

```
storybook-testing-demo/
├── .github/
│   └── workflows/
│       └── ci.yml                  # CI/CD pipeline
├── .storybook/
│   ├── main.ts                     # Storybook configuration
│   ├── preview.ts                  # Global story settings
│   └── vitest.setup.ts             # Vitest setup for Storybook
├── e2e/
│   ├── button.e2e.spec.ts          # E2E tests for Button
│   └── form.e2e.spec.ts            # E2E tests for Form
├── src/
│   ├── components/
│   │   ├── Button/
│   │   │   ├── Button.tsx          # Component
│   │   │   ├── Button.css          # Styles
│   │   │   ├── Button.stories.tsx  # Storybook stories + interaction tests
│   │   │   └── Button.test.tsx     # Unit tests
│   │   ├── Card/
│   │   │   ├── Card.tsx
│   │   │   ├── Card.css
│   │   │   ├── Card.stories.tsx
│   │   │   └── Card.test.tsx
│   │   └── Form/
│   │       ├── Form.tsx
│   │       ├── Form.css
│   │       ├── Form.stories.tsx
│   │       └── Form.test.tsx
│   └── test/
│       └── setup.ts                # Vitest test setup
├── playwright.config.ts            # Playwright configuration
├── vite.config.ts                  # Vite + Vitest configuration
└── package.json                    # Scripts and dependencies
```

## Getting Started

### Prerequisites

- Node.js 20+
- npm or yarn

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd storybook-testing-demo

# Install dependencies
npm install

# Install Playwright browsers (for E2E tests)
npx playwright install
```

### Development

```bash
# Run Storybook
npm run storybook

# Run tests in watch mode
npm test

# Run the React app
npm run dev
```

## Running Tests

### Quick Start

```bash
# Run all tests
npm run test:all

# Run specific test suites
npm run test:unit        # Unit tests only
npm run test:storybook   # Storybook interaction tests
npm run test:e2e         # E2E tests with Playwright
npm run test:coverage    # Tests with coverage report
```

### Advanced

```bash
# Run tests with UI
npm run test:ui          # Vitest UI
npm run test:e2e:ui      # Playwright UI

# Debug E2E tests
npm run test:e2e:debug

# Update snapshots
npm run test:unit -- -u

# Run specific test file
npm run test:unit -- Button.test.tsx

# CI mode (no watch, single run)
npm run test:ci
```

## Testing Examples

### Example 1: Button Component

The Button component demonstrates:
- ✅ Unit tests for props and variants
- ✅ Interaction tests for click handling
- ✅ Accessibility tests for keyboard navigation
- ✅ Snapshot tests for visual regression
- ✅ E2E tests in real browser

**Files**:
- `src/components/Button/Button.tsx` - Component implementation
- `src/components/Button/Button.test.tsx` - Unit tests (95 lines, 12 test cases)
- `src/components/Button/Button.stories.tsx` - Stories with interaction tests
- `e2e/button.e2e.spec.ts` - E2E tests (6 test scenarios)

### Example 2: Card Component

The Card component demonstrates:
- ✅ Clickable/non-clickable states
- ✅ Keyboard navigation tests
- ✅ Accessibility attributes (ARIA)
- ✅ Visual regression testing
- ✅ Integration with footer content

**Files**:
- `src/components/Card/Card.tsx` - Component with accessibility features
- `src/components/Card/Card.test.tsx` - Comprehensive unit tests
- `src/components/Card/Card.stories.tsx` - Interactive stories

### Example 3: Form Component

The Form component demonstrates:
- ✅ Complex validation logic testing
- ✅ Form submission workflows
- ✅ Error handling and display
- ✅ Accessibility (aria-invalid, aria-describedby)
- ✅ Keyboard navigation through form fields
- ✅ Disabled state testing
- ✅ Complete E2E user journey

**Files**:
- `src/components/Form/Form.tsx` - Form with validation
- `src/components/Form/Form.test.tsx` - 40+ test assertions
- `src/components/Form/Form.stories.tsx` - 8 interactive stories
- `e2e/form.e2e.spec.ts` - 11 E2E test scenarios

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs:

1. **Unit Tests** - Fast feedback on component logic
2. **Storybook Tests** - Interaction and accessibility validation
3. **Coverage Analysis** - Ensures code coverage thresholds
4. **E2E Tests** - Validates complete user workflows
5. **Linting** - Code quality checks
6. **Build** - Ensures Storybook builds successfully

### Viewing Test Results in CI

- Test results are uploaded as artifacts
- Coverage reports go to Codecov
- Screenshots on failure are preserved
- All jobs must pass for PR approval

## Best Practices

### 1. Test Organization

- Keep tests close to components (`*.test.tsx` next to `*.tsx`)
- Use descriptive test names
- Group related tests with `describe` blocks
- Follow AAA pattern: Arrange, Act, Assert

### 2. Accessibility

- Always include ARIA attributes
- Test keyboard navigation
- Verify focus management
- Check color contrast
- Use semantic HTML

### 3. Interaction Tests

- Test user behavior, not implementation details
- Use `userEvent` over `fireEvent` for realistic interactions
- Test edge cases (disabled states, errors)
- Verify visual feedback

### 4. E2E Tests

- Test critical user journeys
- Use page objects for complex interactions
- Take screenshots for visual regression
- Keep tests independent and isolated
- Mock external dependencies when needed

### 5. Coverage

- Aim for 80%+ coverage
- Focus on critical paths
- Don't test for 100% - focus on value
- Exclude generated files and configs
- Review coverage reports regularly

### 6. Performance

- Run unit tests in parallel
- Use snapshots judiciously
- Mock expensive operations
- Keep E2E tests focused and fast
- Use `beforeEach` for common setup

## Troubleshooting

### Tests Failing Locally

```bash
# Clear test cache
npm run test:unit -- --clearCache

# Update snapshots
npm run test:unit -- -u

# Reinstall Playwright browsers
npx playwright install
```

### Coverage Not Meeting Thresholds

Check `vite.config.ts` coverage settings and exclude non-critical files.

### E2E Tests Timing Out

Increase timeout in `playwright.config.ts` or check if Storybook is running.

## Resources

- [Storybook Documentation](https://storybook.js.org/docs)
- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Library](https://testing-library.com/)
- [Accessibility Guidelines (WCAG)](https://www.w3.org/WAI/WCAG21/quickref/)

## License

MIT

## Contributing

Contributions are welcome! Please ensure all tests pass before submitting a PR.
