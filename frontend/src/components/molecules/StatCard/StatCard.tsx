// =============================================================================
// StatCard Molecule
// Displays a single statistic with icon, value, status, and label
// =============================================================================

import { cn } from '../../../lib/utils';
import { Card } from '../../atoms/Card/Card';
import { Icon, type IconName } from '../../atoms/Icon/Icon';
import { StatusDot } from '../../atoms/StatusDot/StatusDot';
import { useEffect, useState } from 'preact/hooks';

export interface StatCardProps {
    icon: IconName;
    label: string;
    value: number;
    status?: {
        type: 'pending' | 'progress' | 'resolved' | 'submitted' | 'active';
        label: string;
    };
    subtitle?: string;
    className?: string;
    animateValue?: boolean;
}

// Animate number counting up
function useAnimatedNumber(target: number, duration = 1000): number {
    const [current, setCurrent] = useState(0);

    useEffect(() => {
        const startTime = performance.now();
        const startValue = 0;

        function update(currentTime: number) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Ease out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            const value = Math.round(startValue + (target - startValue) * eased);

            setCurrent(value);

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }

        requestAnimationFrame(update);
    }, [target, duration]);

    return current;
}

// Format large numbers with K/M suffix
function formatNumber(num: number): string {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

export function StatCard({
    icon,
    label,
    value,
    status,
    subtitle,
    className,
    animateValue = true,
}: StatCardProps) {
    const displayValue = animateValue ? useAnimatedNumber(value, 800) : value;

    return (
        <Card
            variant="default"
            padding="lg"
            className={cn('animate-fade-in', className)}
        >
            {/* Header with icon and label */}
            <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-muted-foreground mb-3">
                <Icon name={icon} size="sm" />
                <span>{label}</span>
            </div>

            {/* Value with optional status */}
            <div className="flex items-baseline gap-3 mb-1">
                <span className="text-3xl font-light text-foreground tabular-nums">
                    {formatNumber(displayValue)}
                </span>

                {status && (
                    <span className={cn(
                        'inline-flex items-center gap-1.5 text-xs px-2 py-0.5 rounded',
                        status.type === 'pending' && 'bg-yellow-500/10 text-yellow-500',
                        status.type === 'progress' && 'bg-blue-500/10 text-blue-500',
                        status.type === 'resolved' && 'bg-green-500/10 text-green-500',
                        status.type === 'submitted' && 'bg-purple-500/10 text-purple-500',
                        status.type === 'active' && 'bg-green-500/10 text-green-500',
                    )}>
                        <StatusDot status={status.type} size="sm" pulse={status.type !== 'resolved'} />
                        {status.label}
                    </span>
                )}
            </div>

            {/* Subtitle */}
            {subtitle && (
                <p className="text-xs text-muted-foreground">{subtitle}</p>
            )}
        </Card>
    );
}

export default StatCard;
