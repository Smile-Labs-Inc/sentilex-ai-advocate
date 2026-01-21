// =============================================================================
// ActivityItem Molecule
// Single activity in the timeline feed
// =============================================================================

import { cn } from '../../../lib/utils';
import { Icon, type IconName } from '../../atoms/Icon/Icon';
import type { ActivityItem as ActivityItemType, ActivityType } from '../../../types';
import { getRelativeTime } from '../../../data/mockData';

export interface ActivityItemProps {
    activity: ActivityItemType;
    isLast?: boolean;
    className?: string;
}

// Map activity type to icon and color
const activityConfig: Record<ActivityType, { icon: IconName; color: string }> = {
    'update': { icon: 'RefreshCw', color: 'text-muted-foreground' },
    'law-identified': { icon: 'Scale', color: 'text-purple-400' },
    'evidence-uploaded': { icon: 'Upload', color: 'text-blue-400' },
    'report-submitted': { icon: 'Send', color: 'text-green-400' },
    'case-opened': { icon: 'FolderPlus', color: 'text-yellow-400' },
    'case-resolved': { icon: 'CheckCircle', color: 'text-green-400' },
};

export function ActivityItem({ activity, isLast = false, className }: ActivityItemProps) {
    const config = activityConfig[activity.type] || activityConfig['update'];

    return (
        <div className={cn('relative pl-6', className)}>
            {/* Timeline line */}
            {!isLast && (
                <div className="absolute left-[7px] top-6 bottom-0 w-px bg-border" />
            )}

            {/* Icon dot */}
            <div className={cn(
                'absolute left-0 top-1 w-4 h-4 rounded-full flex items-center justify-center',
                'bg-background border border-border',
            )}>
                <Icon name={config.icon} size="xs" className={config.color} />
            </div>

            {/* Content */}
            <div className="pb-4">
                <p className="text-xs text-muted-foreground leading-relaxed">
                    {activity.message}{' '}
                    {activity.highlightText && (
                        <span className="text-foreground font-medium">{activity.highlightText}</span>
                    )}
                </p>
                <p className="text-[10px] text-muted-foreground/80 mt-1">
                    {getRelativeTime(activity.timestamp)}
                </p>
            </div>
        </div>
    );
}

export default ActivityItem;
