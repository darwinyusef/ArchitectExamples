import React, { useState } from 'react';
import './Form.css';

export interface FormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

export interface FormProps {
  /** Form submit handler */
  onSubmit: (data: FormData) => void;
  /** Is form submitting? */
  isSubmitting?: boolean;
  /** Form title */
  title?: string;
  /** Submit button label */
  submitLabel?: string;
}

interface FormErrors {
  email?: string;
  password?: string;
}

/**
 * A login form component with validation
 */
export const Form = ({
  onSubmit,
  isSubmitting = false,
  title = 'Login',
  submitLabel = 'Sign In',
}: FormProps) => {
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
    rememberMe: false,
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const validateEmail = (email: string): string | undefined => {
    if (!email) {
      return 'Email is required';
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return 'Please enter a valid email';
    }
    return undefined;
  };

  const validatePassword = (password: string): string | undefined => {
    if (!password) {
      return 'Password is required';
    }
    if (password.length < 6) {
      return 'Password must be at least 6 characters';
    }
    return undefined;
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {
      email: validateEmail(formData.email),
      password: validatePassword(formData.password),
    };

    setErrors(newErrors);
    return !newErrors.email && !newErrors.password;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all fields as touched
    setTouched({ email: true, password: true });

    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const handleBlur = (field: string) => {
    setTouched({ ...touched, [field]: true });

    // Validate on blur
    if (field === 'email') {
      setErrors({ ...errors, email: validateEmail(formData.email) });
    } else if (field === 'password') {
      setErrors({ ...errors, password: validatePassword(formData.password) });
    }
  };

  const handleChange = (field: keyof FormData, value: string | boolean) => {
    setFormData({ ...formData, [field]: value });

    // Clear error when user starts typing
    if (typeof value === 'string' && value) {
      setErrors({ ...errors, [field]: undefined });
    }
  };

  return (
    <div className="form-container">
      <form className="form" onSubmit={handleSubmit} noValidate>
        <h2 className="form__title">{title}</h2>

        <div className="form__field">
          <label htmlFor="email" className="form__label">
            Email
          </label>
          <input
            id="email"
            type="email"
            className={`form__input ${touched.email && errors.email ? 'form__input--error' : ''}`}
            value={formData.email}
            onChange={(e) => handleChange('email', e.target.value)}
            onBlur={() => handleBlur('email')}
            disabled={isSubmitting}
            aria-invalid={touched.email && !!errors.email}
            aria-describedby={touched.email && errors.email ? 'email-error' : undefined}
          />
          {touched.email && errors.email && (
            <span id="email-error" className="form__error" role="alert">
              {errors.email}
            </span>
          )}
        </div>

        <div className="form__field">
          <label htmlFor="password" className="form__label">
            Password
          </label>
          <input
            id="password"
            type="password"
            className={`form__input ${touched.password && errors.password ? 'form__input--error' : ''}`}
            value={formData.password}
            onChange={(e) => handleChange('password', e.target.value)}
            onBlur={() => handleBlur('password')}
            disabled={isSubmitting}
            aria-invalid={touched.password && !!errors.password}
            aria-describedby={touched.password && errors.password ? 'password-error' : undefined}
          />
          {touched.password && errors.password && (
            <span id="password-error" className="form__error" role="alert">
              {errors.password}
            </span>
          )}
        </div>

        <div className="form__field form__field--checkbox">
          <label className="form__checkbox-label">
            <input
              type="checkbox"
              checked={formData.rememberMe}
              onChange={(e) => handleChange('rememberMe', e.target.checked)}
              disabled={isSubmitting}
            />
            <span>Remember me</span>
          </label>
        </div>

        <button
          type="submit"
          className="form__submit"
          disabled={isSubmitting}
          aria-busy={isSubmitting}
        >
          {isSubmitting ? 'Signing in...' : submitLabel}
        </button>
      </form>
    </div>
  );
};
