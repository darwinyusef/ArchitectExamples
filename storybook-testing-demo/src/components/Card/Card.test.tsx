import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { composeStories } from '@storybook/react-vite';
import * as stories from './Card.stories';
import { Card } from './Card';

const { Basic, WithImage, Clickable } = composeStories(stories);

describe('Card Component', () => {
  describe('Unit Tests', () => {
    it('renders with title and description', () => {
      render(<Card title="Test Title" description="Test Description" />);

      expect(screen.getByText('Test Title')).toBeInTheDocument();
      expect(screen.getByText('Test Description')).toBeInTheDocument();
    });

    it('renders with image when imageUrl is provided', () => {
      render(<Card title="Test" description="Test" imageUrl="test.jpg" />);

      const image = screen.getByAltText('Test');
      expect(image).toBeInTheDocument();
      expect(image).toHaveAttribute('src', 'test.jpg');
    });

    it('does not render image when imageUrl is not provided', () => {
      render(<Card title="Test" description="Test" />);

      const image = screen.queryByRole('img');
      expect(image).not.toBeInTheDocument();
    });

    it('renders footer when provided', () => {
      render(<Card title="Test" description="Test" footer={<div>Footer Content</div>} />);

      expect(screen.getByText('Footer Content')).toBeInTheDocument();
    });

    it('applies elevated class when elevated is true', () => {
      const { container } = render(<Card title="Test" description="Test" elevated={true} />);

      const card = container.querySelector('.card--elevated');
      expect(card).toBeInTheDocument();
    });

    it('applies clickable class when clickable is true', () => {
      const { container } = render(<Card title="Test" description="Test" clickable={true} />);

      const card = container.querySelector('.card--clickable');
      expect(card).toBeInTheDocument();
    });

    it('handles click when clickable', () => {
      const handleClick = vi.fn();
      render(<Card title="Test" description="Test" clickable={true} onClick={handleClick} />);

      const card = screen.getByRole('button');
      fireEvent.click(card);

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('does not handle click when not clickable', () => {
      const handleClick = vi.fn();
      render(<Card title="Test" description="Test" clickable={false} onClick={handleClick} />);

      const card = screen.getByRole('article');
      fireEvent.click(card);

      expect(handleClick).not.toHaveBeenCalled();
    });

    it('handles Enter key when clickable', () => {
      const handleClick = vi.fn();
      render(<Card title="Test" description="Test" clickable={true} onClick={handleClick} />);

      const card = screen.getByRole('button');
      fireEvent.keyDown(card, { key: 'Enter' });

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('handles Space key when clickable', () => {
      const handleClick = vi.fn();
      render(<Card title="Test" description="Test" clickable={true} onClick={handleClick} />);

      const card = screen.getByRole('button');
      fireEvent.keyDown(card, { key: ' ' });

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('has correct aria-label when clickable', () => {
      render(<Card title="My Card" description="Test" clickable={true} />);

      const card = screen.getByRole('button');
      expect(card).toHaveAttribute('aria-label', 'My Card card');
    });
  });

  describe('Snapshot Tests', () => {
    it('matches snapshot for basic card', () => {
      const { container } = render(<Basic />);
      expect(container.firstChild).toMatchSnapshot();
    });

    it('matches snapshot for card with image', () => {
      const { container } = render(<WithImage />);
      expect(container.firstChild).toMatchSnapshot();
    });

    it('matches snapshot for clickable card', () => {
      const { container } = render(<Clickable />);
      expect(container.firstChild).toMatchSnapshot();
    });
  });

  describe('Story Tests', () => {
    it('renders Basic story correctly', () => {
      render(<Basic />);
      expect(screen.getByText('Card Title')).toBeInTheDocument();
    });

    it('renders WithImage story correctly', () => {
      render(<WithImage />);
      expect(screen.getByAltText('Beautiful Landscape')).toBeInTheDocument();
    });

    it('renders Clickable story correctly', () => {
      render(<Clickable />);
      expect(screen.getByRole('button')).toBeInTheDocument();
    });
  });
});
