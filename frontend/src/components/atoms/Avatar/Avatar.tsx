// =============================================================================
// Avatar Atom
// User avatar with image or initials fallback
// =============================================================================

import { cn } from '../../../lib/utils';
import type { JSX } from 'preact';

export interface AvatarProps extends JSX.HTMLAttributes<HTMLDivElement> {
    src?: string;
    alt?: string;
    name?: string;
    size?: 'sm' | 'md' | 'lg';
}

const sizeStyles = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
};

// Generate initials from name
function getInitials(name: string): string {
    return name
        .split(' ')
        .map(word => word[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
}

// Generate consistent color based on name
function getColorFromName(name: string): string {
    const colors = [
        'bg-blue-600',
        'bg-green-600',
        'bg-purple-600',
        'bg-orange-600',
        'bg-pink-600',
        'bg-cyan-600',
        'bg-indigo-600',
    ];

    let hash = 0;
    for (let i = 0; i < name.length; i++) {
        hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }

    return colors[Math.abs(hash) % colors.length];
}

export function Avatar({
    src,
    alt,
    name = 'User',
    size = 'md',
    className,
    ...props
}: AvatarProps) {
    const initials = getInitials(name);
    const bgColor = getColorFromName(name);

    return (
        <div
            className={cn(
                'relative rounded-full overflow-hidden flex-shrink-0',
                'flex items-center justify-center',
                'font-medium text-white',
                sizeStyles[size],
                !src && bgColor,
                className
            )}
            {...props}
        >
            {src ? (
                <img
                    src={src}
                    alt={alt || name}
                    className="w-full h-full object-cover"
                    loading="lazy"
                />
            ) : (
                <span className="select-none">{initials}</span>
            )}
        </div>
    );
}

export default Avatar;
