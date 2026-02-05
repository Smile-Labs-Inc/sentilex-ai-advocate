// =============================================================================
// Veritas Protocol - Quick Links Data
// Emergency contacts, resources, and useful links
// =============================================================================

import type { QuickLink } from '../types';

export const quickLinks: QuickLink[] = [
    {
        id: 'police-emergency',
        label: 'Police Emergency',
        description: 'Call 119 for immediate assistance',
        icon: 'Phone',
        href: 'tel:119',
        type: 'hotline',
    },
    {
        id: 'cybercrime-portal',
        label: 'Cybercrime Portal',
        description: 'Official cybercrime reporting',
        icon: 'Shield',
        href: 'https://www.cert.gov.lk/report_incident',
        type: 'resource',
    },
    {
        id: 'find-lawyers',
        label: 'Find Lawyers',
        description: 'Connect with legal experts near you',
        icon: 'Scale',
        href: '/lawyers',
        type: 'finder',
    },
    {
        id: 'women-helpline',
        label: 'Women Helpline',
        description: 'Call 1938 for women safety',
        icon: 'Heart',
        href: 'tel:1938',
        type: 'hotline',
    },
    {
        id: 'ncw-portal',
        label: 'NCW Complaints',
        description: 'National Commission for Women',
        icon: 'FileText',
        href: 'http://ncw.nic.in',
        type: 'resource',
    },
    {
        id: 'mental-health',
        label: 'Mental Health Support',
        description: 'iCall: 9152987821',
        icon: 'HeartHandshake',
        href: 'tel:9152987821',
        type: 'hotline',
    },
];

// Primary quick links shown on dashboard (first 4)
export const primaryQuickLinks = quickLinks.slice(0, 4);

// All quick links for expanded view
export const allQuickLinks = quickLinks;
