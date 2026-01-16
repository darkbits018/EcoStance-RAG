import React from 'react';
import { cn } from '../../lib/utils';
import { Icons } from '../icons';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  isLoading?: boolean;
  variant?: 'primary' | 'outline' | 'ghost' | 'destructive' | 'default'; // Added variants
  size?: 'sm' | 'md' | 'lg' | 'icon';
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, children, isLoading, variant = 'primary', size = 'md', ...props }, ref) => {
    const baseStyles = `
      inline-flex items-center justify-center
      font-medium rounded-md
      transition-colors duration-200 ease-in-out
      focus:outline-none focus:ring-2 focus:ring-offset-2
      disabled:opacity-50 disabled:cursor-not-allowed
    `;

    const sizeStyles = {
      sm: 'h-8 px-3 text-sm',
      md: 'h-10 px-5',
      lg: 'h-12 px-6 text-lg',
      icon: 'h-10 w-10 p-0',
    };

    const variantStyles = {
      primary: `
        bg-primary text-white hover:bg-primary/90 focus:ring-primary
      `,
      default: `
        bg-primary text-white hover:bg-primary/90 focus:ring-primary
      `,
      outline: `
        bg-transparent text-primary border border-primary hover:bg-primary/10 focus:ring-primary
      `,
      ghost: `
        bg-transparent text-text-secondary hover:bg-surface-hover hover:text-text focus:ring-border
      `,
      destructive: `
        bg-red-600 text-white hover:bg-red-700 focus:ring-red-500
      `,
    };

    return (
      <button
        className={cn(
          baseStyles,
          sizeStyles[size],
          variantStyles[variant],
          className
        )}
        ref={ref}
        disabled={isLoading}
        {...props}
      >
        {isLoading && <Icons.Spinner className="mr-2 h-4 w-4 animate-spin" />}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button };
