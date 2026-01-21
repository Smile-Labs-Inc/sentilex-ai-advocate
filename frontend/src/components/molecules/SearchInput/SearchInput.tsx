// =============================================================================
// SearchInput Molecule
// Search field with icon and keyboard shortcut hint
// =============================================================================

import { cn } from '../../../lib/utils';
import { Icon } from '../../atoms/Icon/Icon';
import type { JSX } from 'preact';

export interface SearchInputProps extends Omit<JSX.HTMLAttributes<HTMLInputElement>, 'size'> {
    size?: 'sm' | 'md';
    showShortcut?: boolean;
    placeholder?: string;
    value?: string;
}

const sizeStyles = {
    sm: 'pl-8 pr-3 py-1.5 text-xs',
    md: 'pl-9 pr-12 py-2 text-sm',
};

export function SearchInput({
    size = 'md',
    showShortcut = true,
    className,
    placeholder = 'Search...',
    ...props
}: SearchInputProps) {
    return (
        <div className="relative">
            {/* Search icon */}
            <Icon
                name="Search"
                size={size === 'sm' ? 'xs' : 'sm'}
                className={cn(
                    'absolute text-muted-foreground',
                    size === 'sm' ? 'left-2.5 top-2' : 'left-3 top-2.5'
                )}
            />

            {/* Input */}
            <input
                type="text"
                placeholder={placeholder}
                className={cn(
                    'w-full bg-secondary text-foreground rounded-lg',
                    'border border-border',
                    'focus:outline-none focus:border-ring focus:ring-1 focus:ring-ring',
                    'placeholder:text-muted-foreground',
                    'transition-all duration-200',
                    sizeStyles[size],
                    className
                )}
                {...props}
            />

            {/* Keyboard shortcut */}
            {showShortcut && size === 'md' && (
                <span className="absolute right-3 top-2.5 text-xs text-muted-foreground pointer-events-none">
                    ⌘K
                </span>
            )}
        </div>
    );
}

export default SearchInput;
