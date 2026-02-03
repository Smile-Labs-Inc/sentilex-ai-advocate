// =============================================================================
// useIncidentWorkspace Hook
// Manages state for the incident workspace page
// =============================================================================

import { useState, useCallback } from 'preact/hooks';
import type {
    IncidentDraft,
    TimelineEventEditable,
    Evidence,
    LawViolation,
    EvidenceType,
    IncidentType
} from '../types';
import type { WizardData } from '../components/organisms/OnboardingWizard/OnboardingWizard';
import { createIncident, type IncidentCreate } from '../services/incident';

// Helper to generate unique IDs
const generateId = () => Math.random().toString(36).substring(2, 11);

// Helper to determine evidence type from file
const getEvidenceType = (mimeType: string): EvidenceType => {
    if (mimeType.startsWith('image/')) return 'image';
    if (mimeType.startsWith('video/')) return 'video';
    if (mimeType.startsWith('audio/')) return 'audio';
    if (mimeType.includes('pdf') || mimeType.includes('document') || mimeType.includes('text')) {
        return 'document';
    }
    return 'other';
};

// Mock laws data (would come from MCP server in production)
const mockLaws: LawViolation[] = [
    {
        id: '1',
        name: 'Computer Crimes Act No. 24 of 2007',
        section: 'Section 6',
        description: 'Illegal interception of data - Whoever intentionally and without lawful authority intercepts by technical means, any non-public transmission of computer data to, from or within a computer system.',
        jurisdiction: 'Sri Lanka',
        severity: 'high',
        isViolated: true,
        confidence: 85,
        includedInReport: true,
    },
    {
        id: '2',
        name: 'Penal Code of Sri Lanka',
        section: 'Section 345',
        description: 'Criminal intimidation - Whoever threatens another with any injury to his person, reputation or property, or to the person or reputation of anyone in whom that person is interested, with intent to cause alarm.',
        jurisdiction: 'Sri Lanka',
        severity: 'critical',
        isViolated: true,
        confidence: 92,
        includedInReport: true,
    },
    {
        id: '3',
        name: 'Computer Crimes Act No. 24 of 2007',
        section: 'Section 3',
        description: 'Unauthorized access to a computer - Whoever intentionally and without lawful authority accesses the whole or any part of a computer system.',
        jurisdiction: 'Sri Lanka',
        severity: 'medium',
        isViolated: false,
        confidence: 45,
        includedInReport: false,
    },
];

export interface UseIncidentWorkspaceReturn {
    incident: IncidentDraft;
    isAnalyzing: boolean;

    // Timeline operations
    addTimelineEvent: (event: Omit<TimelineEventEditable, 'id'>) => void;
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
}

export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

