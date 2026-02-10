// =============================================================================
// IncidentsList Organism
// List of user's logged incidents with search and filter
// =============================================================================

import { useState, useMemo } from 'preact/hooks';
import { cn } from '../../../lib/utils';
import { Card, CardHeader, CardTitle } from '../../atoms/Card/Card';
import { Button } from '../../atoms/Button/Button';
import { Icon } from '../../atoms/Icon/Icon';
import { SearchInput } from '../../molecules/SearchInput/SearchInput';
import { IncidentRow } from '../../molecules/IncidentRow/IncidentRow';
import type { Incident } from '../../../types';

export interface IncidentsListProps {
    incidents: Incident[];
    onIncidentClick?: (incident: Incident) => void;
    onDeleteIncident?: (incident: Incident) => void;
    onNewIncident?: () => void;
    onViewAllIncidents?: () => void;
    onFilterClick?: () => void;
    className?: string;
}

export function IncidentsList({
    incidents,
    onIncidentClick,
    onDeleteIncident,
    onNewIncident,
    onViewAllIncidents,
    onFilterClick,
    className
}: IncidentsListProps) {
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter] = useState<string>('all');

    // Filter incidents based on search and status
    const filteredIncidents = useMemo(() => {
        return incidents.filter((incident) => {
            // Search filter
            const matchesSearch = searchQuery === '' ||
                incident.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                incident.type.toLowerCase().includes(searchQuery.toLowerCase());

            // Status filter
            const matchesStatus = statusFilter === 'all' || incident.status === statusFilter;

            return matchesSearch && matchesStatus;
        });
    }, [incidents, searchQuery, statusFilter]);

    // Empty state
    if (incidents.length === 0) {
        return (
            <Card variant="default" padding="lg" className={cn('animate-slide-up', className)}>
                <div className="flex flex-col items-center justify-center py-12 text-center">
                    <div className="w-16 h-16 rounded-full bg-secondary flex items-center justify-center mb-4">
                        <Icon name="FileText" size="lg" className="text-muted-foreground" />
                    </div>
                    <h3 className="text-lg font-medium text-foreground mb-2">No incidents yet</h3>
                    <p className="text-sm text-muted-foreground mb-6 max-w-sm">
                        When you report incidents, they'll appear here. Start by reporting your first incident.
                    </p>
                    <Button onClick={onNewIncident} className="gap-2">
                        <Icon name="Plus" size="sm" />
                        Report First Incident
                    </Button>
                </div>
            </Card>
        );
    }

    return (
        <Card variant="default" padding="lg" className={cn('animate-slide-up', className)}>
            <CardHeader>
                <CardTitle>Recent Incidents</CardTitle>

                <div className="flex items-center gap-3">
                    <SearchInput
                        size="sm"
                        placeholder="Search incidents..."
                        showShortcut={false}
                        value={searchQuery}
                        onInput={(e) => setSearchQuery((e.target as HTMLInputElement).value)}
                        className="w-48"
                    />

                    <Button variant="secondary" size="sm" className="gap-2" onClick={onFilterClick}>
                        <Icon name="Filter" size="xs" />
                        Filter
                    </Button>
                </div>
            </CardHeader>

            {/* Incidents list */}
            <div className="space-y-2">
                {filteredIncidents.length > 0 ? (
                    filteredIncidents.map((incident, index) => (
                        <IncidentRow
                            key={incident.id}
                            incident={incident}
                            onClick={onIncidentClick}
                            onDelete={onDeleteIncident}
                            className="animate-fade-in"
                            style={{ animationDelay: `${index * 0.05}s` }}
                        />
                    ))
                ) : (
                    <div className="text-center py-8 text-muted-foreground text-sm">
                        No incidents match your search
                    </div>
                )}
            </div>

            {/* View all link */}
            {filteredIncidents.length > 0 && (
                <div className="mt-4 pt-4 border-t border-border flex justify-center">
                    <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground gap-1" onClick={onViewAllIncidents}>
                        View all incidents
                        <Icon name="ArrowRight" size="xs" />
                    </Button>
                </div>
            )}
        </Card>
    );
}

export default IncidentsList;
