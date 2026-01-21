// =============================================================================
// Veritas Protocol - Dashboard Data Hook
// Centralizes data fetching logic for easy API replacement later
// =============================================================================

import { useState, useMemo } from 'preact/hooks';
import type {
    User,
    Incident,
    UserStats,
    GlobalStats,
    ActivityItem,
    CaseTypeDistribution
} from '../types';
import {
    mockUser,
    mockNewUser,
    mockIncidents,
    mockUserStats,
    mockGlobalStats,
    mockActivityFeed,
    mockCaseTypeDistribution,
} from '../data/mockData';
import { primaryQuickLinks } from '../data/quickLinks';

interface DashboardData {
    user: User;
    isNewUser: boolean;
    userStats: UserStats | null;
    globalStats: GlobalStats | null;
    incidents: Incident[];
    activity: ActivityItem[];
    caseDistribution: CaseTypeDistribution[];
    quickLinks: typeof primaryQuickLinks;
    isLoading: boolean;
}

/**
 * Custom hook for dashboard data
 * Toggle useNewUser to test different dashboard states
 */
export function useDashboardData(useNewUser = false): DashboardData {
    // Simulate loading state (for future API integration)
    const [isLoading] = useState(false);

    // Select user based on flag (will be replaced with auth state later)
    const user = useNewUser ? mockNewUser : mockUser;
    const isNewUser = user.isNewUser;

    // Memoize computed data
    const data = useMemo(() => ({
        user,
        isNewUser,
        userStats: isNewUser ? null : mockUserStats,
        globalStats: mockGlobalStats, // Always available, shown prominently for new users
        incidents: isNewUser ? [] : mockIncidents,
        activity: isNewUser ? [] : mockActivityFeed,
        caseDistribution: mockCaseTypeDistribution,
        quickLinks: primaryQuickLinks,
        isLoading,
    }), [user, isNewUser, isLoading]);

    return data;
}

/**
 * Hook for individual incident data
 * (For future incident detail page)
 */
export function useIncident(id: string): Incident | null {
    return useMemo(() => {
        return mockIncidents.find(inc => inc.id === id) || null;
    }, [id]);
}

/**
 * Hook for filtered incidents
 */
export function useFilteredIncidents(status?: string): Incident[] {
    return useMemo(() => {
        if (!status || status === 'all') return mockIncidents;
        return mockIncidents.filter(inc => inc.status === status);
    }, [status]);
}
