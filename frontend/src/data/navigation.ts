// =============================================================================
// Veritas Protocol - Navigation Data
// Sidebar navigation structure
// =============================================================================

import type { NavSection } from '../types';

export const mainNavigation: NavSection[] = [
    {
        items: [
            { id: 'dashboard', label: 'Dashboard', icon: 'LayoutDashboard', href: '/' },
            { id: 'incidents', label: 'My Incidents', icon: 'FileText', href: '/incidents' },
            { id: 'evidence', label: 'Evidence Vault', icon: 'Lock', href: '/evidence' },
            { id: 'lawyers', label: 'Find Lawyers', icon: 'Scale', href: '/lawyers' },
        ],
    },
    {
        title: 'Support',
        items: [
            { id: 'lawbook', label: 'Lawbook', icon: 'BookOpen', href: '/lawbook' },
            { id: 'ai-assist', label: 'AI Assistant', icon: 'Sparkles', href: '/ai-chat' },
            { id: 'settings', label: 'Settings', icon: 'Settings', href: '/settings' },
        ],
    },
];
