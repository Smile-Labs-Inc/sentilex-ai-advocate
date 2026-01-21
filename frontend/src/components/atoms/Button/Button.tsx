// =============================================================================
// Button Atom
// Primary, Secondary, Ghost, and Outline variants with Apple-like animations
// =============================================================================

import { cn } from '../../../lib/utils';
import type { JSX } from 'preact';

export interface ButtonProps extends JSX.HTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'ghost' | 'outline' | 'destructive';
    size?: 'sm' | 'md' | 'lg' | 'icon';
    isLoading?: boolean;
    disabled?: boolean;
    children: preact.ComponentChildren;
}

const variantStyles = {
    primary: `
    bg-primary text-primary-foreground 
    hover:bg-primary/90 
    active:bg-primary/80 
    active:scale-[0.98]
  `,
    secondary: `
    bg-secondary text-secondary-foreground 
    border border-border 
    hover:bg-accent hover:border-accent
    active:bg-accent/80 
    active:scale-[0.98]
  `,
    ghost: `
    bg-transparent text-muted-foreground 
    hover:text-foreground hover:bg-secondary
    active:bg-accent
  `,
    outline: `
    bg-transparent text-foreground 
    border border-border 
    hover:bg-secondary hover:border-accent
    active:bg-accent
  `,
    destructive: `
    bg-destructive text-destructive-foreground 
    hover:bg-destructive/90 
    active:bg-destructive/80 
    active:scale-[0.98]
  `,
};

const sizeStyles = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
    icon: 'p-2 w-9 h-9',
};

export function Button({
    variant = 'primary',
    size = 'md',
    isLoading = false,
    className,
    disabled,
    children,
    ...props
}: ButtonProps) {
    return (
        <button
            className={cn(
                // Base styles
                'inline-flex items-center justify-center gap-2',
                'font-medium rounded-lg',
                'transition-all duration-200 ease-out',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/20',
                'disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
                // Variant styles
                variantStyles[variant],
                // Size styles
                sizeStyles[size],
                className
            )}
            disabled={disabled || isLoading}
            {...props}
        >
            {isLoading ? (
                <>
                    <svg
                        className="animate-spin h-4 w-4"
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
                        />
                        <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        />
                    </svg>
                    <span>Loading...</span>
                </>
            ) : (
                children
            )}
        </button>
    );
}

export default Button;
