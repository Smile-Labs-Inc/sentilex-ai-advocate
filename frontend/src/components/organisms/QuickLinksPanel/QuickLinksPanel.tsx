// =============================================================================
// QuickLinksPanel Organism
// Grid of quick access links for emergency resources
// =============================================================================

import { cn } from '../../../lib/utils';
import { Card, CardHeader, CardTitle } from '../../atoms/Card/Card';
import { Icon } from '../../atoms/Icon/Icon';
import { QuickLinkCard } from '../../molecules/QuickLinkCard/QuickLinkCard';
import type { QuickLink } from '../../../types';

export interface QuickLinksPanelProps {
    links: QuickLink[];
    className?: string;
}

export function QuickLinksPanel({ links, className }: QuickLinksPanelProps) {
    return (
        <Card variant="default" padding="lg" className={cn('animate-slide-up', className)}>
            <CardHeader>
                <div className="flex items-center gap-2">
                    <Icon name="LifeBuoy" size="sm" className="text-muted-foreground" />
                    <CardTitle className="text-sm">Quick Access</CardTitle>
                </div>
            </CardHeader>

            <div className="space-y-2">
                {links.map((link) => (
                    <QuickLinkCard key={link.id} link={link} />
                ))}
            </div>
        </Card>
    );
}

export default QuickLinksPanel;
