// =============================================================================
// Lawyer Service
// API calls for lawyer-related data
// =============================================================================

export interface Lawyer {
  id: number;
  name: string;
  specialties: string;
  rating: number;
  reviews_count: number;
  availability: string;
  experience_years: number;
  email: string;
  phone: string;
  district: string;
}

import { API_BASE_URL } from "../config";

/**
 * Fetches lawyers from the backend API
 * @param specialty - Optional specialty filter
 * @returns Promise resolving to an array of lawyers
 * @throws Error if the fetch fails
 */
export async function fetchLawyers(specialty?: string): Promise<Lawyer[]> {
  try {
    const url = new URL(`${API_BASE_URL}/lawyers/`);

    if (specialty && specialty !== "All") {
      url.searchParams.append("specialty", specialty);
    }

    const response = await fetch(url.toString());

    if (!response.ok) {
      throw new Error(`Failed to fetch lawyers: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (err) {
    if (err instanceof Error) {
      throw new Error(`Failed to fetch lawyers: ${err.message}`);
    }
    throw new Error("Failed to fetch lawyers: Unknown error");
  }
}
