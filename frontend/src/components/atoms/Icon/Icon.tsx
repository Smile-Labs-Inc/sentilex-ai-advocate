// =============================================================================
// Icon Atom
// Wrapper for Lucide icons with consistent sizing
// =============================================================================

import { cn } from '../../../lib/utils';
import * as LucideIcons from 'lucide-preact';
import type { JSX } from 'preact';

// Get available icon names
export type IconName = keyof typeof LucideIcons;

export interface IconProps extends JSX.HTMLAttributes<SVGSVGElement> {
    name: IconName;
    size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
    strokeWidth?: number;
}

const sizeMap = {
    xs: 12,
    sm: 16,
    md: 20,
    lg: 24,
    xl: 32,
};

export function Icon({
    name,
    size = 'md',
    strokeWidth = 2,
    className,
    ...props
}: IconProps) {
    const LucideIcon = LucideIcons[name] as any;

    if (!LucideIcon) {
        console.warn(`Icon "${name}" not found in lucide-preact`);
        return null;
    }

    return (
        <LucideIcon
            size={sizeMap[size]}
            strokeWidth={strokeWidth}
            className={cn('flex-shrink-0', className)}
            {...props}
        />
    );
}

export default Icon;
