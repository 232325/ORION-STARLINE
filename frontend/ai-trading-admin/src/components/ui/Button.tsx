import React, { ButtonHTMLAttributes, forwardRef } from 'react';
import { cn } from '../../lib/utils';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'ghost' | 'outline' | 'glass';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  fullWidth?: boolean;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      fullWidth = false,
      loading = false,
      leftIcon,
      rightIcon,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const baseStyles = 
      'inline-flex items-center justify-center gap-2 font-semibold rounded-lg transition-all duration-normal ' +
      'focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed ' +
      'active:scale-[0.98] hover:scale-[1.02]';

    const variants = {
      primary:
        'bg-gradient-primary text-white shadow-md hover:shadow-lg hover:brightness-110',
      secondary:
        'bg-transparent border-2 border-primary-500 text-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20',
      success:
        'bg-gradient-success text-white shadow-md hover:shadow-lg hover:brightness-110',
      danger:
        'bg-gradient-danger text-white shadow-md hover:shadow-lg hover:brightness-110',
      warning:
        'bg-gradient-warning text-white shadow-md hover:shadow-lg hover:brightness-110',
      ghost:
        'bg-transparent text-neutral-700 dark:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-800',
      outline:
        'bg-transparent border border-neutral-300 dark:border-neutral-700 text-neutral-700 dark:text-neutral-200 ' +
        'hover:bg-neutral-100 dark:hover:bg-neutral-800',
      glass:
        'glass-card text-neutral-900 dark:text-white hover:bg-white/20 dark:hover:bg-white/10',
    };

    const sizes = {
      sm: 'text-sm px-3 py-1.5 h-9',
      md: 'text-base px-4 py-2 h-10',
      lg: 'text-lg px-6 py-3 h-12',
      xl: 'text-xl px-8 py-4 h-14',
    };

    return (
      <button
        ref={ref}
        className={cn(
          baseStyles,
          variants[variant],
          sizes[size],
          fullWidth && 'w-full',
          className
        )}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <>
            <svg
              className="animate-spin h-5 w-5"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            <span>Yuklanmoqda...</span>
          </>
        ) : (
          <>
            {leftIcon && <span className="inline-flex">{leftIcon}</span>}
            {children}
            {rightIcon && <span className="inline-flex">{rightIcon}</span>}
          </>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;
