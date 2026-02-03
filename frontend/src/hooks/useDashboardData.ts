// =============================================================================
// Veritas Protocol - Dashboard Data Hook
// Centralizes data fetching logic for easy API replacement later
// =============================================================================

import { useState, useMemo, useEffect } from 'preact/hooks';
import type {
    Incident,
    UserStats,
    GlobalStats,
    ActivityItem,
    CaseTypeDistribution
} from '../types';
import {
    mockUserStats,
    mockGlobalStats,
    mockActivityFeed,
    mockCaseTypeDistribution,
} from '../data/mockData';
import { primaryQuickLinks } from '../data/quickLinks';
import { getIncidents, type IncidentResponse } from '../services/incident';

interface DashboardData {
    isNewUser: boolean;
    userStats: UserStats | null;
    globalStats: GlobalStats | null;
    incidents: Incident[];
    activity: ActivityItem[];
    caseDistribution: CaseTypeDistribution[];
    quickLinks: typeof primaryQuickLinks;
    isLoading: boolean;
}

// Helper to convert backend incident to frontend format
function convertIncident(backendIncident: IncidentResponse): Incident {
    const statusMap: Record<string, Incident['status']> = {
        'draft': 'pending',
        'submitted': 'submitted-to-police',
        'under_review': 'in-progress',
        'resolved': 'resolved'
    };

    return {
        id: `inc_${backendIncident.id}`,
        title: backendIncident.title,
        type: backendIncident.incident_type,
        status: statusMap[backendIncident.status] || 'pending',
        createdAt: new Date(backendIncident.created_at),
        updatedAt: new Date(backendIncident.updated_at),
        lawsIdentified: 0, // TODO: Add this to backend if needed
        description: backendIncident.description,
    };
}

/**
 * Custom hook for dashboard data
 * Toggle useNewUser to test different dashboard states
 */
export function useDashboardData(useNewUser = false): DashboardData {
    const [isLoading, setIsLoading] = useState(true);
    const [incidents, setIncidents] = useState<Incident[]>([]);

    // Determine new user based on parameter
    const isNewUser = useNewUser;

    // Fetch real incidents from API
    useEffect(() => {
        const fetchIncidents = async () => {
            if (isNewUser) {
                setIncidents([]);
                setIsLoading(false);
                return;
            }

            try {
                setIsLoading(true);
                const response = await getIncidents();
                const convertedIncidents = response.incidents.map(convertIncident);
                setIncidents(convertedIncidents);
            } catch (error) {
                console.error('Failed to fetch incidents:', error);
                setIncidents([]);
            } finally {
                setIsLoading(false);
            }
        };

        fetchIncidents();
    }, [isNewUser]);

    // Memoize computed data
    const data = useMemo(() => ({
        isNewUser,
        userStats: isNewUser ? null : mockUserStats,
        globalStats: mockGlobalStats,
        incidents,
        activity: isNewUser ? [] : mockActivityFeed,
        caseDistribution: mockCaseTypeDistribution,
        quickLinks: primaryQuickLinks,
        isLoading,
    }), [isNewUser, incidents, isLoading]);

    return data;
}

/**
 * Hook for individual incident data
 * (For future incident detail page)
 */
export function useIncident(id: string): Incident | null {
    const [incident, setIncident] = useState<Incident | null>(null);

    useEffect(() => {
        const fetchIncident = async () => {
            try {
                const numericId = parseInt(id.replace('inc_', ''));
                const { getIncident } = await import('../services/incident');
                const backendIncident = await getIncident(numericId);
                setIncident(convertIncident(backendIncident));
            } catch (error) {
                console.error('Failed to fetch incident:', error);
                setIncident(null);
            }
        };

        if (id) {
            fetchIncident();
        }
    }, [id]);

    return incident;
}

/**
 * Hook for filtered incidents
 */
export function useFilteredIncidents(status?: string): Incident[] {
    const [incidents, setIncidents] = useState<Incident[]>([]);

    useEffect(() => {
        const fetchFilteredIncidents = async () => {
            try {
                const response = await getIncidents();
                let filtered = response.incidents.map(convertIncident);

                if (status && status !== 'all') {
                    const statusMap: Record<string, string> = {
                        'pending': 'draft',
                        'submitted-to-police': 'submitted',
                        'in-progress': 'under_review',
                        'resolved': 'resolved'
                    };
                    const backendStatus = statusMap[status];
                    if (backendStatus) {
                        filtered = filtered.filter(inc => {
                            const backendStatusValue = statusMap[inc.status];
                            return backendStatusValue === backendStatus;
                        });
                    }
                }

                setIncidents(filtered);
            } catch (error) {
                console.error('Failed to fetch incidents:', error);
                setIncidents([]);
            }
        };

        fetchFilteredIncidents();
    }, [status]);

    return incidents;
}
