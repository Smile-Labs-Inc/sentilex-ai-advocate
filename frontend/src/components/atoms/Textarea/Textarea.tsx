// =============================================================================
// Textarea Atom
// Multi-line text input with label and error state
// =============================================================================

import { cn } from '../../../lib/utils';
import type { JSX } from 'preact';

export interface TextareaProps extends JSX.HTMLAttributes<HTMLTextAreaElement> {
    label?: string;
    error?: string;
    rows?: number;
    placeholder?: string;
    value?: string;
}

export function Textarea({
    label,
    error,
    className,
    id,
    rows = 4,
    ...props
}: TextareaProps) {
    const textareaId = id || label?.toLowerCase().replace(/\s+/g, '-');

    return (
        <div className="space-y-1.5">
            {label && (
                <label
                    htmlFor={textareaId}
                    className="block text-sm font-medium text-foreground/80"
                >
                    {label}
                </label>
            )}
            <textarea
                id={textareaId}
                rows={rows}
                className={cn(
                    'w-full bg-secondary text-foreground rounded-lg',
                    'border border-border',
                    'focus:outline-none focus:border-ring focus:ring-1 focus:ring-ring',
                    'placeholder:text-muted-foreground',
                    'transition-all duration-200',
                    'resize-none px-4 py-3 text-sm',
                    error && 'border-destructive focus:border-destructive focus:ring-destructive/20',
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

export default Textarea;
