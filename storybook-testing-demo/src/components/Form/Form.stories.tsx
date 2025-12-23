import type { Meta, StoryObj } from '@storybook/react-vite';
import { fn, expect, userEvent, within, waitFor } from 'storybook/test';
import { Form } from './Form';

const meta = {
  title: 'Components/Form',
  component: Form,
  parameters: {
    layout: 'centered',
    a11y: {
      config: {
        rules: [
          {
            id: 'label',
            enabled: true,
          },
          {
            id: 'color-contrast',
            enabled: true,
          },
        ],
      },
    },
  },
  tags: ['autodocs'],
  args: {
    onSubmit: fn(),
  },
} satisfies Meta<typeof Form>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {},
};

export const CustomLabels: Story = {
  args: {
    title: 'Sign In to Your Account',
    submitLabel: 'Login',
  },
};

export const Submitting: Story = {
  args: {
    isSubmitting: true,
  },
};

/**
 * Test successful form submission
 */
export const SuccessfulSubmission: Story = {
  args: {
    onSubmit: fn(),
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);

    // Find form inputs
    const emailInput = canvas.getByLabelText('Email');
    const passwordInput = canvas.getByLabelText('Password');
    const submitButton = canvas.getByRole('button', { name: /sign in/i });

    // Test: Inputs should be in the document
    await expect(emailInput).toBeInTheDocument();
    await expect(passwordInput).toBeInTheDocument();

    // Fill in the form
    await userEvent.type(emailInput, 'user@example.com');
    await userEvent.type(passwordInput, 'password123');

    // Submit the form
    await userEvent.click(submitButton);

    // Test: onSubmit should be called with correct data
    await waitFor(() =>
      expect(args.onSubmit).toHaveBeenCalledWith({
        email: 'user@example.com',
        password: 'password123',
        rememberMe: false,
      })
    );
  },
};

/**
 * Test email validation
 */
export const EmailValidation: Story = {
  args: {
    onSubmit: fn(),
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);

    const emailInput = canvas.getByLabelText('Email');
    const submitButton = canvas.getByRole('button', { name: /sign in/i });

    // Test: Submit with empty email
    await userEvent.click(submitButton);

    // Test: Error message should appear
    await waitFor(() =>
      expect(canvas.getByText('Email is required')).toBeInTheDocument()
    );
    expect(args.onSubmit).not.toHaveBeenCalled();

    // Test: Submit with invalid email
    await userEvent.type(emailInput, 'invalid-email');
    await userEvent.click(submitButton);

    await waitFor(() =>
      expect(canvas.getByText('Please enter a valid email')).toBeInTheDocument()
    );

    // Test: Error should have aria role
    const errorElement = canvas.getByText('Please enter a valid email');
    expect(errorElement).toHaveAttribute('role', 'alert');
  },
};

/**
 * Test password validation
 */
export const PasswordValidation: Story = {
  args: {
    onSubmit: fn(),
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);

    const emailInput = canvas.getByLabelText('Email');
    const passwordInput = canvas.getByLabelText('Password');
    const submitButton = canvas.getByRole('button', { name: /sign in/i });

    // Fill valid email
    await userEvent.type(emailInput, 'user@example.com');

    // Test: Submit with empty password
    await userEvent.click(submitButton);

    await waitFor(() =>
      expect(canvas.getByText('Password is required')).toBeInTheDocument()
    );
    expect(args.onSubmit).not.toHaveBeenCalled();

    // Test: Submit with short password
    await userEvent.type(passwordInput, '12345');
    await userEvent.click(submitButton);

    await waitFor(() =>
      expect(
        canvas.getByText('Password must be at least 6 characters')
      ).toBeInTheDocument()
    );
  },
};

/**
 * Test remember me checkbox
 */
export const RememberMeCheckbox: Story = {
  args: {
    onSubmit: fn(),
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);

    const emailInput = canvas.getByLabelText('Email');
    const passwordInput = canvas.getByLabelText('Password');
    const rememberMeCheckbox = canvas.getByLabelText('Remember me');
    const submitButton = canvas.getByRole('button', { name: /sign in/i });

    // Fill in the form
    await userEvent.type(emailInput, 'user@example.com');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(rememberMeCheckbox);

    // Test: Checkbox should be checked
    await expect(rememberMeCheckbox).toBeChecked();

    // Submit the form
    await userEvent.click(submitButton);

    // Test: onSubmit should be called with rememberMe: true
    await waitFor(() =>
      expect(args.onSubmit).toHaveBeenCalledWith({
        email: 'user@example.com',
        password: 'password123',
        rememberMe: true,
      })
    );
  },
};

/**
 * Test form field blur validation
 */
export const BlurValidation: Story = {
  args: {
    onSubmit: fn(),
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    const emailInput = canvas.getByLabelText('Email');
    const passwordInput = canvas.getByLabelText('Password');

    // Test: Focus and blur email without entering value
    emailInput.focus();
    emailInput.blur();

    await waitFor(() =>
      expect(canvas.getByText('Email is required')).toBeInTheDocument()
    );

    // Test: Enter invalid email and blur
    await userEvent.type(emailInput, 'invalid');
    passwordInput.focus(); // blur email by focusing password

    await waitFor(() =>
      expect(canvas.getByText('Please enter a valid email')).toBeInTheDocument()
    );

    // Test: aria-invalid should be set
    expect(emailInput).toHaveAttribute('aria-invalid', 'true');
  },
};

/**
 * Test keyboard navigation
 */
export const KeyboardNavigation: Story = {
  args: {
    onSubmit: fn(),
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);

    const emailInput = canvas.getByLabelText('Email');
    const passwordInput = canvas.getByLabelText('Password');
    const submitButton = canvas.getByRole('button', { name: /sign in/i });

    // Tab through form
    await userEvent.tab();
    await expect(emailInput).toHaveFocus();

    await userEvent.keyboard('user@example.com');

    await userEvent.tab();
    await expect(passwordInput).toHaveFocus();

    await userEvent.keyboard('password123');

    await userEvent.tab();
    // Should focus remember me checkbox
    const rememberMeCheckbox = canvas.getByLabelText('Remember me');
    await expect(rememberMeCheckbox).toHaveFocus();

    await userEvent.tab();
    await expect(submitButton).toHaveFocus();

    // Submit with Enter key
    await userEvent.keyboard('{Enter}');

    await waitFor(() => expect(args.onSubmit).toHaveBeenCalled());
  },
};

/**
 * Test disabled state
 */
export const DisabledState: Story = {
  args: {
    isSubmitting: true,
    onSubmit: fn(),
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);

    const emailInput = canvas.getByLabelText('Email');
    const passwordInput = canvas.getByLabelText('Password');
    const rememberMeCheckbox = canvas.getByLabelText('Remember me');
    const submitButton = canvas.getByRole('button', { name: /signing in/i });

    // Test: All inputs should be disabled
    await expect(emailInput).toBeDisabled();
    await expect(passwordInput).toBeDisabled();
    await expect(rememberMeCheckbox).toBeDisabled();
    await expect(submitButton).toBeDisabled();

    // Test: Button should have aria-busy
    await expect(submitButton).toHaveAttribute('aria-busy', 'true');

    // Test: Should not be able to submit
    await userEvent.click(submitButton);
    expect(args.onSubmit).not.toHaveBeenCalled();
  },
};
