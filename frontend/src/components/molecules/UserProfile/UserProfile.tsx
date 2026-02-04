// =============================================================================
// UserProfile Molecule
// Compact user profile display for sidebar with logout and settings
// =============================================================================

import { useState } from 'preact/hooks';
import { route } from 'preact-router';
import { cn } from '../../../lib/utils';
import { Avatar } from '../../atoms/Avatar/Avatar';
import { Icon } from '../../atoms/Icon/Icon';
import { Button } from '../../atoms/Button/Button';
import { useAuth } from '../../../hooks/useAuth';
import type { UserProfile as AuthUserProfile } from '../../../types/auth';

export interface UserProfileProps {
    user: AuthUserProfile;
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
    const { logout } = useAuth();
    const [showMenu, setShowMenu] = useState(false);
    const [isLoggingOut, setIsLoggingOut] = useState(false);

    const handleLogout = async () => {
        setIsLoggingOut(true);
        try {
            await logout();
        } catch (error) {
            console.error('Logout failed:', error);
        } finally {
            setIsLoggingOut(false);
            setShowMenu(false);
        }
    };

    const handleSettingsClick = () => {
        setShowMenu(false);
        route('/settings');
    };

    const displayName = `${user.first_name} ${user.last_name}`;
    const avatarName = `${user.first_name} ${user.last_name}`;

    return (
        <div className="relative">
            <button
                onClick={() => setShowMenu(!showMenu)}
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
                    name={avatarName}
                    size={variant === 'expanded' ? 'md' : 'sm'}
                />

                <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-foreground truncate">
                        {displayName}
                    </p>
                    {variant === 'expanded' && user.email && (
                        <p className="text-[10px] text-muted-foreground truncate">
                            {user.email}
                        </p>
                    )}
                </div>

                <Icon
                    name="ChevronDown"
                    size="sm"
                    className={cn(
                        "text-muted-foreground group-hover:text-foreground/70 transition-all",
                        showMenu && "rotate-180"
                    )}
                />
            </button>

            {showMenu && (
                <>
                    <div
                        className="fixed inset-0 z-10"
                        onClick={() => setShowMenu(false)}
                    />
                    <div className="absolute bottom-full left-0 right-0 mb-2 z-20 bg-card border border-border rounded-lg shadow-lg overflow-hidden">
                        <div className="p-2 space-y-1">
                            <Button
                                variant="ghost"
                                size="sm"
                                className="w-full justify-start"
                                onClick={handleSettingsClick}
                            >
                                <Icon name="Settings" size="sm" className="mr-2" />
                                Settings
                            </Button>
                            <Button
                                variant="ghost"
                                size="sm"
                                className="w-full justify-start"
                                onClick={handleLogout}
                                isLoading={isLoggingOut}
                                disabled={isLoggingOut}
                            >
                                <Icon name="LogOut" size="sm" className="mr-2" />
                                {isLoggingOut ? 'Logging out...' : 'Logout'}
                            </Button>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}

export default UserProfile;
