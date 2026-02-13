// =============================================================================
// StatsGrid Organism
// Grid of 4 stat cards for user statistics
// =============================================================================

import { cn } from '../../../lib/utils';
import { StatCard } from '../../molecules/StatCard/StatCard';
import type { UserStats, GlobalStats } from '../../../types';

export interface StatsGridProps {
    userStats?: UserStats | null;
    globalStats?: GlobalStats | null;
    isNewUser: boolean;
    className?: string;
}

export function StatsGrid({ userStats, globalStats, isNewUser, className }: StatsGridProps) {
    // Show global stats for new users, user stats for returning users
    if (isNewUser && globalStats) {
        return (
            <div className={cn('grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4', className)}>
                <StatCard
                    icon="CheckCircle"
                    label="Cases Solved"
                    value={globalStats.totalCasesSolved}
                    status={{ type: 'resolved', label: 'Resolved' }}
                    subtitle="Platform total"
                />
                <StatCard
                    icon="Users"
                    label="Active Users"
                    value={globalStats.activeUsers}
                    status={{ type: 'active', label: 'Online now' }}
                    subtitle="Getting legal support"
                />
                <StatCard
                    icon="Scale"
                    label="Affiliated Lawyers"
                    value={globalStats.affiliatedLawyers}
                    status={{ type: 'progress', label: 'Available' }}
                    subtitle="Ready to help"
                />
                <StatCard
                    icon="Layers"
                    label="Case Types"
                    value={globalStats.caseTypesHandled}
                    status={{ type: 'progress', label: 'Covered' }}
                    subtitle="Legal categories"
                />
            </div>
        );
    }

    // Returning user stats
    if (userStats) {
        return (
            <div className={cn('grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4', className)}>
                <StatCard
                    icon="Clock"
                    label="Pending Reports"
                    value={userStats.pendingReports}
                    status={{ type: 'pending', label: 'Awaiting review' }}
                    subtitle="Needs attention"
                />
                <StatCard
                    icon="FileText"
                    label="Total Reports"
                    value={userStats.totalReports}
                    subtitle="All incidents logged"
                />
                <StatCard
                    icon="CheckCircle"
                    label="Resolved Cases"
                    value={userStats.resolvedCases}
                    status={{ type: 'resolved', label: 'Completed' }}
                    subtitle="Successfully handled"
                />
                <StatCard
                    icon="Loader"
                    label="In Progress"
                    value={userStats.inProgressCases}
                    status={{ type: 'progress', label: 'Active' }}
                    subtitle="Being processed"
                />
            </div>
        );
    }

    // Fallback: If userStats is null but we have globalStats, show those
    // Fallback: If userStats is null but we have globalStats, show those
    if (globalStats) {
        return (
            <div className={cn('grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4', className)}>
                <StatCard
                    icon="CheckCircle"
                    label="Cases Solved"
                    value={globalStats.totalCasesSolved}
                    status={{ type: 'resolved', label: 'Resolved' }}
                    subtitle="Platform total"
                />
                <StatCard
                    icon="Users"
                    label="Active Users"
                    value={globalStats.activeUsers}
                    status={{ type: 'active', label: 'Online now' }}
                    subtitle="Getting legal support"
                />
                <StatCard
                    icon="Scale"
                    label="Affiliated Lawyers"
                    value={globalStats.affiliatedLawyers}
                    status={{ type: 'progress', label: 'Available' }}
                    subtitle="Ready to help"
                />
                <StatCard
                    icon="Layers"
                    label="Case Types"
                    value={globalStats.caseTypesHandled}
                    status={{ type: 'progress', label: 'Covered' }}
                    subtitle="Legal categories"
                />
            </div>
        );
    }

    // Fallback empty state
    return null;
}

export default StatsGrid;