export function useIncidentWorkspace(wizardData?: WizardData): UseIncidentWorkspaceReturn {
    // Initialize incident from wizard data or create empty
    const [incident, setIncident] = useState<IncidentDraft>(() => {
        const now = new Date();
        return {
            id: generateId(),
            type: (wizardData?.incidentType as IncidentType) || 'other',
            title: wizardData?.title || 'New Incident',
            description: wizardData?.description || '',
            dateOccurred: wizardData?.dateOccurred ? new Date(wizardData.dateOccurred) : now,
            platformsInvolved: wizardData?.platformsInvolved?.split(',').map(p => p.trim()).filter(Boolean) || [],
            perpetratorInfo: wizardData?.perpetratorInfo,
            timeline: [
                {
                    id: generateId(),
                    type: 'incident',
                    title: 'Incident Reported',
                    description: wizardData?.description || 'Case created through the incident wizard.',
                    timestamp: now,
                },
            ],
            evidence: [],
            identifiedLaws: [],
            status: 'draft',
            createdAt: now,
            updatedAt: now,
        };
    });

    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
        {
            id: '1',
            role: 'assistant',
            content: `Hello! I'm your AI Legal Assistant. I've reviewed your initial report about "${incident.title}". I'll help you document this incident thoroughly and identify applicable laws.\n\nTo get started, could you tell me more about when this first began happening?`,
            timestamp: new Date(),
        },
    ]);
    const [isChatLoading, setIsChatLoading] = useState(false);

    // Simulate AI analysis after a delay
    useState(() => {
        const timer = setTimeout(() => {
            setIsAnalyzing(true);

            // Simulate analysis taking time
            setTimeout(() => {
                setIncident(prev => ({
                    ...prev,
                    identifiedLaws: mockLaws,
                    status: 'analyzing',
                    updatedAt: new Date(),
                }));

                // Add AI suggestion to timeline
                setTimeout(() => {
                    setIncident(prev => ({
                        ...prev,
                        timeline: [
                            ...prev.timeline,
                            {
                                id: generateId(),
                                type: 'ai-suggestion',
                                title: 'AI Analysis Complete',
                                description: `Identified ${mockLaws.filter(l => l.isViolated).length} potential law violations based on your report.`,
                                timestamp: new Date(),
                                isAISuggested: true,
                            },
                        ],
                        status: 'ready',
                        updatedAt: new Date(),
                    }));
                    setIsAnalyzing(false);
                }, 1500);
            }, 2000);
        }, 1000);

        return () => clearTimeout(timer);
    });

    // Timeline operations
    const addTimelineEvent = useCallback((event: Omit<TimelineEventEditable, 'id'>) => {
        setIncident(prev => ({
            ...prev,
            timeline: [...prev.timeline, { ...event, id: generateId() }],
            updatedAt: new Date(),
        }));
    }, []);

    const updateTimelineEvent = useCallback((event: TimelineEventEditable) => {
        setIncident(prev => ({
            ...prev,
            timeline: prev.timeline.map(e => e.id === event.id ? event : e),
            updatedAt: new Date(),
        }));
    }, []);

    const deleteTimelineEvent = useCallback((eventId: string) => {
        setIncident(prev => ({
            ...prev,
            timeline: prev.timeline.filter(e => e.id !== eventId),
            updatedAt: new Date(),
        }));
    }, []);

    const acceptSuggestion = useCallback((eventId: string) => {
        setIncident(prev => ({
            ...prev,
            timeline: prev.timeline.map(e =>
                e.id === eventId ? { ...e, isAISuggested: false } : e
            ),
            updatedAt: new Date(),
        }));
    }, []);

    // Evidence operations
    const addEvidence = useCallback((files: File[]) => {
        const newEvidence: Evidence[] = files.map(file => ({
            id: generateId(),
            fileName: file.name,
            fileSize: file.size,
            fileType: getEvidenceType(file.type),
            mimeType: file.type,
            uploadedAt: new Date(),
            isEncrypted: true,
        }));

        setIncident(prev => ({
            ...prev,
            evidence: [...prev.evidence, ...newEvidence],
            timeline: [
                ...prev.timeline,
                {
                    id: generateId(),
                    type: 'evidence',
                    title: 'Evidence Uploaded',
                    description: `${files.length} file${files.length > 1 ? 's' : ''} added to the case.`,
                    timestamp: new Date(),
                    linkedEvidenceIds: newEvidence.map(e => e.id),
                },
            ],
            updatedAt: new Date(),
        }));
    }, []);

    const deleteEvidence = useCallback((evidence: Evidence) => {
        setIncident(prev => ({
            ...prev,
            evidence: prev.evidence.filter(e => e.id !== evidence.id),
            updatedAt: new Date(),
        }));
    }, []);

    const updateEvidenceDescription = useCallback((evidenceId: string, description: string) => {
        setIncident(prev => ({
            ...prev,
            evidence: prev.evidence.map(e =>
                e.id === evidenceId ? { ...e, description } : e
            ),
            updatedAt: new Date(),
        }));
    }, []);

    // Laws operations
    const toggleLawIncluded = useCallback((lawId: string, included: boolean) => {
        setIncident(prev => ({
            ...prev,
            identifiedLaws: prev.identifiedLaws.map(l =>
                l.id === lawId ? { ...l, includedInReport: included } : l
            ),
            updatedAt: new Date(),
        }));
    }, []);

    // Chat operations
    const sendMessage = useCallback((message: string) => {
        const userMessage: ChatMessage = {
            id: generateId(),
            role: 'user',
            content: message,
            timestamp: new Date(),
        };
        setChatMessages(prev => [...prev, userMessage]);
        setIsChatLoading(true);

        // Simulate AI response
        setTimeout(() => {
            const responses: Record<string, string> = {
                default: `Thank you for that information. Based on what you've shared, this appears to strengthen the case under the Computer Crimes Act No. 24 of 2007. Would you like me to add this to your timeline?`,
                evidence: `I recommend collecting and uploading any screenshots or messages that document this behavior. Would you like tips on how to properly capture digital evidence?`,
                legal: `In Sri Lanka, cyber crimes can be reported to the Computer Crimes Division of the CID (Criminal Investigation Department). Given the severity of your case, I'd recommend consulting with one of our affiliated lawyers. Would you like me to find nearby legal professionals?`,
                timeline: `I've noted this information. To build a stronger case, can you tell me approximately how many times this has occurred? Having specific dates and times helps establish a pattern of behavior.`,
            };

            let response = responses.default;
            const lowerMessage = message.toLowerCase();

            if (lowerMessage.includes('evidence') || lowerMessage.includes('screenshot') || lowerMessage.includes('proof')) {
                response = responses.evidence;
            } else if (lowerMessage.includes('legal') || lowerMessage.includes('police') || lowerMessage.includes('lawyer')) {
                response = responses.legal;
            } else if (lowerMessage.includes('time') || lowerMessage.includes('when') || lowerMessage.includes('date')) {
                response = responses.timeline;
            }

            const aiMessage: ChatMessage = {
                id: generateId(),
                role: 'assistant',
                content: response,
                timestamp: new Date(),
            };
            setChatMessages(prev => [...prev, aiMessage]);
            setIsChatLoading(false);
        }, 1500);
    }, []);

    // Submission
    const canSubmit = incident.identifiedLaws.some(l => l.isViolated) &&
        incident.evidence.length > 0 &&
        incident.identifiedLaws.some(l => l.includedInReport);

    // Save draft to backend
    const saveDraft = useCallback(async () => {
        try {
            // Convert date to YYYY-MM-DD format (date only, not datetime)
            const dateOccurred = incident.timeline[0]?.timestamp
                ? incident.timeline[0].timestamp.toISOString().split('T')[0]
                : null;

            const incidentData: IncidentCreate = {
                incident_type: incident.type,
                title: incident.title,
                description: incident.description,
                date_occurred: dateOccurred,
                location: null,
                jurisdiction: 'Sri Lanka',
                platforms_involved: incident.evidence
                    .filter(e => e.source)
                    .map(e => e.source)
                    .join(', ') || null,
                perpetrator_info: null,
                evidence_notes: incident.evidence
                    .map(e => `${e.name}: ${e.description || 'No description'}`)
                    .join('\n') || null,
            };

            const response = await createIncident(incidentData);

            setIncident(prev => ({
                ...prev,
                id: `inc_${response.id}`,
                status: 'draft',
                updatedAt: new Date(),
            }));

            alert('Draft saved successfully!');
        } catch (error) {
            console.error('Failed to save draft:', error);
            alert('Failed to save draft. Please try again.');
        }
    }, [incident]);

    // Submit to police (creates or updates incident with submitted status)
    const submitToPolice = useCallback(async () => {
        try {
            const incidentData: IncidentCreate = {
                incident_type: incident.type,
                title: incident.title,
                description: `${incident.description}\n\n## Identified Laws:\n${incident.identifiedLaws
                    .filter(l => l.includedInReport)
                    .map(l => `- ${l.name}, ${l.section}: ${l.description}`)
                    .join('\n')}`,
                date_occurred: incident.timeline[0]?.timestamp.toISOString() || null,
                location: null,
                jurisdiction: 'Sri Lanka',
                platforms_involved: incident.evidence
                    .filter(e => e.source)
                    .map(e => e.source)
                    .join(', ') || null,
                perpetrator_info: null,
                evidence_notes: incident.evidence
                    .map(e => `${e.name}: ${e.description || 'No description'}`)
                    .join('\n') || null,
            };

            const response = await createIncident(incidentData);

            setIncident(prev => ({
                ...prev,
                id: `inc_${response.id}`,
                status: 'submitted',
                updatedAt: new Date(),
                timeline: [
                    ...prev.timeline,
                    {
                        id: generateId(),
                        type: 'report',
                        title: 'Submitted to Police',
                        description: 'Your case has been submitted to the Sri Lanka Computer Crimes Division for review.',
                        timestamp: new Date(),
                    },
                ],
            }));

            alert('Successfully submitted to police!');
        } catch (error) {
            console.error('Failed to submit to police:', error);
            alert('Failed to submit. Please try again.');
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
    };
}

export default useIncidentWorkspace;
