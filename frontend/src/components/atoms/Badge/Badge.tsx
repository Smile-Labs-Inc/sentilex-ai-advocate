// =============================================================================
// Badge Atom
// Status badges for incidents and other labeled states
// =============================================================================

import { cn } from '../../../lib/utils';
import type { JSX } from 'preact';
import type { IncidentStatus } from '../../../types';

export interface BadgeProps extends JSX.HTMLAttributes<HTMLSpanElement> {
    variant?: 'default' | 'pending' | 'progress' | 'resolved' | 'submitted' | 'outline';
    size?: 'sm' | 'md';
    children: preact.ComponentChildren;
}

const variantStyles = {
    default: 'bg-secondary text-secondary-foreground',
    pending: 'bg-yellow-500/10 text-yellow-500',
    progress: 'bg-blue-500/10 text-blue-500',
    resolved: 'bg-green-500/10 text-green-500',
    submitted: 'bg-purple-500/10 text-purple-500',
    outline: 'bg-transparent border border-border text-muted-foreground',
};

const sizeStyles = {
    sm: 'px-2 py-0.5 text-[10px]',
    md: 'px-2.5 py-1 text-xs',
};

// Map incident status to badge variant
export function getStatusVariant(status: IncidentStatus): BadgeProps['variant'] {
    const map: Record<IncidentStatus, BadgeProps['variant']> = {
        'pending': 'pending',
        'in-progress': 'progress',
        'resolved': 'resolved',
        'submitted-to-police': 'submitted',
    };
    return map[status] || 'default';
}

// Get display label for status
export function getStatusLabel(status: IncidentStatus): string {
    const map: Record<IncidentStatus, string> = {
        'pending': 'Pending',
        'in-progress': 'In Progress',
        'resolved': 'Resolved',
        'submitted-to-police': 'Submitted',
    };
    return map[status] || status;
}

export function Badge({
    variant = 'default',
    size = 'md',
    className,
    children,
    ...props
}: BadgeProps) {
    return (
        <span
            className={cn(
                'inline-flex items-center gap-1.5 font-medium rounded-full',
                'transition-colors duration-200',
                variantStyles[variant],
                sizeStyles[size],
                className
            )}
            {...props}
        >
            {children}
        </span>
    );
}

export default Badge;
