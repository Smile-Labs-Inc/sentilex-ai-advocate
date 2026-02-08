/**
 * useEvidenceVault Hook
 *
 * Manages state for the Evidence Vault page including fetching, filtering, and deleting evidence.
 */

import { useState, useEffect, useCallback } from "preact/hooks";
import {
  getAllEvidence,
  deleteEvidenceById,
  type EvidenceItem,
  type EvidenceFilters,
} from "../services/evidence";

export interface UseEvidenceVaultReturn {
  evidence: EvidenceItem[];
  isLoading: boolean;
  error: string | null;
  totalCount: number;
  filters: EvidenceFilters;
  setFilters: (filters: EvidenceFilters) => void;
  deleteEvidence: (id: number) => Promise<void>;
  refreshEvidence: () => Promise<void>;
}

export function useEvidenceVault(): UseEvidenceVaultReturn {
  const [evidence, setEvidence] = useState<EvidenceItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [filters, setFilters] = useState<EvidenceFilters>({});

  const fetchEvidence = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await getAllEvidence(filters);
      setEvidence(response.evidence);
      setTotalCount(response.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load evidence");
      console.error("Error fetching evidence:", err);
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchEvidence();
  }, [fetchEvidence]);

  const deleteEvidence = async (id: number) => {
    try {
      await deleteEvidenceById(id);
      // Refresh the list after deletion
      await fetchEvidence();
    } catch (err) {
      throw new Error(
        err instanceof Error ? err.message : "Failed to delete evidence",
      );
    }
  };

  const refreshEvidence = async () => {
    await fetchEvidence();
  };

  return {
    evidence,
    isLoading,
    error,
    totalCount,
    filters,
    setFilters,
    deleteEvidence,
    refreshEvidence,
  };
}
