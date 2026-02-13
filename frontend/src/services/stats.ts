/**
 * Stats API Service
 *
 * Handles communication with the backend statistics API.
 */

import { API_CONFIG } from "../config";
import { apiClient } from "./apiClient";

// Types matching backend schemas
export interface UserStatsResponse {
  pending_reports: number;
  total_reports: number;
  resolved_cases: number;
  in_progress_cases: number;
}

export interface GlobalStatsResponse {
  total_cases_solved: number;
  active_users: number;
  affiliated_lawyers: number;
  case_types_handled: number;
}

/**
 * Get statistics for the current user.
 */
export async function getUserStats(): Promise<UserStatsResponse> {
  const response = await apiClient.get(
    `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.STATS.USER}`,
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to fetch user stats: ${response.status}`,
    );
  }

  return response.json();
}

/**
 * Get platform-wide statistics.
 */
export async function getGlobalStats(): Promise<GlobalStatsResponse> {
  const response = await apiClient.get(
    `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.STATS.GLOBAL}`,
    {
      skipAuth: true, // Global stats don't require authentication
    },
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to fetch global stats: ${response.status}`,
    );
  }

  return response.json();
}
