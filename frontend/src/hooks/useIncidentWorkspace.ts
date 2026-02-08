// =============================================================================
// useIncidentWorkspace Hook
// Manages state for the incident workspace page
// =============================================================================

import { useState, useCallback, useEffect } from "preact/hooks";
import type {
  IncidentDraft,
  TimelineEventEditable,
  Evidence,
  LawViolation,
  EvidenceType,
  IncidentType,
  Incident,
  ChatMessage,
} from "../types";
import type { WizardData } from "../components/organisms/OnboardingWizard/OnboardingWizard";
import {
  createIncident,
  type IncidentCreate,
  sendIncidentChatMessage,
  getIncidentChatMessages,
  uploadEvidence as uploadEvidenceAPI,
  getIncidentEvidence,
  deleteEvidence as deleteEvidenceAPI,
  getOccurrences,
} from "../services/incident";

// Helper to generate unique IDs
const generateId = () => Math.random().toString(36).substring(2, 11);

// Helper to determine evidence type from file
const getEvidenceType = (mimeType: string): EvidenceType => {
  if (mimeType.startsWith("image/")) return "image";
  if (mimeType.startsWith("video/")) return "video";
  if (mimeType.startsWith("audio/")) return "audio";
  if (
    mimeType.includes("pdf") ||
    mimeType.includes("document") ||
    mimeType.includes("text")
  ) {
    return "document";
  }
  return "other";
};

// Mock laws data (would come from MCP server in production)
const mockLaws: LawViolation[] = [
  {
    id: "1",
    name: "Computer Crimes Act No. 24 of 2007",
    section: "Section 6",
    description:
      "Illegal interception of data - Whoever intentionally and without lawful authority intercepts by technical means, any non-public transmission of computer data to, from or within a computer system.",
    jurisdiction: "Sri Lanka",
    severity: "high",
    isViolated: true,
    confidence: 85,
    includedInReport: true,
  },
  {
    id: "2",
    name: "Penal Code of Sri Lanka",
    section: "Section 345",
    description:
      "Criminal intimidation - Whoever threatens another with any injury to his person, reputation or property, or to the person or reputation of anyone in whom that person is interested, with intent to cause alarm.",
    jurisdiction: "Sri Lanka",
    severity: "critical",
    isViolated: true,
    confidence: 92,
    includedInReport: true,
  },
  {
    id: "3",
    name: "Computer Crimes Act No. 24 of 2007",
    section: "Section 3",
    description:
      "Unauthorized access to a computer - Whoever intentionally and without lawful authority accesses the whole or any part of a computer system.",
    jurisdiction: "Sri Lanka",
    severity: "medium",
    isViolated: false,
    confidence: 45,
    includedInReport: false,
  },
];

export interface UseIncidentWorkspaceReturn {
  incident: IncidentDraft;
  isAnalyzing: boolean;

  // Timeline operations
  addTimelineEvent: (event: Omit<TimelineEventEditable, "id">) => void;
  updateTimelineEvent: (event: TimelineEventEditable) => void;
  deleteTimelineEvent: (eventId: string) => void;
  acceptSuggestion: (eventId: string) => void;

  // Evidence operations
  addEvidence: (files: File[]) => void;
  deleteEvidence: (evidence: Evidence) => void;
  updateEvidenceDescription: (evidenceId: string, description: string) => void;

  // Laws operations
  toggleLawIncluded: (lawId: string, included: boolean) => void;

  // Submission
  canSubmit: boolean;
  submitToPolice: () => Promise<void>;
  saveDraft: () => Promise<void>;

  // Chat
  sendMessage: (message: string) => void;
  chatMessages: ChatMessage[];
  isChatLoading: boolean;
  refreshIncident: () => Promise<void>;
}

