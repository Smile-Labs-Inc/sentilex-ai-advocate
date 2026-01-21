// =============================================================================
// IncidentHeader Organism
// Header section for incident detail page
// =============================================================================

import { cn } from '../../../lib/utils';
import { Button } from '../../atoms/Button/Button';
import { Badge, getStatusVariant, getStatusLabel } from '../../atoms/Badge/Badge';
import { Icon, type IconName } from '../../atoms/Icon/Icon';
import { StatusDot } from '../../atoms/StatusDot/StatusDot';
import type { Incident, IncidentType } from '../../../types';

export interface IncidentHeaderProps {
    incident: Incident;
    onBack: () => void;
    className?: string;
}

const typeIconMap: Record<IncidentType, IconName> = {
    'cyberbullying': 'MessageSquareWarning',
    'harassment': 'AlertTriangle',
    'stalking': 'Eye',
    'non-consensual-leak': 'ImageOff',
    'identity-theft': 'UserX',
    'online-fraud': 'CreditCard',
    'other': 'FileQuestion',
};

const typeLabels: Record<IncidentType, string> = {
    'cyberbullying': 'Cyberbullying',
    'harassment': 'Harassment',
    'stalking': 'Stalking',
    'non-consensual-leak': 'Non-consensual Leak',
    'identity-theft': 'Identity Theft',
    'online-fraud': 'Online Fraud',
    'other': 'Other',
};

const statusToDot: Record<string, 'pending' | 'progress' | 'resolved' | 'submitted'> = {
    'pending': 'pending',
    'in-progress': 'progress',
    'resolved': 'resolved',
    'submitted-to-police': 'submitted',
};

export function IncidentHeader({ incident, onBack, className }: IncidentHeaderProps) {
    const iconName = typeIconMap[incident.type];

    return (
        <div className={cn('mb-8', className)}>
            {/* Back button */}
            <Button
                variant="ghost"
                size="sm"
                onClick={onBack}
                className="mb-4 -ml-2"
            >
                <Icon name="ArrowLeft" size="sm" />
                Back to Dashboard
            </Button>

            {/* Header content */}
            <div className="flex items-start justify-between gap-4 animate-fade-in">
                <div className="flex items-start gap-4">
                    {/* Type icon */}
                    <div className="w-12 h-12 rounded-xl bg-secondary border border-border flex items-center justify-center">
                        <Icon name={iconName} size="md" className="text-muted-foreground" />
                    </div>

                    {/* Title and meta */}
                    <div>
                        <h1 className="text-xl font-semibold text-foreground mb-1">
                            {incident.title}
                        </h1>
                        <div className="flex items-center gap-3 text-sm text-muted-foreground">
                            <span>{typeLabels[incident.type]}</span>
                            <span>•</span>
                            <span>Case #{incident.id.slice(-6).toUpperCase()}</span>
                            <span>•</span>
                            <span>{incident.lawsIdentified} laws identified</span>
                        </div>
                    </div>
                </div>

                {/* Status and actions */}
                <div className="flex items-center gap-3">
                    <Badge variant={getStatusVariant(incident.status)}>
                        <StatusDot
                            status={statusToDot[incident.status]}
                            size="sm"
                            pulse={incident.status !== 'resolved'}
                        />
                        {getStatusLabel(incident.status)}
                    </Badge>

                    <Button variant="secondary" size="sm">
                        <Icon name="Share2" size="xs" />
                        Share
                    </Button>

                    <Button size="sm">
                        <Icon name="FileText" size="xs" />
                        Generate Report
                    </Button>
                </div>
            </div>
        </div>
    );
}

export default IncidentHeader;
