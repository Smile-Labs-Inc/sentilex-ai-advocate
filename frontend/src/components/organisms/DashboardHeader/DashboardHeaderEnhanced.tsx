// =============================================================================
// Enhanced DashboardHeader Organism
// Welcome message, professional notification bell, and primary action button
// =============================================================================

import { cn } from '../../../lib/utils';
import { Button } from '../../atoms/Button/Button';
import { Icon } from '../../atoms/Icon/Icon';
import { NotificationBell } from '../../molecules/NotificationBell/NotificationBell';
import type { UserProfile, Notification } from '../../../types';

export interface DashboardHeaderProps {
    user: UserProfile;
    notifications?: Notification[];
    onNewIncident?: () => void;
    onOpenActivity?: () => void;
    onMarkNotificationAsRead?: (id: string) => void;
    onMarkAllNotificationsAsRead?: () => void;
    onViewAllNotifications?: () => void;
    className?: string;
}

export function DashboardHeader({
    user,
    notifications = [],
    onNewIncident,
    onOpenActivity,
    onMarkNotificationAsRead = () => { },
    onMarkAllNotificationsAsRead = () => { },
    onViewAllNotifications = () => { },
    className
}: DashboardHeaderProps) {
    const greeting = getGreeting();

    return (
        <header className={cn('flex justify-between items-start mb-8', className)}>
            {/* Left side - Welcome message */}
            <div className="animate-fade-in">
                <div className="uppercase text-xs font-bold tracking-wider text-muted-foreground mb-1">
                    Dashboard
                </div>
                <h1 className="text-2xl text-foreground font-medium mb-1">
                    {`${greeting}, ${user.first_name} 👋`}
                </h1>
                <p className="text-muted-foreground text-sm">
                    Let's protect your digital rights today.
                </p>
            </div>

            {/* Right side - Actions */}
            <div className="flex items-center gap-4 animate-fade-in" style={{ animationDelay: '0.1s' }}>
                {/* Recent Activity Button */}
                <button
                    onClick={() => onOpenActivity?.()}
                    className="w-9 h-9 flex items-center justify-center rounded-lg bg-secondary hover:bg-accent transition-colors"
                    aria-label="Open recent activity"
                >
                    <Icon name="Activity" size="sm" className="text-foreground" />
                </button>

                {/* Professional Notification Bell */}
                <NotificationBell
                    notifications={notifications}
                    onMarkAsRead={onMarkNotificationAsRead}
                    onMarkAllAsRead={onMarkAllNotificationsAsRead}
                    onViewAll={onViewAllNotifications}
                />

                {/* Primary action */}
                <Button onClick={onNewIncident} className="gap-2">
                    <Icon name="Plus" size="sm" />
                    NEW INCIDENT
                </Button>
            </div>
        </header>
    );
}

// Get appropriate greeting based on time of day
function getGreeting(): string {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
}

export default DashboardHeader;