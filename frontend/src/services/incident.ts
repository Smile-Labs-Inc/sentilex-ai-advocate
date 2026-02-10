/**
 * Incident API Service
 *
 * Handles communication with the backend incidents API.
 */

import { API_BASE_URL } from "../config";
import { apiClient } from "./apiClient";

// Types matching backend schemas
export type IncidentType =
  | "cyberbullying"
  | "harassment"
  | "stalking"
  | "non-consensual-leak"
  | "identity-theft"
  | "online-fraud"
  | "other";

export type IncidentStatus =
  | "draft"
  | "submitted"
  | "under_review"
  | "resolved";

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
 * Create a new incident report.
 */
export async function createIncident(
  data: IncidentCreate,
): Promise<IncidentResponse> {
  const response = await apiClient.post(`${API_BASE_URL}/incidents/`, data);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to create incident: ${response.status}`,
    );
  }

  return response.json();
}

/**
 * Get all incidents for the current user.
 */
export async function getIncidents(
  statusFilter?: IncidentStatus,
): Promise<IncidentListResponse> {
  const url = new URL(`${API_BASE_URL}/incidents/`);
  if (statusFilter) {
    url.searchParams.append("status_filter", statusFilter);
  }

  const response = await apiClient.get(url.toString());

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to fetch incidents: ${response.status}`,
    );
  }

  return response.json();
}

/**
 * Get a single incident by ID.
 */
export async function getIncident(
  incidentId: number,
): Promise<IncidentResponse> {
  const response = await apiClient.get(`${API_BASE_URL}/incidents/${incidentId}`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to fetch incident: ${response.status}`,
    );
  }

  return response.json();
}

/**
 * Delete an incident (any status can be deleted).
 */
export async function deleteIncident(incidentId: number): Promise<void> {
  const response = await apiClient.delete(`${API_BASE_URL}/incidents/${incidentId}`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to delete incident: ${response.status}`,
    );
  }
}

// ============================================================================
// Incident Chat API Functions
// ============================================================================

export type IncidentChatRole = "user" | "assistant" | "system";

export interface IncidentChatMessageCreate {
  content: string;
}

export interface IncidentChatMessageResponse {
  id: number;
  incident_id: number;
  user_id: number | null;
  role: IncidentChatRole;
  content: string;
  created_at: string;
}

export interface IncidentChatExchangeResponse {
  user_message: IncidentChatMessageResponse;
  assistant_message: IncidentChatMessageResponse;
}

/**
 * Send a message in incident chat and get AI response.
 */
export async function sendIncidentChatMessage(
  incidentId: number,
  content: string,
): Promise<IncidentChatExchangeResponse> {
  const response = await apiClient.post(
    `${API_BASE_URL}/incidents/${incidentId}/messages`,
    { content }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to send message: ${response.status}`,
    );
  }

  return response.json();
}

/**
 * Get all chat messages for an incident.
 */
export async function getIncidentChatMessages(
  incidentId: number,
): Promise<IncidentChatMessageResponse[]> {
  const response = await apiClient.get(
    `${API_BASE_URL}/incidents/${incidentId}/messages`
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to fetch messages: ${response.status}`,
    );
  }

  return response.json();
}

// ============================================================================
// Evidence Upload API Functions
// ============================================================================

export interface EvidenceResponse {
  id: number;
  incident_id: number;
  file_name: string;
  file_path: string;
  file_type: string | null;
  file_size: number | null;
  uploaded_at: string;
}

export interface EvidenceListResponse {
  evidence: EvidenceResponse[];
  total: number;
}

/**
 * Upload evidence files for an incident.
 */
export async function uploadEvidence(
  incidentId: number,
  files: File[],
): Promise<EvidenceResponse[]> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });

  const response = await apiClient.fetch(
    `${API_BASE_URL}/incidents/${incidentId}/evidence`,
    {
      method: "POST",
      body: formData,
      // Don't set Content-Type header for FormData - browser will set it with boundary
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to upload evidence: ${response.status}`,
    );
  }

  return response.json();
}

/**
 * Get all evidence for an incident.
 */
export async function getIncidentEvidence(
  incidentId: number,
): Promise<EvidenceListResponse> {
  const response = await apiClient.get(
    `${API_BASE_URL}/incidents/${incidentId}/evidence`
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to fetch evidence: ${response.status}`,
    );
  }

  return response.json();
}

/**
 * Delete an evidence file.
 */
export async function deleteEvidence(
  incidentId: number,
  evidenceId: number,
): Promise<void> {
  const response = await apiClient.delete(
    `${API_BASE_URL}/incidents/${incidentId}/evidence/${evidenceId}`
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to delete evidence: ${response.status}`,
    );
  }
}

// ============================================================================
// Occurrence Types and Methods
// ============================================================================

export interface OccurrenceCreate {
  title: string;
  description: string;
  date_occurred: string; // YYYY-MM-DD format
}

export interface OccurrenceUpdate {
  title?: string;
  description?: string;
  date_occurred?: string;
}

export interface OccurrenceResponse {
  id: number;
  incident_id: number;
  title: string;
  description: string;
  date_occurred: string;
  created_at: string;
  updated_at: string;
}

export interface OccurrenceListResponse {
  occurrences: OccurrenceResponse[];
  total: number;
}

/**
 * Create a new occurrence for an incident.
 */
export async function createOccurrence(
  incidentId: number,
  data: OccurrenceCreate,
): Promise<OccurrenceResponse> {
  const response = await apiClient.post(
    `${API_BASE_URL}/incidents/${incidentId}/occurrences`,
    data
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to create occurrence: ${response.status}`,
    );
  }

  return response.json();
}

/**
 * Get all occurrences for an incident.
 */
export async function getOccurrences(
  incidentId: number,
): Promise<OccurrenceListResponse> {
  const response = await apiClient.get(
    `${API_BASE_URL}/incidents/${incidentId}/occurrences`
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to fetch occurrences: ${response.status}`,
    );
  }

  return response.json();
}

/**
 * Get a specific occurrence by ID.
 */
export async function getOccurrence(
  incidentId: number,
  occurrenceId: number,
): Promise<OccurrenceResponse> {
  const response = await apiClient.get(
    `${API_BASE_URL}/incidents/${incidentId}/occurrences/${occurrenceId}`
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to fetch occurrence: ${response.status}`,
    );
  }

  return response.json();
}

/**
 * Upload evidence files linked to a specific occurrence.
 */
export async function uploadEvidenceToOccurrence(
  incidentId: number,
  occurrenceId: number,
  files: File[],
): Promise<EvidenceResponse[]> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });

  const response = await apiClient.fetch(
    `${API_BASE_URL}/incidents/${incidentId}/evidence?occurrence_id=${occurrenceId}`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to upload evidence: ${response.status}`,
    );
  }

  return response.json();
}

/**
 * Delete an occurrence.
 */
export async function deleteOccurrence(
  incidentId: number,
  occurrenceId: number,
): Promise<void> {
  const response = await apiClient.delete(
    `${API_BASE_URL}/incidents/${incidentId}/occurrences/${occurrenceId}`
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to delete occurrence: ${response.status}`,
    );
  }
}
