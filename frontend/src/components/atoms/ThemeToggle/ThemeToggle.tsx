// =============================================================================
// ThemeToggle Atom
// Toggle button for switching between light and dark themes
// =============================================================================

import { cn } from '../../../lib/utils';
import { Icon } from '../Icon/Icon';
import type { ResolvedTheme } from '../../../hooks/useTheme';

export interface ThemeToggleProps {
    /** Current resolved theme */
    theme: ResolvedTheme;
    /** Callback when toggle is clicked */
    onToggle: () => void;
    /** Optional size variant */
    size?: 'sm' | 'md' | 'lg';
    /** Optional additional classes */
    className?: string;
    /** Show label next to icon */
    showLabel?: boolean;
}

const sizeStyles = {
    sm: 'w-8 h-8',
    md: 'w-9 h-9',
    lg: 'w-10 h-10',
};

const iconSizes = {
    sm: 'sm' as const,
    md: 'sm' as const,
    lg: 'md' as const,
};

export function ThemeToggle({
    theme,
    onToggle,
    size = 'md',
    className,
    showLabel = false,
}: ThemeToggleProps) {
    const isDark = theme === 'dark';

    return (
        <button
            type="button"
            onClick={onToggle}
            className={cn(
                // Base styles
                'relative flex items-center justify-center gap-2 rounded-lg',
                'transition-all duration-300 ease-out',
                // Theme-aware colors
                'bg-secondary hover:bg-accent',
                'text-muted-foreground hover:text-foreground',
                // Focus state
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
                'focus-visible:ring-offset-background',
                // Size (when no label)
                !showLabel && sizeStyles[size],
                // With label padding
                showLabel && 'px-3 py-2',
                className
            )}
            aria-label={`Switch to ${isDark ? 'light' : 'dark'} theme`}
            title={`Switch to ${isDark ? 'light' : 'dark'} theme`}
        >
            {/* Icon container with rotation animation */}
            <div className="relative">
                {/* Sun icon - visible in dark mode (to switch to light) */}
                <Icon
                    name="Sun"
                    size={iconSizes[size]}
                    className={cn(
                        'transition-all duration-300',
                        isDark
                            ? 'rotate-0 scale-100 opacity-100'
                            : 'rotate-90 scale-0 opacity-0 absolute inset-0'
                    )}
                />
                {/* Moon icon - visible in light mode (to switch to dark) */}
                <Icon
                    name="Moon"
                    size={iconSizes[size]}
                    className={cn(
                        'transition-all duration-300',
                        isDark
                            ? '-rotate-90 scale-0 opacity-0 absolute inset-0'
                            : 'rotate-0 scale-100 opacity-100'
                    )}
                />
            </div>

            {/* Optional label */}
            {showLabel && (
                <span className="text-sm font-medium">
                    {isDark ? 'Light' : 'Dark'}
                </span>
            )}
        </button>
    );
}

export default ThemeToggle;
