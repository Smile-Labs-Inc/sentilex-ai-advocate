// =============================================================================
// Lawbook Service
// API calls for lawbook-related data
// =============================================================================

export interface Law {
    id: string;
    title: string;
    filename: string;
}

export interface LawContentResponse {
    content: string;
}

import { API_BASE_URL } from '../config';

/**
 * Fetches the list of available laws
 * @returns Promise resolving to an array of laws
 */
export async function fetchLaws(): Promise<Law[]> {
    try {
        const response = await fetch(`${API_BASE_URL}/lawbook/`);

        if (!response.ok) {
            throw new Error(`Failed to fetch laws: ${response.statusText}`);
        }

        const data = await response.json();
        return data.laws;
    } catch (error) {
        if (error instanceof Error) {
            throw new Error(`Failed to fetch laws: ${error.message}`);
        }
        throw new Error('Failed to fetch laws: Unknown error');
    }
}

/**
 * Fetches the content of a specific law by ID
 * @param lawId - The ID of the law to fetch
 * @returns Promise resolving to the law content string
 */
export async function fetchLawContent(lawId: string): Promise<string> {
    try {
        const response = await fetch(`${API_BASE_URL}/lawbook/${lawId}`);

        if (!response.ok) {
            throw new Error(`Failed to fetch law content: ${response.statusText}`);
        }

        const data = await response.json();
        return data.content;
    } catch (error) {
        if (error instanceof Error) {
            throw new Error(`Failed to fetch law content: ${error.message}`);
        }
        throw new Error('Failed to fetch law content: Unknown error');
    }
}
