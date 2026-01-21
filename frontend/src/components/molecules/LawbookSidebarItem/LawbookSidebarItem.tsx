
import { cn } from '../../../lib/utils';
import { Icon } from '../../atoms/Icon/Icon';
import type { LawbookChapter } from '../../../types';
import type { IconName } from '../../atoms/Icon/Icon';

export interface LawbookSidebarItemProps {
    chapter: LawbookChapter;
    isActive?: boolean;
    onClick?: () => void;
    className?: string;
}

export function LawbookSidebarItem({ chapter, isActive, onClick, className }: LawbookSidebarItemProps) {
    return (
        <button
            onClick={onClick}
            className={cn(
                'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200',
                'hover:bg-accent/50 group',
                isActive
                    ? 'bg-accent/80 text-foreground font-medium'
                    : 'text-muted-foreground',
                className
            )}
        >
            <div className={cn(
                'flex items-center justify-center w-8 h-8 rounded-md transition-colors',
                isActive
                    ? 'bg-primary/10 text-primary'
                    : 'bg-muted text-muted-foreground group-hover:text-foreground'
            )}>
                <Icon name={(chapter.icon as IconName) || 'BookOpen'} size="sm" />
            </div>

            <div className="flex-1 text-left line-clamp-1">
                {chapter.title}
            </div>

            <Icon
                name="ChevronRight"
                size="xs"
                className={cn(
                    'transition-transform duration-200 opacity-0 group-hover:opacity-100',
                    isActive && 'opacity-100'
                )}
            />
        </button>
    );
}
