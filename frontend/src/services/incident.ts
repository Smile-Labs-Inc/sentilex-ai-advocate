/**
 * Incident API Service
 * 
 * Handles communication with the backend incidents API.
 */

import { API_BASE_URL, APP_CONFIG } from '../config';

// Types matching backend schemas
export type IncidentType =
    | 'cyberbullying'
    | 'harassment'
    | 'stalking'
    | 'non-consensual-leak'
    | 'identity-theft'
    | 'online-fraud'
    | 'other';

export type IncidentStatus = 'draft' | 'submitted' | 'under_review' | 'resolved';

export interface IncidentCreate {
    incident_type: IncidentType;
    title: string;
    description: string;
    date_occurred?: string | null;
    location?: string | null;
    jurisdiction?: string | null;
    platforms_involved?: string | null;
    perpetrator_info?: string | null;
    evidence_notes?: string | null;
}

export interface IncidentResponse {
    id: number;
    user_id: number;
    incident_type: IncidentType;
    title: string;
    description: string;
    date_occurred: string | null;
    location: string | null;
    jurisdiction: string | null;
    platforms_involved: string | null;
    perpetrator_info: string | null;
    evidence_notes: string | null;
    status: IncidentStatus;
    created_at: string;
    updated_at: string;
}

export interface IncidentListResponse {
    incidents: IncidentResponse[];
    total: number;
}

/**
 * Get the auth token from localStorage.
 */
function getAuthToken(): string | null {
    return localStorage.getItem(APP_CONFIG.TOKEN_STORAGE_KEY);
}

/**
 * Create a new incident report.
 */
export async function createIncident(data: IncidentCreate): Promise<IncidentResponse> {
    const token = getAuthToken();

    if (!token) {
        throw new Error('User is not authenticated');
    }

    const response = await fetch(`${API_BASE_URL}/incidents/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to create incident: ${response.status}`);
    }

    return response.json();
}

/**
 * Get all incidents for the current user.
 */
export async function getIncidents(statusFilter?: IncidentStatus): Promise<IncidentListResponse> {
    const token = getAuthToken();

    if (!token) {
        throw new Error('User is not authenticated');
    }

    const url = new URL(`${API_BASE_URL}/incidents/`);
    if (statusFilter) {
        url.searchParams.append('status_filter', statusFilter);
    }

    const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to fetch incidents: ${response.status}`);
    }

    return response.json();
}

/**
 * Get a single incident by ID.
 */
export async function getIncident(incidentId: number): Promise<IncidentResponse> {
    const token = getAuthToken();

    if (!token) {
        throw new Error('User is not authenticated');
    }

    const response = await fetch(`${API_BASE_URL}/incidents/${incidentId}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to fetch incident: ${response.status}`);
    }

    return response.json();
}
