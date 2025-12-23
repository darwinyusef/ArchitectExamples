import React from 'react';
import './Button.css';

export interface ButtonProps {
  /** Button variant */
  variant?: 'primary' | 'secondary' | 'danger';
  /** Button size */
  size?: 'small' | 'medium' | 'large';
  /** Button label */
  label: string;
  /** Is button disabled? */
  disabled?: boolean;
  /** Click handler */
  onClick?: () => void;
  /** Accessibility label */
  ariaLabel?: string;
}

/**
 * A reusable button component with accessibility support
 */
export const Button = ({
  variant = 'primary',
  size = 'medium',
  label,
  disabled = false,
  onClick,
  ariaLabel,
}: ButtonProps) => {
  const classNames = [
    'btn',
    `btn--${variant}`,
    `btn--${size}`,
    disabled && 'btn--disabled',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button
      type="button"
      className={classNames}
      disabled={disabled}
      onClick={onClick}
      aria-label={ariaLabel || label}
      aria-disabled={disabled}
    >
      {label}
    </button>
  );
};
