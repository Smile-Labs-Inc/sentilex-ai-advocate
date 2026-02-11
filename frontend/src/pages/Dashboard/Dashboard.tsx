// =============================================================================
// Dashboard Page
// Home Dashboard - adapts based on new vs returning user
// =============================================================================

import { useDashboardData } from "../../hooks/useDashboardData";
import { DashboardLayout } from "../../components/templates/DashboardLayout/DashboardLayout";
import { DashboardHeader } from "../../components/organisms/DashboardHeader/DashboardHeaderEnhanced";
import { StatsGrid } from "../../components/organisms/StatsGrid/StatsGrid";
import { useNotifications } from "../../hooks/useNotifications";
import { NewIncidentCTA } from "../../components/organisms/NewIncidentCTA/NewIncidentCTA";
import { IncidentsList } from "../../components/organisms/IncidentsList/IncidentsList";
import { QuickLinksPanel } from "../../components/organisms/QuickLinksPanel/QuickLinksPanel";
import { QuickActionsGrid } from "../../components/organisms/QuickActionsGrid/QuickActionsGrid";
import { ActivityModal } from "../../components/organisms/ActivityModal/ActivityModal";
import { useState } from "preact/hooks";
import { DonutChart } from "../../components/organisms/Charts/DonutChart";
import { useAuth } from "../../hooks/useAuth";
import { Button } from "../../components/atoms/Button/Button";
import { Icon } from "../../components/atoms/Icon/Icon";
import { deleteIncident } from "../../services/incident";
import type { Incident, NavItem } from "../../types";

export interface DashboardProps {
  onNavigate?: (item: NavItem) => void;
  onNewIncident?: () => void;
  onViewIncident?: (incident: Incident) => void;
  onIncidentsUpdated?: () => void;
}

export function Dashboard({
  onNavigate,
  onNewIncident,
  onViewIncident,
  onIncidentsUpdated,
}: DashboardProps) {
  const [showActivityModal, setShowActivityModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [incidentToDelete, setIncidentToDelete] = useState<Incident | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const { user } = useAuth();
  const {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
  } = useNotifications();

  // Toggle this to see new user view
  const showNewUserView = false;

  const {
    isNewUser,
    userStats,
    globalStats,
    incidents,
    activity,
    caseDistribution,
    quickLinks,
  } = useDashboardData(showNewUserView);

  if (!user) {
    return null; // Should never happen due to auth guard in app.tsx
  }

  const handleNewIncident = () => {
    onNewIncident?.();
  };

  const handleViewIncident = (incident: Incident) => {
    onViewIncident?.(incident);
  };

  const handleViewAllIncidents = () => {
    onNavigate?.({
      id: "incidents",
      label: "My Incidents",
      icon: "FileText",
      href: "/incidents",
    });
  };

  const handleFilterIncidents = () => {
    // Filter functionality can be implemented based on requirements
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

  const handleQuickAction = (actionId: string) => {
    if (actionId === "new-incident") {
      handleNewIncident();
    } else if (actionId === "ai-chat") {
      onNavigate?.({
        id: "ai-chat",
        label: "AI Chat",
        icon: "Sparkles",
        href: "/ai-chat",
      });
    } else if (actionId === "find-lawyer") {
      onNavigate?.({
        id: "lawyers",
        label: "Find Lawyers",
        icon: "Scale",
        href: "/lawyers",
      });
    } else if (actionId === "upload-evidence") {
      onNavigate?.({
        id: "evidence",
        label: "Evidence Vault",
        icon: "Upload",
        href: "/evidence",
      });
    }
  };

  const handleMarkNotificationAsRead = (id: string) => {
    markAsRead(id);
  };

  const handleMarkAllNotificationsAsRead = () => {
    markAllAsRead();
  };

  const handleViewAllNotifications = () => {
    onNavigate?.({
      id: "notifications",
      label: "Notifications",
      icon: "Bell",
      href: "/notifications",
    });
  };

  return (
    <DashboardLayout
      user={user}
      onNavigate={onNavigate}
      onOpenActivity={() => setShowActivityModal(true)}
    >
      {/* Header */}
      <DashboardHeader
        user={user}
        notifications={notifications}
        onNewIncident={handleNewIncident}
        onOpenActivity={() => setShowActivityModal(true)}
        onMarkNotificationAsRead={handleMarkNotificationAsRead}
        onMarkAllNotificationsAsRead={handleMarkAllNotificationsAsRead}
        onViewAllNotifications={handleViewAllNotifications}
      />

      {/* New User: Prominent CTA */}
      {isNewUser && (
        <div className="mb-6">
          <NewIncidentCTA onStart={handleNewIncident} />
        </div>
      )}

      {/* Stats Grid */}
      <div className="mb-6">
        <StatsGrid
          userStats={userStats}
          globalStats={globalStats}
          isNewUser={isNewUser}
        />
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-12 gap-6">
        {/* Left column - 9 cols */}
        <div className="col-span-12 lg:col-span-9 space-y-6">
          {/* For new users: Show case distribution chart */}
          {isNewUser && <DonutChart data={caseDistribution} />}

          {/* For returning users: Show incidents list */}
          {!isNewUser && (
            <IncidentsList
              incidents={incidents}
              onIncidentClick={handleViewIncident}
              onDeleteIncident={handleDeleteIncident}
              onNewIncident={handleNewIncident}
              onViewAllIncidents={handleViewAllIncidents}
              onFilterClick={handleFilterIncidents}
            />
          )}
        </div>

        {/* Right column - 3 cols */}
        <div className="col-span-12 lg:col-span-3 space-y-6">
          {/* Quick Actions */}
          <QuickActionsGrid onAction={handleQuickAction} />

          {/* Quick Links */}
          <QuickLinksPanel links={quickLinks} />

          {/* Activity Feed moved to top-left button (opens modal) */}
        </div>
      </div>

      {/* Activity modal opened from top-left button */}
      {!isNewUser && (
        <>
          {showActivityModal && (
            <ActivityModal
              isOpen={showActivityModal}
              activities={activity}
              onClose={() => setShowActivityModal(false)}
            />
          )}
        </>
      )}

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

export default Dashboard;
