import React from 'react';
import './Card.css';

export interface CardProps {
  /** Card title */
  title: string;
  /** Card description */
  description: string;
  /** Card image URL */
  imageUrl?: string;
  /** Card footer content */
  footer?: React.ReactNode;
  /** Click handler for the card */
  onClick?: () => void;
  /** Is the card elevated? */
  elevated?: boolean;
  /** Is the card clickable? */
  clickable?: boolean;
}

/**
 * A flexible card component for displaying content
 */
export const Card = ({
  title,
  description,
  imageUrl,
  footer,
  onClick,
  elevated = false,
  clickable = false,
}: CardProps) => {
  const classNames = [
    'card',
    elevated && 'card--elevated',
    clickable && 'card--clickable',
  ]
    .filter(Boolean)
    .join(' ');

  const handleClick = () => {
    if (clickable && onClick) {
      onClick();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (clickable && onClick && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      onClick();
    }
  };

  return (
    <article
      className={classNames}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      role={clickable ? 'button' : undefined}
      tabIndex={clickable ? 0 : undefined}
      aria-label={clickable ? `${title} card` : undefined}
    >
      {imageUrl && (
        <div className="card__image">
          <img src={imageUrl} alt={title} />
        </div>
      )}
      <div className="card__content">
        <h3 className="card__title">{title}</h3>
        <p className="card__description">{description}</p>
      </div>
      {footer && <div className="card__footer">{footer}</div>}
    </article>
  );
};
