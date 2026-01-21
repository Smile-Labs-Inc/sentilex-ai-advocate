// =============================================================================
// LawsSection Organism
// Display identified laws applicable to the case
// =============================================================================

import { cn } from '../../../lib/utils';
import { Card, CardHeader, CardTitle } from '../../atoms/Card/Card';
import { Badge } from '../../atoms/Badge/Badge';
import { Icon } from '../../atoms/Icon/Icon';

export interface IdentifiedLaw {
    id: string;
    name: string;
    section: string;
    description: string;
    relevance: 'high' | 'medium' | 'low';
    jurisdiction: string;
}

export interface LawsSectionProps {
    laws: IdentifiedLaw[];
    className?: string;
}

const relevanceConfig = {
    high: { label: 'Highly Relevant', color: 'bg-green-500/10 text-green-400 border-green-500/20' },
    medium: { label: 'Relevant', color: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' },
    low: { label: 'May Apply', color: 'bg-secondary text-muted-foreground border-border' },
};

export function LawsSection({ laws, className }: LawsSectionProps) {
    return (
        <Card variant="default" padding="lg" className={cn('animate-slide-up', className)}>
            <CardHeader>
                <div className="flex items-center gap-2">
                    <Icon name="Scale" size="sm" className="text-purple-400" />
                    <CardTitle className="text-sm">Identified Laws</CardTitle>
                </div>
                <Badge variant="outline" className="text-xs">
                    {laws.length} found
                </Badge>
            </CardHeader>

            {laws.length === 0 ? (
                <div className="text-center py-8">
                    <Icon name="Scale" size="lg" className="text-muted-foreground/50 mx-auto mb-3" />
                    <p className="text-sm text-muted-foreground">
                        No laws identified yet
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                        The AI will analyze your case and identify applicable laws
                    </p>
                </div>
            ) : (
                <div className="space-y-3">
                    {laws.map((law) => {
                        const relevance = relevanceConfig[law.relevance];
                        return (
                            <div
                                key={law.id}
                                className="p-4 bg-secondary/30 rounded-lg border border-border hover:border-input transition-colors"
                            >
                                <div className="flex items-start justify-between gap-3 mb-2">
                                    <div>
                                        <h4 className="text-sm font-medium text-foreground">
                                            {law.name}
                                        </h4>
                                        <p className="text-xs text-muted-foreground">
                                            {law.section} • {law.jurisdiction}
                                        </p>
                                    </div>
                                    <span className={cn(
                                        'text-[10px] px-2 py-0.5 rounded border',
                                        relevance.color
                                    )}>
                                        {relevance.label}
                                    </span>
                                </div>
                                <p className="text-xs text-muted-foreground leading-relaxed">
                                    {law.description}
                                </p>
                            </div>
                        );
                    })}
                </div>
            )}
        </Card>
    );
}

export default LawsSection;
