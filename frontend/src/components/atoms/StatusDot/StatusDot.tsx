// =============================================================================
// StatusDot Atom
// Animated status indicator dot
// =============================================================================

import { cn } from '../../../lib/utils';
import type { JSX } from 'preact';

export interface StatusDotProps extends JSX.HTMLAttributes<HTMLSpanElement> {
    status?: 'pending' | 'progress' | 'resolved' | 'submitted' | 'active' | 'inactive';
    size?: 'sm' | 'md';
    pulse?: boolean;
}

const statusColors = {
    pending: 'bg-yellow-500',
    progress: 'bg-blue-500',
    resolved: 'bg-green-500',
    submitted: 'bg-purple-500',
    active: 'bg-green-500',
    inactive: 'bg-muted-foreground',
};

const sizeStyles = {
    sm: 'w-1.5 h-1.5',
    md: 'w-2 h-2',
};

export function StatusDot({
    status = 'active',
    size = 'md',
    pulse = true,
    className,
    ...props
}: StatusDotProps) {
    return (
        <span
            className={cn('relative inline-flex', className)}
            {...props}
        >
            {/* Ping animation */}
            {pulse && (
                <span
                    className={cn(
                        'absolute inline-flex rounded-full opacity-75',
                        'animate-ping',
                        sizeStyles[size],
                        statusColors[status]
                    )}
                    style={{ animationDuration: '2s' }}
                />
            )}
            {/* Solid dot */}
            <span
                className={cn(
                    'relative inline-flex rounded-full',
                    sizeStyles[size],
                    statusColors[status]
                )}
            />
        </span>
    );
}

export default StatusDot;
