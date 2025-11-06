import React, { InputHTMLAttributes, forwardRef, useState } from 'react';
import { cn } from '../../lib/utils';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      type = 'text',
      label,
      error,
      helperText,
      leftIcon,
      rightIcon,
      fullWidth = false,
      disabled,
      ...props
    },
    ref
  ) => {
    const [isFocused, setIsFocused] = useState(false);

    const baseStyles =
      'h-11 w-full rounded-lg border bg-white dark:bg-neutral-800 px-4 py-2 text-base ' +
      'transition-all duration-normal placeholder:text-neutral-400 dark:placeholder:text-neutral-500 ' +
      'focus:outline-none focus:ring-2 disabled:cursor-not-allowed disabled:opacity-50';

    const stateStyles = error
      ? 'border-danger-500 focus:border-danger-500 focus:ring-danger-500/20'
      : 'border-neutral-300 dark:border-neutral-600 focus:border-primary-500 focus:ring-primary-500/20';

    const iconPadding = cn(leftIcon && 'pl-11', rightIcon && 'pr-11');

    return (
      <div className={cn('space-y-2', fullWidth && 'w-full')}>
        {label && (
          <label
            className={cn(
              'block text-sm font-medium transition-colors',
              error
                ? 'text-danger-600 dark:text-danger-400'
                : 'text-neutral-700 dark:text-neutral-300'
            )}
          >
            {label}
            {props.required && <span className="ml-1 text-danger-500">*</span>}
          </label>
        )}

        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400 dark:text-neutral-500">
              {leftIcon}
            </div>
          )}

          <input
            ref={ref}
            type={type}
            className={cn(baseStyles, stateStyles, iconPadding, className)}
            disabled={disabled}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            {...props}
          />

          {rightIcon && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 dark:text-neutral-500">
              {rightIcon}
            </div>
          )}
        </div>

        {(error || helperText) && (
          <p
            className={cn(
              'text-sm',
              error
                ? 'text-danger-600 dark:text-danger-400'
                : 'text-neutral-600 dark:text-neutral-400'
            )}
          >
            {error || helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
