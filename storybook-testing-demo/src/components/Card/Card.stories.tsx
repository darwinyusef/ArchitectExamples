import type { Meta, StoryObj } from '@storybook/react-vite';
import { fn, expect, userEvent, within } from 'storybook/test';
import { Card } from './Card';

const meta = {
  title: 'Components/Card',
  component: Card,
  parameters: {
    layout: 'centered',
    a11y: {
      config: {
        rules: [
          {
            id: 'color-contrast',
            enabled: true,
          },
        ],
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    elevated: {
      control: 'boolean',
    },
    clickable: {
      control: 'boolean',
    },
  },
} satisfies Meta<typeof Card>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Basic: Story = {
  args: {
    title: 'Card Title',
    description: 'This is a basic card with a title and description.',
  },
};

export const WithImage: Story = {
  args: {
    title: 'Beautiful Landscape',
    description: 'A stunning view of mountains and forests.',
    imageUrl: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=200&fit=crop',
  },
};

export const Elevated: Story = {
  args: {
    title: 'Elevated Card',
    description: 'This card has a shadow effect to appear elevated.',
    elevated: true,
  },
};

export const WithFooter: Story = {
  args: {
    title: 'Card with Footer',
    description: 'This card includes a footer section.',
    footer: <div style={{ fontSize: '12px', color: '#666' }}>Last updated: 2 hours ago</div>,
  },
};

export const Clickable: Story = {
  args: {
    title: 'Clickable Card',
    description: 'Click this card to see the interaction.',
    clickable: true,
    onClick: fn(),
  },
};

export const Complete: Story = {
  args: {
    title: 'Complete Card',
    description: 'This card has all features: image, elevation, footer, and is clickable.',
    imageUrl: 'https://images.unsplash.com/photo-1682687220742-aba13b6e50ba?w=400&h=200&fit=crop',
    elevated: true,
    clickable: true,
    onClick: fn(),
    footer: (
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
        <span>Author: John Doe</span>
        <span>5 min read</span>
      </div>
    ),
  },
};

/**
 * Test interaction with clickable card
 */
export const ClickableCardTest: Story = {
  args: {
    title: 'Click Test',
    description: 'Testing card click functionality',
    clickable: true,
    onClick: fn(),
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);
    const card = canvas.getByRole('button');

    // Test: Card should be in the document
    await expect(card).toBeInTheDocument();

    // Test: Card should have correct title
    await expect(card).toHaveTextContent('Click Test');

    // Test: Card should be clickable
    await userEvent.click(card);
    await expect(args.onClick).toHaveBeenCalledTimes(1);
  },
};

/**
 * Test keyboard navigation on clickable card
 */
export const KeyboardNavigationTest: Story = {
  args: {
    title: 'Keyboard Test',
    description: 'Testing keyboard navigation',
    clickable: true,
    onClick: fn(),
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);
    const card = canvas.getByRole('button');

    // Test: Card should be focusable
    card.focus();
    await expect(card).toHaveFocus();

    // Test: Enter key should trigger onClick
    await userEvent.keyboard('{Enter}');
    await expect(args.onClick).toHaveBeenCalledTimes(1);

    // Test: Space key should trigger onClick
    await userEvent.keyboard(' ');
    await expect(args.onClick).toHaveBeenCalledTimes(2);
  },
};

/**
 * Visual regression test - card with image
 */
export const VisualTest: Story = {
  args: {
    title: 'Visual Regression Test',
    description: 'This story is used for visual regression testing.',
    imageUrl: 'https://images.unsplash.com/photo-1682687220742-aba13b6e50ba?w=400&h=200&fit=crop',
    elevated: true,
    footer: <div>Footer content</div>,
  },
  parameters: {
    // Chromatic snapshots will capture this story
    chromatic: { disableSnapshot: false },
  },
};
