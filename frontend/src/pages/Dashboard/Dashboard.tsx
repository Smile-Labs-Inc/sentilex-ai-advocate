// =============================================================================
// Dashboard Page
// Home Dashboard - adapts based on new vs returning user
// =============================================================================

import { useDashboardData } from '../../hooks/useDashboardData';
import { DashboardLayout } from '../../components/templates/DashboardLayout/DashboardLayout';
import { DashboardHeader } from '../../components/organisms/DashboardHeader/DashboardHeader';
import { StatsGrid } from '../../components/organisms/StatsGrid/StatsGrid';
import { NewIncidentCTA } from '../../components/organisms/NewIncidentCTA/NewIncidentCTA';
import { IncidentsList } from '../../components/organisms/IncidentsList/IncidentsList';
import { QuickLinksPanel } from '../../components/organisms/QuickLinksPanel/QuickLinksPanel';
import { QuickActionsGrid } from '../../components/organisms/QuickActionsGrid/QuickActionsGrid';
import { ActivityFeed } from '../../components/organisms/ActivityFeed/ActivityFeed';
import { DonutChart } from '../../components/organisms/Charts/DonutChart';
import { useAuth } from '../../hooks/useAuth';
import type { Incident, NavItem } from '../../types';

export interface DashboardProps {
    onNavigate?: (item: NavItem) => void;
    onNewIncident?: () => void;
    onViewIncident?: (incident: Incident) => void;
}

export function Dashboard({ onNavigate, onNewIncident, onViewIncident }: DashboardProps) {
    const { user } = useAuth();

    // Toggle this to see new user view
    const showNewUserView = false;

    const {
        isNewUser,
        userStats,
        globalStats,
        incidents,
        activity,
        caseDistribution,
        quickLinks
    } = useDashboardData(showNewUserView);

    if (!user) {
        return null; // Should never happen due to auth guard in app.tsx
    }

    const handleNewIncident = () => {
        onNewIncident?.();
        console.log('Start new incident');
    };

    const handleViewIncident = (incident: Incident) => {
        onViewIncident?.(incident);
        console.log('View incident:', incident.id);
    };

    const handleQuickAction = (actionId: string) => {
        console.log('Quick action:', actionId);
        if (actionId === 'new-incident') {
            handleNewIncident();
        } else if (actionId === 'ai-chat') {
            onNavigate?.({ id: 'ai-chat', label: 'AI Chat', icon: 'Sparkles', href: '/ai-chat' });
        }
    };

    return (
        <DashboardLayout user={user} onNavigate={onNavigate}>
            {/* Header */}
            <DashboardHeader
                user={user}
                onNewIncident={handleNewIncident}
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
                    {isNewUser && (
                        <DonutChart data={caseDistribution} />
                    )}

                    {/* For returning users: Show incidents list */}
                    {!isNewUser && (
                        <IncidentsList
                            incidents={incidents}
                            onIncidentClick={handleViewIncident}
                            onNewIncident={handleNewIncident}
                        />
                    )}
                </div>

                {/* Right column - 3 cols */}
                <div className="col-span-12 lg:col-span-3 space-y-6">
                    {/* Quick Actions */}
                    <QuickActionsGrid onAction={handleQuickAction} />

                    {/* Quick Links */}
                    <QuickLinksPanel links={quickLinks} />

                    {/* Activity Feed (returning users only) */}
                    {!isNewUser && (
                        <ActivityFeed activities={activity} />
                    )}
                </div>
            </div>
        </DashboardLayout>
    );
}

export default Dashboard;
