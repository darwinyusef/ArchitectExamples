import { test, expect } from '@playwright/test';

/**
 * End-to-End Tests for Form Component
 *
 * These tests simulate real user workflows including
 * form validation, submission, and error handling.
 */

test.describe('Form E2E Tests', () => {
  test('should successfully submit form with valid data', async ({ page }) => {
    await page.goto('/iframe.html?id=components-form--default');

    // Fill out the form using specific selectors
    await page.fill('#storybook-root input[type="email"]', 'user@example.com');
    await page.fill('#storybook-root input[type="password"]', 'securePassword123');

    // Check remember me
    await page.check('#storybook-root input[type="checkbox"]');

    // Submit the form
    await page.click('#storybook-root button[type="submit"]');

    // Form should not show errors
    await expect(page.locator('#storybook-root [role="alert"]')).not.toBeVisible();
  });

  test('should show validation errors on invalid submission', async ({ page }) => {
    await page.goto('/iframe.html?id=components-form--default');

    // Submit empty form
    await page.click('#storybook-root button[type="submit"]');

    // Should show error messages
    await expect(page.locator('#storybook-root >> text=Email is required')).toBeVisible();
    await expect(page.locator('#storybook-root >> text=Password is required')).toBeVisible();
  });

  test('should validate email format', async ({ page }) => {
    await page.goto('/iframe.html?id=components-form--default');

    // Enter invalid email
    await page.fill('#storybook-root input[type="email"]', 'invalid-email');
    await page.fill('#storybook-root input[type="password"]', 'password123');

    // Submit
    await page.click('#storybook-root button[type="submit"]');

    // Should show email validation error
    await expect(page.locator('#storybook-root >> text=Please enter a valid email')).toBeVisible();
  });

  test('should validate password length', async ({ page }) => {
    await page.goto('/iframe.html?id=components-form--default');

    // Enter valid email but short password
    await page.fill('#storybook-root input[type="email"]', 'user@example.com');
    await page.fill('#storybook-root input[type="password"]', '123');

    // Submit
    await page.click('#storybook-root button[type="submit"]');

    // Should show password validation error
    await expect(
      page.locator('#storybook-root >> text=Password must be at least 6 characters')
    ).toBeVisible();
  });

  test('should show validation on blur', async ({ page }) => {
    await page.goto('/iframe.html?id=components-form--default');

    const emailInput = page.locator('#storybook-root input[type="email"]');

    // Focus and blur without entering value
    await emailInput.focus();
    await emailInput.blur();

    // Should show error
    await expect(page.locator('#storybook-root >> text=Email is required')).toBeVisible();
  });

  test('should clear error when user starts typing', async ({ page }) => {
    await page.goto('/iframe.html?id=components-form--default');

    // Submit to trigger errors
    await page.click('#storybook-root button[type="submit"]');
    await expect(page.locator('#storybook-root >> text=Email is required')).toBeVisible();

    // Start typing
    await page.fill('#storybook-root input[type="email"]', 'u');

    // Error should be cleared
    await expect(page.locator('#storybook-root >> text=Email is required')).not.toBeVisible();
  });

  test('should handle keyboard navigation', async ({ page }) => {
    await page.goto('/iframe.html?id=components-form--default');

    // Focus first input directly
    const emailInput = page.locator('#storybook-root input[type="email"]');
    await emailInput.focus();
    await expect(emailInput).toBeFocused();

    // Tab to password
    await page.keyboard.press('Tab');
    const passwordInput = page.locator('#storybook-root input[type="password"]');
    await expect(passwordInput).toBeFocused();

    // Tab to checkbox
    await page.keyboard.press('Tab');
    const checkbox = page.locator('#storybook-root input[type="checkbox"]');
    await expect(checkbox).toBeFocused();

    // Tab to submit button
    await page.keyboard.press('Tab');
    const submitButton = page.locator('#storybook-root button[type="submit"]');
    await expect(submitButton).toBeFocused();
  });

  test('should disable form when submitting', async ({ page }) => {
    await page.goto('/iframe.html?id=components-form--submitting');

    // All inputs should be disabled
    await expect(page.locator('#storybook-root input[type="email"]')).toBeDisabled();
    await expect(page.locator('#storybook-root input[type="password"]')).toBeDisabled();
    await expect(page.locator('#storybook-root input[type="checkbox"]')).toBeDisabled();
    await expect(page.locator('#storybook-root button[type="submit"]')).toBeDisabled();

    // Button should show loading text
    await expect(page.locator('#storybook-root button:has-text("Signing in...")')).toBeVisible();
  });

  test('should have proper accessibility attributes', async ({ page }) => {
    await page.goto('/iframe.html?id=components-form--default');

    // Submit to trigger validation errors
    await page.click('#storybook-root button[type="submit"]');

    const emailInput = page.locator('#storybook-root input[type="email"]');

    // Check aria-invalid attribute
    await expect(emailInput).toHaveAttribute('aria-invalid', 'true');

    // Check aria-describedby points to error message
    await expect(emailInput).toHaveAttribute('aria-describedby', 'email-error');

    // Check error has role="alert"
    const errorMessage = page.locator('#storybook-root #email-error');
    await expect(errorMessage).toHaveAttribute('role', 'alert');
  });

  test('should take screenshot for visual regression', async ({ page }) => {
    await page.goto('/iframe.html?id=components-form--default');

    // Wait for form to be visible
    await page.locator('#storybook-root form').waitFor();

    // Screenshot of default state
    await expect(page).toHaveScreenshot('form-default.png');

    // Submit to show errors
    await page.click('#storybook-root button[type="submit"]');

    // Wait for errors to appear
    await page.locator('#storybook-root >> text=Email is required').waitFor();

    // Screenshot of error state
    await expect(page).toHaveScreenshot('form-with-errors.png');
  });
});
