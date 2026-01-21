// =============================================================================
// QuickLinkCard Molecule
// Emergency hotline or resource link card
// =============================================================================

import { cn } from '../../../lib/utils';
import { Icon, type IconName } from '../../atoms/Icon/Icon';
import type { QuickLink } from '../../../types';

export interface QuickLinkCardProps {
    link: QuickLink;
    className?: string;
}

// Map string icon names to Lucide icon names
const iconMap: Record<string, IconName> = {
    'Phone': 'Phone',
    'Shield': 'Shield',
    'Scale': 'Scale',
    'Heart': 'Heart',
    'FileText': 'FileText',
    'HeartHandshake': 'HeartHandshake',
    'BookOpen': 'BookOpen',
    'HelpCircle': 'HelpCircle',
};

export function QuickLinkCard({ link, className }: QuickLinkCardProps) {
    const iconName = iconMap[link.icon] || 'ExternalLink';
    const isExternal = link.href.startsWith('http') || link.href.startsWith('tel:');

    return (
        <a
            href={link.href}
            target={isExternal ? '_blank' : undefined}
            rel={isExternal ? 'noopener noreferrer' : undefined}
            className={cn(
                'group flex items-start gap-3 p-3 rounded-lg',
                'bg-card/50 border border-border',
                'hover:bg-accent/80 hover:border-accent',
                'transition-all duration-300 ease-out',
                'active:scale-[0.98]',
                className
            )}
        >
            {/* Icon */}
            <div className={cn(
                'flex items-center justify-center w-9 h-9 rounded-lg flex-shrink-0',
                'bg-secondary group-hover:bg-accent',
                'transition-colors duration-300',
                link.type === 'hotline' && 'text-red-400',
                link.type === 'resource' && 'text-blue-400',
                link.type === 'finder' && 'text-green-400',
            )}>
                <Icon name={iconName} size="sm" />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                    <span className="font-medium text-sm text-foreground group-hover:text-foreground/90 truncate">
                        {link.label}
                    </span>
                    {isExternal && (
                        <Icon
                            name="ExternalLink"
                            size="xs"
                            className="text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity"
                        />
                    )}
                </div>
                <p className="text-xs text-muted-foreground truncate mt-0.5">
                    {link.description}
                </p>
            </div>
        </a>
    );
}

export default QuickLinkCard;
