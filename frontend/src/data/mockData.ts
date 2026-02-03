// =============================================================================
// Veritas Protocol - Mock Data
// Centralized dummy data that can be easily swapped with API calls later
// =============================================================================

import type {
    Incident,
    UserStats,
    GlobalStats,
    ActivityItem,
    CaseTypeDistribution
} from '../types';
import type { UserProfile } from '../types/auth';

// =============================================================================
// Mock User
// Toggle isNewUser to test different dashboard views
// =============================================================================

export const mockUser: UserProfile = {
    id: 1,
    first_name: 'Alex',
    last_name: 'Chen',
    email: 'alex.chen@email.com',
    role: 'user',
    is_active: true,
    email_verified: true,
    mfa_enabled: false,
    preferred_language: 'en',
    district: 'Colombo',
};

export const mockNewUser: UserProfile = {
    id: 2,
    first_name: 'New',
    last_name: 'User',
    email: 'newuser@email.com',
    role: 'user',
    is_active: true,
    email_verified: false,
    mfa_enabled: false,
    preferred_language: 'en',
};

// =============================================================================
// Mock Incidents (for returning users)
// =============================================================================

export const mockIncidents: Incident[] = [
    {
        id: 'inc_001',
        title: 'Harassment on Social Media Platform',
        type: 'harassment',
        status: 'in-progress',
        createdAt: new Date('2026-01-15T10:30:00'),
        updatedAt: new Date('2026-01-16T14:20:00'),
        lawsIdentified: 3,
        description: 'Repeated threatening messages received via Instagram DMs',
    },
    {
        id: 'inc_002',
        title: 'Unauthorized Image Distribution',
        type: 'non-consensual-leak',
        status: 'submitted-to-police',
        createdAt: new Date('2026-01-10T09:15:00'),
        updatedAt: new Date('2026-01-14T11:00:00'),
        lawsIdentified: 5,
        description: 'Private images shared without consent on multiple platforms',
    },
    {
        id: 'inc_003',
        title: 'Online Stalking Behavior',
        type: 'stalking',
        status: 'pending',
        createdAt: new Date('2026-01-17T08:00:00'),
        updatedAt: new Date('2026-01-17T08:00:00'),
        lawsIdentified: 0,
        description: 'Unknown person tracking online activity and sending messages',
    },
    {
        id: 'inc_004',
        title: 'Cyberbullying in Gaming Community',
        type: 'cyberbullying',
        status: 'resolved',
        createdAt: new Date('2025-12-20T16:45:00'),
        updatedAt: new Date('2026-01-05T10:30:00'),
        lawsIdentified: 2,
        description: 'Coordinated harassment campaign in online gaming platform',
    },
    {
        id: 'inc_005',
        title: 'Identity Theft Attempt',
        type: 'identity-theft',
        status: 'resolved',
        createdAt: new Date('2025-12-01T12:00:00'),
        updatedAt: new Date('2025-12-28T09:00:00'),
        lawsIdentified: 4,
        description: 'Someone created fake accounts impersonating me',
    },
];

// =============================================================================
// Mock User Statistics
// =============================================================================

export const mockUserStats: UserStats = {
    pendingReports: 1,
    totalReports: 5,
    resolvedCases: 2,
    inProgressCases: 2,
};

// =============================================================================
// Mock Global Statistics (for new users)
// =============================================================================

export const mockGlobalStats: GlobalStats = {
    totalCasesSolved: 2847,
    activeUsers: 1256,
    affiliatedLawyers: 89,
    caseTypesHandled: 12,
};

// =============================================================================
// Mock Case Type Distribution (for charts)
// =============================================================================

export const mockCaseTypeDistribution: CaseTypeDistribution[] = [
    {
        type: 'harassment',
        label: 'Harassment',
        count: 847,
        percentage: 32,
        color: '#ffffff'
    },
    {
        type: 'cyberbullying',
        label: 'Cyberbullying',
        count: 623,
        percentage: 24,
        color: '#a1a1aa'
    },
    {
        type: 'stalking',
        label: 'Stalking',
        count: 412,
        percentage: 16,
        color: '#71717a'
    },
    {
        type: 'non-consensual-leak',
        label: 'Non-consensual Leaks',
        count: 389,
        percentage: 15,
        color: '#52525b'
    },
    {
        type: 'identity-theft',
        label: 'Identity Theft',
        count: 234,
        percentage: 9,
        color: '#3f3f46'
    },
    {
        type: 'other',
        label: 'Other',
        count: 104,
        percentage: 4,
        color: '#27272a'
    },
];

// =============================================================================
// Mock Activity Feed
// =============================================================================

export const mockActivityFeed: ActivityItem[] = [
    {
        id: 'act_001',
        message: 'New law identified for case',
        highlightText: 'IT Act Section 66A',
        timestamp: new Date('2026-01-17T08:45:00'),
        type: 'law-identified',
    },
    {
        id: 'act_002',
        message: 'Evidence uploaded to',
        highlightText: 'Case #inc_001',
        timestamp: new Date('2026-01-16T14:20:00'),
        type: 'evidence-uploaded',
    },
    {
        id: 'act_003',
        message: 'Report submitted to police for',
        highlightText: 'Case #inc_002',
        timestamp: new Date('2026-01-14T11:00:00'),
        type: 'report-submitted',
    },
    {
        id: 'act_004',
        message: 'Case resolved successfully',
        highlightText: 'Cyberbullying Case',
        timestamp: new Date('2026-01-05T10:30:00'),
        type: 'case-resolved',
    },
    {
        id: 'act_005',
        message: 'New incident created',
        highlightText: 'Stalking Report',
        timestamp: new Date('2026-01-17T08:00:00'),
        type: 'case-opened',
    },
];

// =============================================================================
// Helper function to get relative time
// =============================================================================

export function getRelativeTime(date: Date): string {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
}
