// =============================================================================
// IncidentRow Molecule
// Single row in the incidents table/list
// =============================================================================

import { cn } from '../../../lib/utils';
import { Badge, getStatusVariant, getStatusLabel } from '../../atoms/Badge/Badge';
import { Icon, type IconName } from '../../atoms/Icon/Icon';
import { StatusDot } from '../../atoms/StatusDot/StatusDot';
import { Button } from '../../atoms/Button/Button';
import type { Incident, IncidentType } from '../../../types';
import { getRelativeTime } from '../../../data/mockData';
import type { JSX } from 'preact';

export interface IncidentRowProps {
    incident: Incident;
    onClick?: (incident: Incident) => void;
    onDelete?: (incident: Incident) => void;
    className?: string;
    style?: JSX.CSSProperties;
}

// Map incident type to icon
const typeIconMap: Record<IncidentType, IconName> = {
    'cyberbullying': 'MessageSquareWarning',
    'harassment': 'AlertTriangle',
    'stalking': 'Eye',
    'non-consensual-leak': 'ImageOff',
    'identity-theft': 'UserX',
    'online-fraud': 'CreditCard',
    'other': 'FileQuestion',
};

// Map incident type to readable label
const typeLabels: Record<IncidentType, string> = {
    'cyberbullying': 'Cyberbullying',
    'harassment': 'Harassment',
    'stalking': 'Stalking',
    'non-consensual-leak': 'Non-consensual Leak',
    'identity-theft': 'Identity Theft',
    'online-fraud': 'Online Fraud',
    'other': 'Other',
};

// Map status to dot variant
const statusToDot: Record<string, 'pending' | 'progress' | 'resolved' | 'submitted'> = {
    'pending': 'pending',
    'in-progress': 'progress',
    'resolved': 'resolved',
    'submitted-to-police': 'submitted',
};

export function IncidentRow({ incident, onClick, onDelete, className, style }: IncidentRowProps) {
    const iconName = typeIconMap[incident.type] || 'FileText';

    const handleDelete = (e: Event) => {
        e.stopPropagation(); // Prevent row click
        onDelete?.(incident);
    };

    return (
        <div
            onClick={() => onClick?.(incident)}
            style={style}
            className={cn(
                'group flex items-center gap-4 p-4 rounded-lg',
                'bg-secondary/30 border border-transparent',
                'hover:bg-secondary/60 hover:border-border',
                'transition-all duration-300 ease-out',
                'cursor-pointer',
                'active:scale-[0.995]',
                className
            )}
        >
            {/* Type Icon */}
            <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-secondary/50 text-muted-foreground group-hover:text-foreground transition-colors">
                <Icon name={iconName} size="md" />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium text-sm text-foreground truncate group-hover:text-foreground/90">
                        {incident.title}
                    </h4>
                </div>
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    <span>{typeLabels[incident.type]}</span>
                    <span>•</span>
                    <span>{incident.lawsIdentified} laws identified</span>
                </div>
            </div>

            {/* Status Badge */}
            <Badge variant={getStatusVariant(incident.status)} size="sm">
                <StatusDot
                    status={statusToDot[incident.status]}
                    size="sm"
                    pulse={incident.status !== 'resolved'}
                />
                {getStatusLabel(incident.status)}
            </Badge>

            {/* Date */}
            <div className="text-xs text-muted-foreground text-right min-w-[80px]">
                {getRelativeTime(incident.updatedAt)}
            </div>

            {/* Delete Button */}
            {onDelete && (
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleDelete}
                    className="opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-foreground"
                    title="Delete incident"
                >
                    <Icon name="Trash2" size="sm" />
                </Button>
            )}

            {/* Arrow */}
            <Icon
                name="ChevronRight"
                size="sm"
                className="text-muted-foreground group-hover:text-foreground/70 group-hover:translate-x-0.5 transition-all"
            />
        </div>
    );
}

export default IncidentRow;
