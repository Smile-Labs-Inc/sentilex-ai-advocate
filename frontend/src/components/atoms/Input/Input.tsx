// =============================================================================
// Input Atom
// Text input field with label and error state
// =============================================================================

import { cn } from '../../../lib/utils';
import type { JSX } from 'preact';

export interface InputProps extends Omit<JSX.HTMLAttributes<HTMLInputElement>, 'size'> {
    label?: string;
    error?: string;
    size?: 'sm' | 'md' | 'lg';
    placeholder?: string;
    type?: string;
    value?: string;
}

const sizeStyles = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2.5 text-sm',
    lg: 'px-4 py-3 text-base',
};

export function Input({
    label,
    error,
    size = 'md',
    className,
    id,
    ...props
}: InputProps) {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');

    return (
        <div className="space-y-1.5">
            {label && (
                <label
                    htmlFor={inputId}
                    className="block text-sm font-medium text-foreground/80"
                >
                    {label}
                </label>
            )}
            <input
                id={inputId}
                className={cn(
                    'w-full bg-secondary text-foreground rounded-lg',
                    'border border-border',
                    'focus:outline-none focus:border-ring focus:ring-1 focus:ring-ring',
                    'placeholder:text-muted-foreground',
                    'transition-all duration-200',
                    error && 'border-destructive focus:border-destructive focus:ring-destructive/20',
                    sizeStyles[size],
                    className
                )}
                {...props}
            />
            {error && (
                <p className="text-xs text-destructive">{error}</p>
            )}
        </div>
    );
}

export default Input;
