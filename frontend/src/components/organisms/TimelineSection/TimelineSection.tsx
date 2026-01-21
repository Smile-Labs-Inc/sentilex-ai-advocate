// =============================================================================
// TimelineSection Organism
// Case timeline showing events and updates
// =============================================================================

import { cn } from '../../../lib/utils';
import { Card, CardHeader, CardTitle } from '../../atoms/Card/Card';
import { Icon, type IconName } from '../../atoms/Icon/Icon';

export interface TimelineEvent {
    id: string;
    type: 'created' | 'updated' | 'law-identified' | 'evidence-added' | 'ai-analysis' | 'status-change';
    title: string;
    description?: string;
    timestamp: Date;
}

export interface TimelineSectionProps {
    events: TimelineEvent[];
    className?: string;
}

const eventConfig: Record<TimelineEvent['type'], { icon: IconName; color: string }> = {
    'created': { icon: 'FolderPlus', color: 'text-green-400' },
    'updated': { icon: 'RefreshCw', color: 'text-muted-foreground' },
    'law-identified': { icon: 'Scale', color: 'text-purple-400' },
    'evidence-added': { icon: 'Upload', color: 'text-blue-400' },
    'ai-analysis': { icon: 'Sparkles', color: 'text-yellow-400' },
    'status-change': { icon: 'ArrowRight', color: 'text-orange-400' },
};

function formatDate(date: Date): string {
    return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    }).format(date);
}

export function TimelineSection({ events, className }: TimelineSectionProps) {
    return (
        <Card variant="default" padding="lg" className={cn('animate-slide-up', className)}>
            <CardHeader>
                <div className="flex items-center gap-2">
                    <Icon name="Clock" size="sm" className="text-muted-foreground" />
                    <CardTitle className="text-sm">Case Timeline</CardTitle>
                </div>
            </CardHeader>

            <div className="space-y-0">
                {events.map((event, index) => {
                    const config = eventConfig[event.type];
                    const isLast = index === events.length - 1;

                    return (
                        <div key={event.id} className="relative pl-6">
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
                                <div className="flex items-center justify-between">
                                    <p className="text-sm font-medium text-foreground">
                                        {event.title}
                                    </p>
                                    <span className="text-xs text-muted-foreground">
                                        {formatDate(event.timestamp)}
                                    </span>
                                </div>
                                {event.description && (
                                    <p className="text-xs text-muted-foreground mt-1">
                                        {event.description}
                                    </p>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </Card>
    );
}

export default TimelineSection;
