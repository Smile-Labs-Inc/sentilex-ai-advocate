// =============================================================================
// Incidents Page
// Dedicated page for viewing all incidents with sidebar
// =============================================================================

import { useState } from "preact/hooks";
import { useDashboardData } from "../../hooks/useDashboardData";
import { DashboardLayout } from "../../components/templates/DashboardLayout/DashboardLayout";
import { IncidentsList } from "../../components/organisms/IncidentsList/IncidentsList";
import { Button } from "../../components/atoms/Button/Button";
import { Icon } from "../../components/atoms/Icon/Icon";
import { useAuth } from "../../hooks/useAuth";
import { deleteIncident } from "../../services/incident";
import type { Incident, NavItem } from "../../types";

export interface IncidentsPageProps {
  onNavigate?: (item: NavItem) => void;
  onNewIncident?: () => void;
  onViewIncident?: (incident: Incident) => void;
  onIncidentsUpdated?: () => void;
}

export function IncidentsPage({
  onNavigate,
  onNewIncident,
  onViewIncident,
  onIncidentsUpdated,
}: IncidentsPageProps) {
  const { user } = useAuth();
  const { incidents } = useDashboardData();
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [incidentToDelete, setIncidentToDelete] = useState<Incident | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  if (!user) {
    return null;
  }

  const handleViewIncident = (incident: Incident) => {
    onViewIncident?.(incident);
  };

  const handleDeleteIncident = (incident: Incident) => {
    setIncidentToDelete(incident);
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!incidentToDelete) return;

    setIsDeleting(true);
    try {
      const incidentId = parseInt(incidentToDelete.id.replace('inc_', ''));
      await deleteIncident(incidentId);
      setShowDeleteModal(false);
      setIncidentToDelete(null);
      onIncidentsUpdated?.();
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to delete incident');
    } finally {
      setIsDeleting(false);
    }
  };

  const cancelDelete = () => {
    if (!isDeleting) {
      setShowDeleteModal(false);
      setIncidentToDelete(null);
    }
  };

  const handleViewAllIncidents = () => {
    // Already on incidents page
  };

  const handleFilterIncidents = () => {
    // Filter functionality
  };
  // Filter functionality can be implemented based on requirements
  return (
  <DashboardLayout
    user={user}
    onNavigate={onNavigate}
  >
    {/* Full width incidents list */}
    <div className="max-w-6xl mx-auto">
      <IncidentsList
        incidents={incidents}
        onIncidentClick={handleViewIncident}
        onDeleteIncident={handleDeleteIncident}
        onNewIncident={onNewIncident}
        onViewAllIncidents={handleViewAllIncidents}
        onFilterClick={handleFilterIncidents}
      />
    </div>

    {/* Delete confirmation modal */}
    {showDeleteModal && incidentToDelete && (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Backdrop */}
        <div
          className="absolute inset-0 bg-background/80 backdrop-blur-sm"
          onClick={cancelDelete}
        />

        {/* Modal */}
        <div className="relative w-full max-w-md bg-card border border-border rounded-lg shadow-lg overflow-hidden animate-scale-in">
          {/* Header */}
          <div className="flex items-center gap-3 p-6 border-b border-border">
            <div className="w-10 h-10 rounded-full bg-muted/50 flex items-center justify-center shrink-0">
              <Icon name="AlertTriangle" size="sm" className="text-muted-foreground" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-foreground">Delete Incident</h3>
              <p className="text-sm text-muted-foreground">This action cannot be undone</p>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-4">
            <div className="bg-muted/30 border border-border/50 rounded-lg p-4">
              <p className="text-sm text-foreground font-medium">
                {incidentToDelete.title}
              </p>
              <p className="text-xs text-muted-foreground mt-2">
                Case #{incidentToDelete.id.slice(0, 8).toUpperCase()}
              </p>
            </div>

            <p className="text-sm text-muted-foreground">
              All incident data, including timeline events, evidence, and chat history will be permanently deleted. This action cannot be undone.
            </p>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 p-6 border-t border-border bg-muted/20">
            <Button
              variant="ghost"
              size="sm"
              onClick={cancelDelete}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={confirmDelete}
              disabled={isDeleting}
              className="gap-2 border-muted-foreground/30 text-muted-foreground hover:bg-muted hover:text-foreground"
            >
              {isDeleting && <Icon name="Loader2" size="xs" className="animate-spin" />}
              {isDeleting ? 'Deleting...' : 'Delete Incident'}
            </Button>
          </div>
        </div>
      </div>
    )}
  </DashboardLayout>
  );
}

export default IncidentsPage;
