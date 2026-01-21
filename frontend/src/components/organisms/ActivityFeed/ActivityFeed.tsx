// =============================================================================
// ActivityFeed Organism
// Timeline of recent activity
// =============================================================================

import { cn } from '../../../lib/utils';
import { Card, CardHeader, CardTitle } from '../../atoms/Card/Card';
import { Icon } from '../../atoms/Icon/Icon';
import { ActivityItem } from '../../molecules/ActivityItem/ActivityItem';
import type { ActivityItem as ActivityItemType } from '../../../types';

export interface ActivityFeedProps {
    activities: ActivityItemType[];
    className?: string;
}

export function ActivityFeed({ activities, className }: ActivityFeedProps) {
    // Empty state
    if (activities.length === 0) {
        return (
            <Card variant="default" padding="lg" className={cn('h-full', className)}>
                <CardHeader>
                    <div className="flex items-center gap-2">
                        <Icon name="Activity" size="sm" className="text-muted-foreground" />
                        <CardTitle className="text-sm">Recent Activity</CardTitle>
                    </div>
                </CardHeader>

                <div className="flex flex-col items-center justify-center py-8 text-center">
                    <Icon name="Inbox" size="lg" className="text-muted-foreground/50 mb-3" />
                    <p className="text-xs text-muted-foreground">No activity yet</p>
                </div>
            </Card>
        );
    }

    return (
        <Card variant="default" padding="lg" className={cn('h-full animate-slide-up', className)}>
            <CardHeader>
                <div className="flex items-center gap-2">
                    <Icon name="Activity" size="sm" className="text-muted-foreground" />
                    <CardTitle className="text-sm">Recent Activity</CardTitle>
                </div>
            </CardHeader>

            <div className="space-y-0">
                {activities.slice(0, 5).map((activity, index) => (
                    <ActivityItem
                        key={activity.id}
                        activity={activity}
                        isLast={index === Math.min(activities.length, 5) - 1}
                    />
                ))}
            </div>
        </Card>
    );
}

export default ActivityFeed;
