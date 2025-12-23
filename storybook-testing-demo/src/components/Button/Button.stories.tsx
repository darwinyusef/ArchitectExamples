import type { Meta, StoryObj } from '@storybook/react-vite';
import { fn, expect, userEvent, within } from 'storybook/test';
import { Button } from './Button';

/**
 * Button component with multiple variants and interaction tests
 */
const meta = {
  title: 'Components/Button',
  component: Button,
  parameters: {
    layout: 'centered',
    // Configure accessibility tests
    a11y: {
      config: {
        rules: [
          {
            id: 'color-contrast',
            enabled: true,
          },
          {
            id: 'button-name',
            enabled: true,
          },
        ],
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'danger'],
    },
    size: {
      control: 'select',
      options: ['small', 'medium', 'large'],
    },
    disabled: {
      control: 'boolean',
    },
  },
  args: {
    onClick: fn(),
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

// Basic variants
export const Primary: Story = {
  args: {
    variant: 'primary',
    label: 'Primary Button',
  },
};

export const Secondary: Story = {
  args: {
    variant: 'secondary',
    label: 'Secondary Button',
  },
};

export const Danger: Story = {
  args: {
    variant: 'danger',
    label: 'Danger Button',
  },
};

// Size variants
export const Small: Story = {
  args: {
    size: 'small',
    label: 'Small Button',
  },
};

export const Large: Story = {
  args: {
    size: 'large',
    label: 'Large Button',
  },
};

// State variants
export const Disabled: Story = {
  args: {
    disabled: true,
    label: 'Disabled Button',
  },
};

/**
 * Story with interaction test - tests that button click works
 */
export const WithInteractionTest: Story = {
  args: {
    variant: 'primary',
    label: 'Click Me',
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button');

    // Test: Button should be in the document
    await expect(button).toBeInTheDocument();

    // Test: Button should have the correct label
    await expect(button).toHaveTextContent('Click Me');

    // Test: Button should be clickable
    await userEvent.click(button);
    await expect(args.onClick).toHaveBeenCalledTimes(1);
  },
};

/**
 * Story with accessibility test - tests keyboard navigation
 */
export const KeyboardNavigation: Story = {
  args: {
    variant: 'primary',
    label: 'Keyboard Test',
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button');

    // Test: Button should be focusable
    button.focus();
    await expect(button).toHaveFocus();

    // Test: Button should respond to keyboard events
    await userEvent.keyboard('{Enter}');
    await expect(args.onClick).toHaveBeenCalled();
  },
};

/**
 * Story with disabled state test
 */
export const DisabledButtonTest: Story = {
  args: {
    variant: 'primary',
    label: 'Disabled',
    disabled: true,
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button');

    // Test: Button should be disabled
    await expect(button).toBeDisabled();

    // Test: Click should not work when disabled
    await userEvent.click(button);
    await expect(args.onClick).not.toHaveBeenCalled();
  },
};
