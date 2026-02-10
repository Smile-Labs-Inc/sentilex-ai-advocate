/**
 * Evidence API Service
 *
 * Handles communication with the backend evidence API for cross-incident evidence management.
 */

import { API_BASE_URL, APP_CONFIG } from "../config";

// Types matching backend schemas
export interface EvidenceItem {
  id: number;
  incident_id: number;
  occurrence_id: number | null;
  file_name: string;
  file_path: string;
  file_type: string | null;
  file_size: number | null;
  uploaded_at: string;
  description: string | null;
  incident_title: string;
  incident_type: string;
  incident_status: string;
  thumbnail_url?: string | null;
}

export interface EvidenceListResponse {
  evidence: EvidenceItem[];
  total: number;
}

export interface EvidenceFilters {
  incident_id?: number;
  file_type?: string;
  date_from?: string; // YYYY-MM-DD
  date_to?: string; // YYYY-MM-DD
  search?: string;
}

/**
 * Get the auth token from localStorage.
 */
function getAuthToken(): string | null {
  return localStorage.getItem(APP_CONFIG.TOKEN_STORAGE_KEY);
}

/**
 * Get all evidence files for the current user across all incidents.
 */
export async function getAllEvidence(
  filters?: EvidenceFilters,
): Promise<EvidenceListResponse> {
  const token = getAuthToken();

  if (!token) {
    throw new Error("User is not authenticated");
  }

  // Build query string from filters
  const params = new URLSearchParams();
  if (filters?.incident_id) {
    params.append("incident_id", filters.incident_id.toString());
  }
  if (filters?.file_type) {
    params.append("file_type", filters.file_type);
  }
  if (filters?.date_from) {
    params.append("date_from", filters.date_from);
  }
  if (filters?.date_to) {
    params.append("date_to", filters.date_to);
  }
  if (filters?.search) {
    params.append("search", filters.search);
  }

  const queryString = params.toString();
  const url = `${API_BASE_URL}/evidence/${queryString ? `?${queryString}` : ""}`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to fetch evidence: ${response.status}`,
    );
  }

  return response.json();
}

/**
 * Get a specific evidence file by ID.
 */
export async function getEvidenceById(
  evidenceId: number,
): Promise<EvidenceItem> {
  const token = getAuthToken();

  if (!token) {
    throw new Error("User is not authenticated");
  }

  const response = await fetch(`${API_BASE_URL}/evidence/${evidenceId}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

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
export async function deleteEvidenceById(evidenceId: number): Promise<void> {
  const token = getAuthToken();

  if (!token) {
    throw new Error("User is not authenticated");
  }

  const response = await fetch(`${API_BASE_URL}/evidence/${evidenceId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to delete evidence: ${response.status}`,
    );
  }
}

/**
 * Get download URL for evidence file.
 */
export function getEvidenceDownloadUrl(evidenceId: number): string {
  const token = getAuthToken();
  return `${API_BASE_URL}/evidence/${evidenceId}/download?token=${token}`;
}

/**
 * Get preview URL for evidence file.
 */
export function getEvidencePreviewUrl(evidenceId: number): string {
  const token = getAuthToken();
  return `${API_BASE_URL}/evidence/${evidenceId}/preview?token=${token}`;
}

/**
 * Download evidence file directly - gets presigned URL from API then redirects to S3.
 */
export async function downloadEvidence(evidenceId: number): Promise<void> {
  const token = getAuthToken();

  if (!token) {
    throw new Error("User is not authenticated");
  }

  try {
    const response = await fetch(`${API_BASE_URL}/evidence/${evidenceId}/download`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `Failed to get download URL: ${response.status}`,
      );
    }

    const data: { download_url: string } = await response.json();

    // Redirect to the presigned S3 URL
    window.location.href = data.download_url;
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Failed to download evidence';
    throw new Error(errorMessage);
  }
}

/**
 * Upload evidence files for a specific incident.
 */
export async function uploadEvidenceToIncident(
  incidentId: number,
  files: File[],
): Promise<any> {
  const token = getAuthToken();

  if (!token) {
    throw new Error("User is not authenticated");
  }

  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });

  const endpoint = `${API_BASE_URL}/incidents/${incidentId}/evidence`;
  const headers = {
    Authorization: `Bearer ${token}`,
  };

  const response = await fetch(endpoint, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to upload evidence: ${response.status}`,
    );
  }

  const result = await response.json();
  return result;
}
