// =============================================================================
// QuickActionsGrid Organism
// Grid of AI-powered quick action buttons
// =============================================================================

import { cn } from '../../../lib/utils';
import { Card, CardHeader, CardTitle } from '../../atoms/Card/Card';
import { Icon, type IconName } from '../../atoms/Icon/Icon';

interface QuickAction {
    id: string;
    label: string;
    sublabel?: string;
    icon: IconName;
    onClick?: () => void;
}

export interface QuickActionsGridProps {
    onAction?: (actionId: string) => void;
    className?: string;
}

const quickActions: QuickAction[] = [
    {
        id: 'new-incident',
        label: 'Report New',
        sublabel: 'Incident',
        icon: 'FileWarning',
    },
    {
        id: 'upload-evidence',
        label: 'Upload',
        sublabel: 'Evidence',
        icon: 'Upload',
    },
    {
        id: 'find-lawyer',
        label: 'Find',
        sublabel: 'Lawyer',
        icon: 'Scale',
    },
    {
        id: 'ai-chat',
        label: 'Ask AI',
        sublabel: 'Assistant',
        icon: 'Sparkles',
    },
];

export function QuickActionsGrid({ onAction, className }: QuickActionsGridProps) {
    return (
        <Card variant="default" padding="lg" className={cn('animate-slide-up', className)}>
            <CardHeader>
                <div className="flex items-center gap-2">
                    <Icon name="Sparkles" size="sm" className="text-muted-foreground" />
                    <CardTitle className="text-sm">Quick Actions</CardTitle>
                </div>
            </CardHeader>

            <div className="grid grid-cols-2 gap-2">
                {quickActions.map((action) => (
                    <button
                        key={action.id}
                        onClick={() => onAction?.(action.id)}
                        className={cn(
                            'flex flex-col items-center justify-center gap-2 p-4 rounded-lg',
                            'bg-card/50 border border-border',
                            'hover:bg-accent/80 hover:border-accent',
                            'active:scale-[0.98]',
                            'transition-all duration-200 ease-out',
                            'group'
                        )}
                    >
                        <Icon
                            name={action.icon}
                            size="md"
                            className="text-muted-foreground group-hover:text-foreground transition-colors"
                        />
                        <div className="text-center">
                            <span className="text-[10px] leading-tight text-muted-foreground group-hover:text-foreground transition-colors">
                                {action.label}
                                {action.sublabel && (
                                    <>
                                        <br />
                                        {action.sublabel}
                                    </>
                                )}
                            </span>
                        </div>
                    </button>
                ))}
            </div>
        </Card>
    );
}

export default QuickActionsGrid;
