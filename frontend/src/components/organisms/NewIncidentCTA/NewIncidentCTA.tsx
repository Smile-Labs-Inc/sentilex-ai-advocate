// =============================================================================
// NewIncidentCTA Organism
// Prominent call-to-action for new users to start their first incident
// =============================================================================

import { cn } from '../../../lib/utils';
import { Button } from '../../atoms/Button/Button';
import { Icon } from '../../atoms/Icon/Icon';

export interface NewIncidentCTAProps {
    onStart?: () => void;
    className?: string;
}

export function NewIncidentCTA({ onStart, className }: NewIncidentCTAProps) {
    return (
        <div
            className={cn(
                'relative overflow-hidden rounded-2xl',
                'bg-gradient-to-br from-secondary via-secondary to-accent',
                'border border-border',
                'p-8',
                'animate-scale-in',
                className
            )}
        >
            {/* Background decorative elements */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-foreground/[0.02] rounded-full blur-3xl transform translate-x-1/2 -translate-y-1/2" />
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-foreground/[0.01] rounded-full blur-2xl transform -translate-x-1/2 translate-y-1/2" />

            {/* Content */}
            <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                <div className="flex items-start gap-4">
                    {/* Icon */}
                    <div className="flex-shrink-0 w-14 h-14 rounded-2xl bg-foreground/5 border border-foreground/10 flex items-center justify-center">
                        <Icon name="Shield" size="lg" className="text-foreground" />
                    </div>

                    {/* Text */}
                    <div>
                        <h2 className="text-xl font-semibold text-foreground mb-2">
                            Report a Cybercrime Incident
                        </h2>
                        <p className="text-sm text-muted-foreground max-w-lg">
                            Our AI will guide you through documenting your case, identify applicable laws,
                            and help you take the right legal steps. Your information is encrypted and secure.
                        </p>
                    </div>
                </div>

                {/* CTA Button */}
                <Button
                    onClick={onStart}
                    size="lg"
                    className="flex-shrink-0 gap-2 group"
                >
                    <span>Start New Incident</span>
                    <Icon
                        name="ArrowRight"
                        size="sm"
                        className="group-hover:translate-x-0.5 transition-transform"
                    />
                </Button>
            </div>

            {/* Trust indicators */}
            <div className="relative z-10 flex items-center gap-6 mt-6 pt-6 border-t border-border/50">
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Icon name="Lock" size="xs" className="text-muted-foreground" />
                    <span>End-to-end encrypted</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Icon name="Clock" size="xs" className="text-muted-foreground" />
                    <span>Takes ~5 minutes</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Icon name="Scale" size="xs" className="text-muted-foreground" />
                    <span>AI-powered legal analysis</span>
                </div>
            </div>
        </div>
    );
}

export default NewIncidentCTA;
