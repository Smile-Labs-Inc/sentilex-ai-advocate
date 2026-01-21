// =============================================================================
// NavItem Molecule
// Single navigation item for sidebar
// =============================================================================

import { cn } from '../../../lib/utils';
import { Icon, type IconName } from '../../atoms/Icon/Icon';
import type { NavItem as NavItemType } from '../../../types';

export interface NavItemProps {
    item: NavItemType;
    isActive?: boolean;
    onClick?: (item: NavItemType) => void;
    className?: string;
}

export function NavItem({ item, isActive, onClick, className }: NavItemProps) {
    return (
        <a
            href={item.href}
            onClick={(e) => {
                e.preventDefault();
                onClick?.(item);
            }}
            className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg',
                'text-sm font-medium',
                'transition-all duration-200 ease-out',
                isActive
                    ? 'bg-secondary text-foreground border border-border'
                    : 'text-muted-foreground hover:text-foreground hover:bg-secondary/50',
                className
            )}
        >
            <Icon name={item.icon as IconName} size="sm" />
            <span>{item.label}</span>
        </a>
    );
}

export default NavItem;
