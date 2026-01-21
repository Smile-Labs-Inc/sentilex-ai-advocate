// =============================================================================
// UserProfile Molecule
// Compact user profile display for sidebar
// =============================================================================

import { cn } from '../../../lib/utils';
import { Avatar } from '../../atoms/Avatar/Avatar';
import { Icon } from '../../atoms/Icon/Icon';
import type { User } from '../../../types';

export interface UserProfileProps {
    user: User;
    variant?: 'compact' | 'expanded';
    onClick?: () => void;
    className?: string;
}

export function UserProfile({
    user,
    variant = 'compact',
    onClick,
    className,
}: UserProfileProps) {
    return (
        <button
            onClick={onClick}
            className={cn(
                'flex items-center gap-3 w-full text-left',
                'p-2 rounded-lg',
                'hover:bg-secondary/50',
                'transition-colors duration-200',
                'group',
                className
            )}
        >
            <Avatar
                src={user.avatar}
                name={user.name}
                size={variant === 'expanded' ? 'md' : 'sm'}
            />

            <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-foreground truncate">
                    {user.name}
                </p>
                {variant === 'expanded' && (
                    <p className="text-[10px] text-muted-foreground truncate">
                        {user.email}
                    </p>
                )}
            </div>

            <Icon
                name="ChevronDown"
                size="sm"
                className="text-muted-foreground group-hover:text-foreground/70 transition-colors"
            />
        </button>
    );
}

export default UserProfile;
