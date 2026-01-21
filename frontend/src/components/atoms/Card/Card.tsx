// =============================================================================
// Card Atom
// Base card container with hover effects
// =============================================================================

import { cn } from '../../../lib/utils';
import type { JSX } from 'preact';

export interface CardProps extends JSX.HTMLAttributes<HTMLDivElement> {
    variant?: 'default' | 'elevated' | 'interactive' | 'ghost';
    padding?: 'none' | 'sm' | 'md' | 'lg';
    children: preact.ComponentChildren;
}

const variantStyles = {
    default: `
    bg-card/50 border border-border
  `,
    elevated: `
    bg-card/80 border border-border
    shadow-lg shadow-black/10
  `,
    interactive: `
    bg-card/50 border border-border
    hover:border-accent hover:bg-card/80
    active:scale-[0.99]
    cursor-pointer
  `,
    ghost: `
    bg-transparent border-0
  `,
};

const paddingStyles = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
};

export function Card({
    variant = 'default',
    padding = 'md',
    className,
    children,
    ...props
}: CardProps) {
    return (
        <div
            className={cn(
                'rounded-xl',
                'transition-all duration-300 ease-out',
                variantStyles[variant],
                paddingStyles[padding],
                className
            )}
            {...props}
        >
            {children}
        </div>
    );
}

// Card Header subcomponent
export interface CardHeaderProps extends JSX.HTMLAttributes<HTMLDivElement> {
    children: preact.ComponentChildren;
}

export function CardHeader({ className, children, ...props }: CardHeaderProps) {
    return (
        <div
            className={cn('flex items-center justify-between mb-4', className)}
            {...props}
        >
            {children}
        </div>
    );
}

// Card Title subcomponent
export interface CardTitleProps extends JSX.HTMLAttributes<HTMLHeadingElement> {
    children: preact.ComponentChildren;
}

export function CardTitle({ className, children, ...props }: CardTitleProps) {
    return (
        <h3
            className={cn('text-lg font-medium text-foreground', className)}
            {...props}
        >
            {children}
        </h3>
    );
}

// Card Description subcomponent
export interface CardDescriptionProps extends JSX.HTMLAttributes<HTMLParagraphElement> {
    children: preact.ComponentChildren;
}

export function CardDescription({ className, children, ...props }: CardDescriptionProps) {
    return (
        <p
            className={cn('text-xs text-muted-foreground', className)}
            {...props}
        >
            {children}
        </p>
    );
}

// Card Content subcomponent
export interface CardContentProps extends JSX.HTMLAttributes<HTMLDivElement> {
    children: preact.ComponentChildren;
}

export function CardContent({ className, children, ...props }: CardContentProps) {
    return (
        <div className={cn('', className)} {...props}>
            {children}
        </div>
    );
}

export default Card;
