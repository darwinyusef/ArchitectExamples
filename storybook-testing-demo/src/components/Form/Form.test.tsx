import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { composeStories } from '@storybook/react-vite';
import * as stories from './Form.stories';
import { Form } from './Form';

const { Default, Submitting } = composeStories(stories);

describe('Form Component', () => {
  let onSubmitMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    onSubmitMock = vi.fn();
  });

  describe('Rendering Tests', () => {
    it('renders form with title and inputs', () => {
      render(<Form onSubmit={onSubmitMock} />);

      expect(screen.getByText('Login')).toBeInTheDocument();
      expect(screen.getByLabelText('Email')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
      expect(screen.getByLabelText('Remember me')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    });

    it('renders with custom title and submit label', () => {
      render(<Form onSubmit={onSubmitMock} title="Welcome" submitLabel="Login" />);

      expect(screen.getByText('Welcome')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
    });
  });

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

      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Please enter a valid email')).toBeInTheDocument();
      });
      expect(onSubmitMock).not.toHaveBeenCalled();
    });

    it('shows password required error', async () => {
      render(<Form onSubmit={onSubmitMock} />);

      const emailInput = screen.getByLabelText('Email');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'user@example.com' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Password is required')).toBeInTheDocument();
      });
      expect(onSubmitMock).not.toHaveBeenCalled();
    });

    it('shows password length error', async () => {
      render(<Form onSubmit={onSubmitMock} />);

      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'user@example.com' } });
      fireEvent.change(passwordInput, { target: { value: '123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Password must be at least 6 characters')).toBeInTheDocument();
      });
      expect(onSubmitMock).not.toHaveBeenCalled();
    });
  });

  describe('Submission Tests', () => {
    it('submits form with valid data', async () => {
      render(<Form onSubmit={onSubmitMock} />);

      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Password');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'user@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(onSubmitMock).toHaveBeenCalledWith({
          email: 'user@example.com',
          password: 'password123',
          rememberMe: false,
        });
      });
    });

    it('submits with remember me checked', async () => {
      render(<Form onSubmit={onSubmitMock} />);

      const emailInput = screen.getByLabelText('Email');
      const passwordInput = screen.getByLabelText('Password');
      const rememberMeCheckbox = screen.getByLabelText('Remember me');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'user@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(rememberMeCheckbox);
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(onSubmitMock).toHaveBeenCalledWith({
          email: 'user@example.com',
          password: 'password123',
          rememberMe: true,
        });
      });
    });
  });

  describe('Disabled State Tests', () => {
    it('disables all inputs when isSubmitting is true', () => {
      render(<Form onSubmit={onSubmitMock} isSubmitting={true} />);

      expect(screen.getByLabelText('Email')).toBeDisabled();
      expect(screen.getByLabelText('Password')).toBeDisabled();
      expect(screen.getByLabelText('Remember me')).toBeDisabled();
      expect(screen.getByRole('button')).toBeDisabled();
    });

    it('shows submitting text on button', () => {
      render(<Form onSubmit={onSubmitMock} isSubmitting={true} />);

      expect(screen.getByText('Signing in...')).toBeInTheDocument();
    });
  });

  describe('Accessibility Tests', () => {
    it('has proper aria-invalid on invalid email', async () => {
      render(<Form onSubmit={onSubmitMock} />);

      const emailInput = screen.getByLabelText('Email');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(emailInput).toHaveAttribute('aria-invalid', 'true');
      });
    });

    it('has proper aria-describedby on error', async () => {
      render(<Form onSubmit={onSubmitMock} />);

      const emailInput = screen.getByLabelText('Email');
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(emailInput).toHaveAttribute('aria-describedby', 'email-error');
      });
    });

    it('error messages have role="alert"', async () => {
      render(<Form onSubmit={onSubmitMock} />);

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        const errorElement = screen.getByText('Email is required');
        expect(errorElement).toHaveAttribute('role', 'alert');
      });
    });
  });

  describe('Snapshot Tests', () => {
    it('matches snapshot for default state', () => {
      const { container } = render(<Default />);
      expect(container.firstChild).toMatchSnapshot();
    });

    it('matches snapshot for submitting state', () => {
      const { container } = render(<Submitting />);
      expect(container.firstChild).toMatchSnapshot();
    });
  });
});
