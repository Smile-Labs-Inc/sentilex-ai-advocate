// =============================================================================
// StatsOverview Molecule
// Horizontal stats display above Recent Incidents list
// =============================================================================

import { Icon } from '../../atoms/Icon/Icon';
import type { UserStats } from '../../../types';

export interface StatsOverviewProps {
    userStats?: UserStats | null;
    className?: string;
}

export function StatsOverview({ userStats, className }: StatsOverviewProps) {
    if (!userStats) {
        return null;
    }

    const stats = [
        {
            icon: 'Clock',
            label: 'Pending Reports',
            value: userStats.pendingReports,
            color: 'text-amber-300',
            bgColor: 'bg-amber-500/10',
        },
        {
            icon: 'FileText',
            label: 'Total Reports',
            value: userStats.totalReports,
            color: 'text-blue-300',
            bgColor: 'bg-blue-500/10',
        },
        {
            icon: 'CheckCircle',
            label: 'Resolved Cases',
            value: userStats.resolvedCases,
            color: 'text-green-300',
            bgColor: 'bg-green-500/10',
        },
        {
            icon: 'Loader',
            label: 'In Progress',
            value: userStats.inProgressCases,
            color: 'text-purple-300',
            bgColor: 'bg-purple-500/10',
        },
    ];

    return (
        <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-4 ${className || ''}`}>
            {stats.map((stat, index) => (
                <div
                    key={index}
                    className="bg-white/5 border border-white/15 rounded-lg p-3 backdrop-blur-sm transition-all hover:bg-white/10 hover:border-white/20"
                >
                    <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-lg ${stat.bgColor} flex items-center justify-center shrink-0`}>
                            <Icon name={stat.icon as any} size="sm" className={stat.color} />
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-xs text-white/50 mb-0.5 truncate">{stat.label}</p>
                            <p className="text-2xl font-semibold text-white leading-none">
                                {stat.value}
                            </p>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
}

export default StatsOverview;
