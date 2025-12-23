import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { composeStories } from '@storybook/react-vite';
import * as stories from './Button.stories';
import { Button } from './Button';

// Compose stories for testing
const { Primary, Secondary, Disabled } = composeStories(stories);

describe('Button Component', () => {
  // Unit tests
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

    it('renders with correct size class', () => {
      render(<Button label="Large" size="large" />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('btn--large');
    });

    it('is disabled when disabled prop is true', () => {
      render(<Button label="Disabled" disabled={true} />);
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
    });

    it('does not trigger onClick when disabled', () => {
      const handleClick = vi.fn();
      render(<Button label="Disabled" disabled={true} onClick={handleClick} />);

      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(handleClick).not.toHaveBeenCalled();
    });

    it('has correct aria-label', () => {
      render(<Button label="Test" ariaLabel="Custom Aria Label" />);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Custom Aria Label');
    });

    it('uses label as aria-label when ariaLabel is not provided', () => {
      render(<Button label="Test Button" />);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Test Button');
    });
  });

  // Snapshot tests
  describe('Snapshot Tests', () => {
    it('matches snapshot for primary variant', () => {
      const { container } = render(<Primary />);
      expect(container.firstChild).toMatchSnapshot();
    });

    it('matches snapshot for secondary variant', () => {
      const { container } = render(<Secondary />);
      expect(container.firstChild).toMatchSnapshot();
    });

    it('matches snapshot for disabled state', () => {
      const { container } = render(<Disabled />);
      expect(container.firstChild).toMatchSnapshot();
    });

    it('matches snapshot for all size variations', () => {
      const { container: smallContainer } = render(<Button label="Small" size="small" />);
      const { container: mediumContainer } = render(<Button label="Medium" size="medium" />);
      const { container: largeContainer } = render(<Button label="Large" size="large" />);

      expect(smallContainer.firstChild).toMatchSnapshot();
      expect(mediumContainer.firstChild).toMatchSnapshot();
      expect(largeContainer.firstChild).toMatchSnapshot();
    });
  });

  // Story-based tests
  describe('Story Tests', () => {
    it('renders Primary story correctly', () => {
      render(<Primary />);
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('renders Secondary story correctly', () => {
      render(<Secondary />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('btn--secondary');
    });

    it('renders Disabled story correctly', () => {
      render(<Disabled />);
      expect(screen.getByRole('button')).toBeDisabled();
    });
  });
});
