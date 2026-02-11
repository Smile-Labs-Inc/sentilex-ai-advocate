/**
 * Documents Service
 *
 * API service for generating and downloading case documents (PDFs, ZIPs).
 */

import { APP_CONFIG } from "../config";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8001";

/**
 * Get authentication token from localStorage.
 */
function getAuthToken(): string | null {
  return localStorage.getItem(APP_CONFIG.TOKEN_STORAGE_KEY);
}

/**
 * Download a file from a blob response.
 */
function downloadBlob(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

/**
 * Export police statement PDF for an incident.
 */
export async function exportPoliceStatement(incidentId: number): Promise<void> {
  const token = getAuthToken();

  if (!token) {
    throw new Error("User is not authenticated");
  }

  const response = await fetch(
    `${API_BASE_URL}/documents/incidents/${incidentId}/export/police-statement`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail ||
        `Failed to export police statement: ${response.status}`,
    );
  }

  const blob = await response.blob();
  const filename = `Police_Statement_${incidentId}_${new Date().toISOString().split("T")[0]}.pdf`;
  downloadBlob(blob, filename);
}

/**
 * Export CERT technical report PDF for an incident.
 */
export async function exportCERTReport(incidentId: number): Promise<void> {
  const token = getAuthToken();

  if (!token) {
    throw new Error("User is not authenticated");
  }

  const response = await fetch(
    `${API_BASE_URL}/documents/incidents/${incidentId}/export/cert-report`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to export CERT report: ${response.status}`,
    );
  }

  const blob = await response.blob();
  const filename = `CERT_Report_${incidentId}_${new Date().toISOString().split("T")[0]}.pdf`;
  downloadBlob(blob, filename);
}

/**
 * Export evidence manifest PDF for an incident.
 */
export async function exportEvidenceManifest(
  incidentId: number,
): Promise<void> {
  const token = getAuthToken();

  if (!token) {
    throw new Error("User is not authenticated");
  }

  const response = await fetch(
    `${API_BASE_URL}/documents/incidents/${incidentId}/export/evidence-manifest`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail ||
        `Failed to export evidence manifest: ${response.status}`,
    );
  }

  const blob = await response.blob();
  const filename = `Evidence_Manifest_${incidentId}_${new Date().toISOString().split("T")[0]}.pdf`;
  downloadBlob(blob, filename);
}

/**
 * Export complete case file (ZIP) for an incident.
 */
export async function exportCaseFile(incidentId: number): Promise<void> {
  const token = getAuthToken();

  if (!token) {
    throw new Error("User is not authenticated");
  }

  const response = await fetch(
    `${API_BASE_URL}/documents/incidents/${incidentId}/export/case-file`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to export case file: ${response.status}`,
    );
  }

  const blob = await response.blob();
  const filename = `Case_File_${incidentId}_${new Date().toISOString().split("T")[0]}.zip`;
  downloadBlob(blob, filename);
}
