/**
 * Incident API Service
 *
 * Handles communication with the backend incidents API.
 */

import { API_CONFIG } from "../config";
import { apiClient } from "./apiClient";

// Helper to construct full URL
const getUrl = (endpoint: string) => `${API_CONFIG.BASE_URL}${endpoint}`;

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
  const url = getUrl(API_CONFIG.ENDPOINTS.INCIDENTS.CREATE);
  const response = await apiClient.post(url, data);

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
  let url = getUrl(API_CONFIG.ENDPOINTS.INCIDENTS.LIST);

  // Use string concatenation for query params to avoid "Invalid URL" with relative paths
  if (statusFilter) {
    url += `?status_filter=${encodeURIComponent(statusFilter)}`;
  }

  const response = await apiClient.get(url);

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
  const url = getUrl(API_CONFIG.ENDPOINTS.INCIDENTS.GET(incidentId));
  const response = await apiClient.get(url);

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
  const url = getUrl(API_CONFIG.ENDPOINTS.INCIDENTS.DELETE(incidentId));
  const response = await apiClient.delete(url);

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
  const url = getUrl(API_CONFIG.ENDPOINTS.INCIDENTS.MESSAGES.SEND(incidentId));
  const response = await apiClient.post(url, { content });

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
  const url = getUrl(API_CONFIG.ENDPOINTS.INCIDENTS.MESSAGES.LIST(incidentId));
  const response = await apiClient.get(url);

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

  const url = getUrl(
    API_CONFIG.ENDPOINTS.INCIDENTS.EVIDENCE.UPLOAD(incidentId),
  );
  const response = await apiClient.fetch(url, {
    method: "POST",
    body: formData,
    // Don't set Content-Type header for FormData - browser will set it with boundary
  });

  console.log("[incident.uploadEvidence] Response status:", response.status);

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
  const url = getUrl(API_CONFIG.ENDPOINTS.INCIDENTS.EVIDENCE.LIST(incidentId));
  const response = await apiClient.get(url);

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
  const url = getUrl(
    API_CONFIG.ENDPOINTS.INCIDENTS.EVIDENCE.DELETE(incidentId, evidenceId),
  );
  const response = await apiClient.delete(url);

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
  const url = getUrl(API_CONFIG.ENDPOINTS.OCCURRENCES.CREATE(incidentId));
  const response = await apiClient.post(url, data);

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
  const url = getUrl(API_CONFIG.ENDPOINTS.OCCURRENCES.LIST(incidentId));
  const response = await apiClient.get(url);

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
  const url = getUrl(
    API_CONFIG.ENDPOINTS.OCCURRENCES.GET(incidentId, occurrenceId),
  );
  const response = await apiClient.get(url);

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

  let url = getUrl(API_CONFIG.ENDPOINTS.INCIDENTS.EVIDENCE.UPLOAD(incidentId));
  url += `?occurrence_id=${occurrenceId}`; // Append query param safely

  const response = await apiClient.fetch(url, {
    method: "POST",
    body: formData,
  });

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
  const url = getUrl(
    API_CONFIG.ENDPOINTS.OCCURRENCES.DELETE(incidentId, occurrenceId),
  );
  const response = await apiClient.delete(url);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to delete occurrence: ${response.status}`,
    );
  }
}
