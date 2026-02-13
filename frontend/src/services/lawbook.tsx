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

export interface QueryRequest {
    question: string;
    case_context?: string;
}

export interface Citation {
    law_name: string;
    section: string;
    text: string;
}

export interface QueryMetadata {
    retrieval_timestamp: string;
    sources_count: number;
    citations_count: number;
    validation_status: string;
    reasoning_confidence: number;
    validation_confidence: number;
}

export interface LegalAnalysis {
    response: string;
    confidence_note: string;
    disclaimer: string;
    metadata: QueryMetadata;
    citations: Citation[];
}

export interface QueryResponse {
    status: 'success' | 'refused';
    data: LegalAnalysis;
    session_id: string;
    timestamp: string;
}

import { API_CONFIG } from '../config';

/**
 * Fetches the list of available laws
 * @returns Promise resolving to an array of laws
 */
export async function fetchLaws(): Promise<Law[]> {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.LAWBOOK.LAWS}`);

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
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.LAWBOOK.LAW_CONTENT(lawId)}`);

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

/**
 * Submits a legal query to the backend
 * @param request - The query request containing question and optional context
 * @returns Promise resolving to the query response
 */
export async function submitQuery(request: QueryRequest): Promise<QueryResponse> {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.LAWBOOK.QUERY}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(request),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('Lawbook Query Error:', errorData);

            // Format validation errors if available
            let errorMessage = errorData.detail || `Failed to submit query: ${response.statusText}`;
            if (Array.isArray(errorData.detail)) {
                errorMessage = errorData.detail.map((err: any) => `${err.loc.join('.')}: ${err.msg}`).join(', ');
            }

            throw new Error(errorMessage);
        }

        return await response.json();
    } catch (error) {
        if (error instanceof Error) {
            throw new Error(error.message);
        }
        throw new Error('Failed to submit query: Unknown error');
    }
}