export function useIncidentWorkspace(
  wizardData?: WizardData,
  existingIncident?: Incident,
): UseIncidentWorkspaceReturn {
  // Initialize incident from existing incident, wizard data, or create empty
  const [incident, setIncident] = useState<IncidentDraft>(() => {
    const now = new Date();

    // If we have an existing incident, convert it to IncidentDraft format
    if (existingIncident) {
      return {
        id: existingIncident.id,
        type: existingIncident.type,
        title: existingIncident.title,
        description: existingIncident.description || "",
        dateOccurred: new Date(existingIncident.createdAt),
        platformsInvolved: [],
        perpetratorInfo: undefined,
        timeline: [
          {
            id: generateId(),
            type: "incident",
            title: "Incident Reported",
            description: existingIncident.description || "",
            timestamp: new Date(existingIncident.createdAt),
          },
        ],
        evidence: [],
        identifiedLaws: [],
        status: "draft",
        createdAt: new Date(existingIncident.createdAt),
        updatedAt: new Date(existingIncident.updatedAt),
      };
    }

    // Otherwise use wizard data or create empty
    return {
      id: generateId(),
      type: (wizardData?.incidentType as IncidentType) || "other",
      title: wizardData?.title || "New Incident",
      description: wizardData?.description || "",
      dateOccurred: wizardData?.dateOccurred
        ? new Date(wizardData.dateOccurred)
        : now,
      platformsInvolved:
        wizardData?.platformsInvolved
          ?.split(",")
          .map((p) => p.trim())
          .filter(Boolean) || [],
      perpetratorInfo: wizardData?.perpetratorInfo,
      timeline: [
        {
          id: generateId(),
          type: "incident",
          title: "Incident Reported",
          description:
            wizardData?.description ||
            "Case created through the incident wizard.",
          timestamp: now,
        },
      ],
      evidence: [],
      identifiedLaws: [],
      status: "draft",
      createdAt: now,
      updatedAt: now,
    };
  });

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [incidentId, setIncidentId] = useState<number | null>(() => {
    if (existingIncident) {
      return parseInt(existingIncident.id.replace("inc_", ""), 10);
    }
    return null;
  });

  // Automatically create incident in database when wizard data is provided
  // Load existing data (exposed as refreshIncident)
  const loadIncidentData = useCallback(async () => {
    if (!incidentId) return;

    try {
      setIsAnalyzing(true);
      // Load evidence
      const evidenceData = await getIncidentEvidence(incidentId);
      const formattedEvidence: Evidence[] = evidenceData.evidence.map((e) => ({
        id: e.id.toString(),
        fileName: e.file_name,
        fileSize: e.file_size || 0,
        fileType: getEvidenceTypeFromMime(e.file_type || ""),
        mimeType: e.file_type || "",
        uploadedAt: new Date(e.uploaded_at),
        description: "",
        isEncrypted: false,
        thumbnailUrl: e.file_path,
      }));

      // Load chat messages
      const messages = await getIncidentChatMessages(incidentId);
      const formattedMessages: ChatMessage[] = messages.map((msg) => ({
        id: msg.id.toString(),
        role: msg.role as "user" | "assistant",
        content: msg.content,
        timestamp: new Date(msg.created_at),
      }));
      setChatMessages(formattedMessages);

      // Load occurrences and map to timeline
      const occurrencesResponse = await getOccurrences(incidentId);
      const occurrences = occurrencesResponse.occurrences;

      const occurrenceEvents: TimelineEventEditable[] = occurrences.map(
        (occ) => ({
          id: `occ_${occ.id}`,
          type: "incident",
          title: occ.title,
          description: occ.description,
          timestamp: new Date(occ.date_occurred),
        }),
      );

      setIncident((prev) => {
        // Filter out previous occurrence events to avoid duplicates
        const baseTimeline = prev.timeline.filter(
          (t) => !t.id.startsWith("occ_"),
        );
        const newTimeline = [...baseTimeline, ...occurrenceEvents].sort(
          (a, b) => a.timestamp.getTime() - b.timestamp.getTime(),
        );

        return {
          ...prev,
          evidence: formattedEvidence,
          timeline: newTimeline,
          updatedAt: new Date(),
        };
      });
    } catch (error) {
      console.error("Failed to load incident data:", error);
    } finally {
      setIsAnalyzing(false);
    }
  }, [incidentId]);

  // Automatically create incident in database when wizard data is provided
  useEffect(() => {
    if (wizardData && !incidentId && !existingIncident) {
      // Create incident immediately after wizard completion
      const createInitialIncident = async () => {
        try {
          const dateOccurred = wizardData.dateOccurred
            ? new Date(wizardData.dateOccurred).toISOString().split("T")[0]
            : null;

          const incidentData: IncidentCreate = {
            incident_type: wizardData.incidentType as any,
            title: wizardData.title,
            description: wizardData.description,
            date_occurred: dateOccurred,
            location: wizardData.location || null,
            jurisdiction: "Sri Lanka",
            platforms_involved: wizardData.platformsInvolved || null,
            perpetrator_info: wizardData.perpetrator_info || null,
            evidence_notes: null,
          };

          console.log("Creating incident with data:", incidentData);
          const response = await createIncident(incidentData);
          console.log("Incident created successfully:", response);

          // Store incident ID for future API calls
          setIncidentId(response.id);
        } catch (error) {
          console.error("Failed to create incident:", error);
          // alert("Failed to create incident. Please try again.");
        }
      };

      createInitialIncident();
    } else if (existingIncident && incidentId) {
      loadIncidentData();
    }
  }, [wizardData, incidentId, existingIncident, loadIncidentData]);

  // Simulate AI analysis after a delay
  useState(() => {
    const timer = setTimeout(() => {
      setIsAnalyzing(true);

      // Simulate analysis taking time
      setTimeout(() => {
        setIncident((prev) => ({
          ...prev,
          identifiedLaws: mockLaws,
          status: "analyzing",
          updatedAt: new Date(),
        }));

        // Add AI suggestion to timeline
        setTimeout(() => {
          setIncident((prev) => ({
            ...prev,
            timeline: [
              ...prev.timeline,
              {
                id: generateId(),
                type: "ai-suggestion",
                title: "AI Analysis Complete",
                description: `Identified ${mockLaws.filter((l) => l.isViolated).length} potential law violations based on your report.`,
                timestamp: new Date(),
                isAISuggested: true,
              },
            ],
            status: "ready",
            updatedAt: new Date(),
          }));
          setIsAnalyzing(false);
        }, 1500);
      }, 2000);
    }, 1000);

    return () => clearTimeout(timer);
  });

  // Timeline operations
  const addTimelineEvent = useCallback(
    (event: Omit<TimelineEventEditable, "id">) => {
      setIncident((prev) => ({
        ...prev,
        timeline: [...prev.timeline, { ...event, id: generateId() }],
        updatedAt: new Date(),
      }));
    },
    [],
  );

  const updateTimelineEvent = useCallback((event: TimelineEventEditable) => {
    setIncident((prev) => ({
      ...prev,
      timeline: prev.timeline.map((e) => (e.id === event.id ? event : e)),
      updatedAt: new Date(),
    }));
  }, []);

  const deleteTimelineEvent = useCallback((eventId: string) => {
    setIncident((prev) => ({
      ...prev,
      timeline: prev.timeline.filter((e) => e.id !== eventId),
      updatedAt: new Date(),
    }));
  }, []);

  const acceptSuggestion = useCallback((eventId: string) => {
    setIncident((prev) => ({
      ...prev,
      timeline: prev.timeline.map((e) =>
        e.id === eventId ? { ...e, isAISuggested: false } : e,
      ),
      updatedAt: new Date(),
    }));
  }, []);

  // Evidence operations
  const addEvidence = useCallback(
    async (files: File[]) => {
      if (!incidentId) {
        console.error("No incident ID available");
        return;
      }

      try {
        // Upload files to backend
        const uploadedEvidence = await uploadEvidenceAPI(incidentId, files);

        // Convert to frontend format
        const newEvidence: Evidence[] = uploadedEvidence.map((e) => ({
          id: e.id.toString(),
          fileName: e.file_name,
          fileSize: e.file_size || 0,
          fileType: getEvidenceTypeFromMime(e.file_type || ""),
          mimeType: e.file_type || "",
          uploadedAt: new Date(e.uploaded_at),
          isEncrypted: true,
        }));

        setIncident((prev) => ({
          ...prev,
          evidence: [...prev.evidence, ...newEvidence],
          timeline: [
            ...prev.timeline,
            {
              id: generateId(),
              type: "evidence",
              title: "Evidence Uploaded",
              description: `${files.length} file${files.length > 1 ? "s" : ""} added to the case.`,
              timestamp: new Date(),
              linkedEvidenceIds: newEvidence.map((e) => e.id),
            },
          ],
          updatedAt: new Date(),
        }));
      } catch (error) {
        console.error("Failed to upload evidence:", error);
        alert("Failed to upload evidence. Please try again.");
      }
    },
    [incidentId],
  );

  const deleteEvidence = useCallback(
    async (evidence: Evidence) => {
      if (!incidentId) {
        console.error("No incident ID available");
        return;
      }

      try {
        await deleteEvidenceAPI(incidentId, parseInt(evidence.id));

        setIncident((prev) => ({
          ...prev,
          evidence: prev.evidence.filter((e) => e.id !== evidence.id),
          updatedAt: new Date(),
        }));
      } catch (error) {
        console.error("Failed to delete evidence:", error);
        alert("Failed to delete evidence. Please try again.");
      }
    },
    [incidentId],
  );

  const updateEvidenceDescription = useCallback(
    (evidenceId: string, description: string) => {
      setIncident((prev) => ({
        ...prev,
        evidence: prev.evidence.map((e) =>
          e.id === evidenceId ? { ...e, description } : e,
        ),
        updatedAt: new Date(),
      }));
    },
    [],
  );

  // Laws operations
  const toggleLawIncluded = useCallback((lawId: string, included: boolean) => {
    setIncident((prev) => ({
      ...prev,
      identifiedLaws: prev.identifiedLaws.map((l) =>
        l.id === lawId ? { ...l, includedInReport: included } : l,
      ),
      updatedAt: new Date(),
    }));
  }, []);

  // Load chat messages when incident ID is available
  useEffect(() => {
    if (incidentId) {
      loadChatMessages();
      loadEvidence();
    }
  }, [incidentId]);

  const loadChatMessages = async () => {
    if (!incidentId) return;

    try {
      const messages = await getIncidentChatMessages(incidentId);
      const formattedMessages: ChatMessage[] = messages.map((msg) => ({
        id: msg.id.toString(),
        role: msg.role as "user" | "assistant",
        content: msg.content,
        timestamp: new Date(msg.created_at),
      }));
      setChatMessages(formattedMessages);
    } catch (error) {
      console.error("Failed to load chat messages:", error);
    }
  };

  const loadEvidence = async () => {
    if (!incidentId) return;

    try {
      const response = await getIncidentEvidence(incidentId);
      const formattedEvidence: Evidence[] = response.evidence.map((e) => ({
        id: e.id.toString(),
        fileName: e.file_name,
        fileSize: e.file_size || 0,
        fileType: getEvidenceTypeFromMime(e.file_type || ""),
        mimeType: e.file_type || "",
        uploadedAt: new Date(e.uploaded_at),
        isEncrypted: true,
      }));

      setIncident((prev) => ({
        ...prev,
        evidence: formattedEvidence,
        updatedAt: new Date(),
      }));
    } catch (error) {
      console.error("Failed to load evidence:", error);
    }
  };

  const getEvidenceTypeFromMime = (mimeType: string): EvidenceType => {
    if (mimeType.startsWith("image/")) return "image";
    if (mimeType.startsWith("video/")) return "video";
    if (mimeType.startsWith("audio/")) return "audio";
    if (
      mimeType.includes("pdf") ||
      mimeType.includes("document") ||
      mimeType.includes("text")
    ) {
      return "document";
    }
    return "other";
  };

  // Chat operations
  const sendMessage = useCallback(
    async (message: string) => {
      if (!incidentId) {
        console.error("No incident ID available");
        return;
      }

      // Add user message to UI immediately
      const userMessage: ChatMessage = {
        id: generateId(),
        role: "user",
        content: message,
        timestamp: new Date(),
      };
      setChatMessages((prev) => [...prev, userMessage]);
      setIsChatLoading(true);

      try {
        // Send message to backend and get AI response
        const response = await sendIncidentChatMessage(incidentId, message);

        // Add AI response to UI
        const aiMessage: ChatMessage = {
          id: response.assistant_message.id.toString(),
          role: "assistant",
          content: response.assistant_message.content,
          timestamp: new Date(response.assistant_message.created_at),
        };

        setChatMessages((prev) => [
          ...prev.slice(0, -1), // Remove temporary user message
          {
            id: response.user_message.id.toString(),
            role: "user",
            content: response.user_message.content,
            timestamp: new Date(response.user_message.created_at),
          },
          aiMessage,
        ]);
      } catch (error) {
        console.error("Failed to send message:", error);
        // Add error message
        const errorMessage: ChatMessage = {
          id: generateId(),
          role: "assistant",
          content:
            "Sorry, I encountered an error processing your message. Please try again.",
          timestamp: new Date(),
        };
        setChatMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsChatLoading(false);
      }
    },
    [incidentId],
  );

  // Submission
  const canSubmit =
    incident.identifiedLaws.some((l) => l.isViolated) &&
    incident.evidence.length > 0 &&
    incident.identifiedLaws.some((l) => l.includedInReport);

  // Save draft to backend
  const saveDraft = useCallback(async () => {
    try {
      // Convert date to YYYY-MM-DD format (date only, not datetime)
      const dateOccurred = incident.timeline[0]?.timestamp
        ? incident.timeline[0].timestamp.toISOString().split("T")[0]
        : null;

      const incidentData: IncidentCreate = {
        incident_type: incident.type,
        title: incident.title,
        description: incident.description,
        date_occurred: dateOccurred,
        location: null,
        jurisdiction: "Sri Lanka",
        platforms_involved: incident.platformsInvolved.join(", ") || null,
        perpetrator_info: incident.perpetratorInfo || null,
        evidence_notes:
          incident.evidence
            .map((e) => `${e.fileName}: ${e.description || "No description"}`)
            .join("\n") || null,
      };

      const response = await createIncident(incidentData);

      setIncident((prev) => ({
        ...prev,
        id: `inc_${response.id}`,
        status: "draft",
        updatedAt: new Date(),
      }));

      // Store incident ID for future API calls
      setIncidentId(response.id);

      alert("Draft saved successfully!");
    } catch (error) {
      console.error("Failed to save draft:", error);
      alert("Failed to save draft. Please try again.");
    }
  }, [incident]);

  // Submit to police (creates or updates incident with submitted status)
  const submitToPolice = useCallback(async () => {
    try {
      const incidentData: IncidentCreate = {
        incident_type: incident.type,
        title: incident.title,
        description: `${incident.description}\n\n## Identified Laws:\n${incident.identifiedLaws
          .filter((l) => l.includedInReport)
          .map((l) => `- ${l.name}, ${l.section}: ${l.description}`)
          .join("\n")}`,
        date_occurred: incident.timeline[0]?.timestamp.toISOString() || null,
        location: null,
        jurisdiction: "Sri Lanka",
        platforms_involved: incident.platformsInvolved.join(", ") || null,
        perpetrator_info: incident.perpetratorInfo || null,
        evidence_notes:
          incident.evidence
            .map((e) => `${e.fileName}: ${e.description || "No description"}`)
            .join("\n") || null,
      };

      const response = await createIncident(incidentData);

      setIncident((prev) => ({
        ...prev,
        id: `inc_${response.id}`,
        status: "submitted",
        updatedAt: new Date(),
        timeline: [
          ...prev.timeline,
          {
            id: generateId(),
            type: "report",
            title: "Submitted to Police",
            description:
              "Your case has been submitted to the Sri Lanka Computer Crimes Division for review.",
            timestamp: new Date(),
          },
        ],
      }));

      alert("Successfully submitted to police!");
    } catch (error) {
      console.error("Failed to submit to police:", error);
      alert("Failed to submit. Please try again.");
    }
  }, [incident]);

  return {
    incident,
    isAnalyzing,
    addTimelineEvent,
    updateTimelineEvent,
    deleteTimelineEvent,
    acceptSuggestion,
    addEvidence,
    deleteEvidence,
    updateEvidenceDescription,
    toggleLawIncluded,
    canSubmit,
    submitToPolice,
    saveDraft,
    sendMessage,
    chatMessages,
    isChatLoading,
    refreshIncident: loadIncidentData,
  };
}

export default useIncidentWorkspace;
