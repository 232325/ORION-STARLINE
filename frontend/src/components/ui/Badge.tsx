import React, { HTMLAttributes, forwardRef } from 'react';
import { cn } from '../../lib/utils';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'danger' | 'warning' | 'info' | 'neutral' | 'primary';
  size?: 'sm' | 'md' | 'lg';
  rounded?: boolean;
  outlined?: boolean;
  dot?: boolean;
}

const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  (
    {
      className,
      variant = 'default',
      size = 'md',
      rounded = false,
      outlined = false,
      dot = false,
      children,
      ...props
    },
    ref
  ) => {
    const baseStyles =
      'inline-flex items-center gap-1.5 font-medium transition-colors whitespace-nowrap';

    const variants = outlined
      ? {
          default:
            'bg-transparent border border-neutral-300 text-neutral-700 dark:border-neutral-600 dark:text-neutral-300',
          success:
            'bg-transparent border border-success-500 text-success-700 dark:text-success-400',
          danger:
            'bg-transparent border border-danger-500 text-danger-700 dark:text-danger-400',
          warning:
            'bg-transparent border border-warning-500 text-warning-700 dark:text-warning-400',
          info:
            'bg-transparent border border-primary-500 text-primary-700 dark:text-primary-400',
          neutral:
            'bg-transparent border border-neutral-400 text-neutral-700 dark:text-neutral-300',
          primary:
            'bg-transparent border border-primary-600 text-primary-700 dark:text-primary-400',
        }
      : {
          default:
            'bg-neutral-100 text-neutral-800 dark:bg-neutral-700 dark:text-neutral-200',
          success:
            'bg-success-100 text-success-800 dark:bg-success-900/30 dark:text-success-300',
          danger:
            'bg-danger-100 text-danger-800 dark:bg-danger-900/30 dark:text-danger-300',
          warning:
            'bg-warning-100 text-warning-800 dark:bg-warning-900/30 dark:text-warning-300',
          info:
            'bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-300',
          neutral:
            'bg-neutral-200 text-neutral-800 dark:bg-neutral-700 dark:text-neutral-200',
          primary:
            'bg-primary-500 text-white dark:bg-primary-600',
        };

    const sizes = {
      sm: 'text-xs px-2 py-0.5 rounded-md',
      md: 'text-sm px-2.5 py-1 rounded-lg',
      lg: 'text-base px-3 py-1.5 rounded-lg',
    };

    const dotColors = {
      default: 'bg-neutral-500',
      success: 'bg-success-500',
      danger: 'bg-danger-500',
      warning: 'bg-warning-500',
      info: 'bg-primary-500',
      neutral: 'bg-neutral-500',
      primary: 'bg-primary-500',
    };

    return (
      <span
        ref={ref}
        className={cn(
          baseStyles,
          variants[variant],
          sizes[size],
          rounded && 'rounded-full',
          className
        )}
        {...props}
      >
        {dot && (
          <span
            className={cn(
              'h-2 w-2 rounded-full',
              dotColors[variant]
            )}
          />
        )}
        {children}
      </span>
    );
  }
);

Badge.displayName = 'Badge';

export default Badge;
