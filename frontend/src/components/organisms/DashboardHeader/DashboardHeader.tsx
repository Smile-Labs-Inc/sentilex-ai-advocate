// =============================================================================
// DashboardHeader Organism
// Welcome message, notifications, and primary action button
// =============================================================================

import { cn } from '../../../lib/utils';
import { Button } from '../../atoms/Button/Button';
import { Avatar } from '../../atoms/Avatar/Avatar';
import { Icon } from '../../atoms/Icon/Icon';
import type { User } from '../../../types';

export interface DashboardHeaderProps {
    user: User;
    onNewIncident?: () => void;
    className?: string;
}

export function DashboardHeader({ user, onNewIncident, className }: DashboardHeaderProps) {
    const isNewUser = user.isNewUser;
    const greeting = getGreeting();

    return (
        <header className={cn('flex justify-between items-start mb-8', className)}>
            {/* Left side - Welcome message */}
            <div className="animate-fade-in">
                <div className="uppercase text-xs font-bold tracking-wider text-muted-foreground mb-1">
                    Dashboard
                </div>
                <h1 className="text-2xl text-foreground font-medium mb-1">
                    {isNewUser
                        ? `Welcome to Veritas Protocol 👋`
                        : `${greeting}, ${user.name.split(' ')[0]} 👋`
                    }
                </h1>
                <p className="text-muted-foreground text-sm">
                    {isNewUser
                        ? 'Your AI-powered ally for cybercrime legal support'
                        : "Let's protect your digital rights today."
                    }
                </p>
            </div>

            {/* Right side - Actions */}
            <div className="flex items-center gap-4 animate-fade-in" style={{ animationDelay: '0.1s' }}>
                {/* Avatar stack (returning users only) */}
                {!isNewUser && (
                    <div className="flex -space-x-2">
                        {['User1', 'User2', 'User3'].map((name, i) => (
                            <div
                                key={i}
                                className="relative"
                                style={{ zIndex: 3 - i }}
                            >
                                <Avatar
                                    name={name}
                                    size="sm"
                                    className="border-2 border-background"
                                />
                            </div>
                        ))}
                        <div className="w-8 h-8 rounded-full border-2 border-background bg-secondary text-xs flex items-center justify-center text-foreground font-medium">
                            5+
                        </div>
                    </div>
                )}

                {/* Notifications */}
                <button className="relative w-9 h-9 flex items-center justify-center rounded-lg bg-secondary hover:bg-accent transition-colors">
                    <Icon name="Bell" size="sm" className="text-muted-foreground" />
                    <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
                </button>

                {/* Primary action */}
                <Button onClick={onNewIncident} className="gap-2">
                    <Icon name="Plus" size="sm" />
                    {isNewUser ? 'START NEW INCIDENT' : 'NEW INCIDENT'}
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
