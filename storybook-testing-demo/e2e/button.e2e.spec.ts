import { test, expect } from '@playwright/test';

/**
 * End-to-End Tests for Button Component
 *
 * These tests simulate real user scenarios by testing the component
 * in the actual Storybook environment.
 */

test.describe('Button E2E Tests', () => {
  test('should navigate to Button story and interact with it', async ({ page }) => {
    // Navigate to the Button component in Storybook
    await page.goto('/iframe.html?id=components-button--primary');

    // Wait for the button to be visible - use specific selector
    const button = page.locator('#storybook-root button.btn');
    await expect(button).toBeVisible();

    // Check button properties
    await expect(button).toHaveClass(/btn--primary/);

    // Test interaction
    await button.click();
  });

  test('should test different button variants', async ({ page }) => {
    // Test Primary variant
    await page.goto('/iframe.html?id=components-button--primary');
    const primaryButton = page.locator('#storybook-root button.btn');
    await expect(primaryButton).toBeVisible();
    await expect(primaryButton).toHaveClass(/btn--primary/);

    // Test Secondary variant
    await page.goto('/iframe.html?id=components-button--secondary');
    const secondaryButton = page.locator('#storybook-root button.btn');
    await expect(secondaryButton).toBeVisible();
    await expect(secondaryButton).toHaveClass(/btn--secondary/);

    // Test Danger variant
    await page.goto('/iframe.html?id=components-button--danger');
    const dangerButton = page.locator('#storybook-root button.btn');
    await expect(dangerButton).toBeVisible();
    await expect(dangerButton).toHaveClass(/btn--danger/);
  });

  test('should handle disabled state correctly', async ({ page }) => {
    await page.goto('/iframe.html?id=components-button--disabled');

    const button = page.locator('#storybook-root button.btn');
    await expect(button).toBeVisible();
    await expect(button).toBeDisabled();

    // Verify disabled styling
    await expect(button).toHaveClass(/btn--disabled/);
  });

  test('should support keyboard navigation', async ({ page }) => {
    await page.goto('/iframe.html?id=components-button--primary');

    const button = page.locator('#storybook-root button.btn');
    await expect(button).toBeVisible();

    // Focus the button
    await button.focus();
    await expect(button).toBeFocused();

    // Activate using Enter
    await page.keyboard.press('Enter');
  });

  test('should take screenshot for visual regression', async ({ page }) => {
    await page.goto('/iframe.html?id=components-button--primary');

    // Wait for button to be visible
    await page.locator('#storybook-root button.btn').waitFor();

    // Take a screenshot for visual regression testing
    await expect(page).toHaveScreenshot('button-primary.png');
  });

  test('should test all button sizes', async ({ page }) => {
    // Small
    await page.goto('/iframe.html?id=components-button--small');
    const smallButton = page.locator('#storybook-root button.btn');
    await expect(smallButton).toBeVisible();
    await expect(smallButton).toHaveClass(/btn--small/);

    // Large
    await page.goto('/iframe.html?id=components-button--large');
    const largeButton = page.locator('#storybook-root button.btn');
    await expect(largeButton).toBeVisible();
    await expect(largeButton).toHaveClass(/btn--large/);
  });

  test('should verify button text content', async ({ page }) => {
    await page.goto('/iframe.html?id=components-button--primary');

    const button = page.locator('#storybook-root button.btn');
    await expect(button).toHaveText('Primary Button');
  });

  test('should verify button accessibility', async ({ page }) => {
    await page.goto('/iframe.html?id=components-button--primary');

    const button = page.locator('#storybook-root button.btn');

    // Check ARIA attributes
    await expect(button).toHaveAttribute('type', 'button');
    await expect(button).toHaveAttribute('aria-label');
  });
});
