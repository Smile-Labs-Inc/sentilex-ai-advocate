// =============================================================================
// Veritas Protocol - Type Definitions
// =============================================================================

// Re-export auth types
export * from "./auth";

export type IncidentType =
  | "cyberbullying"
  | "harassment"
  | "stalking"
  | "non-consensual-leak"
  | "identity-theft"
  | "online-fraud"
  | "other";

export type IncidentStatus =
  | "pending"
  | "in-progress"
  | "resolved"
  | "submitted-to-police";

export type QuickLinkType = "hotline" | "resource" | "finder";

export type ActivityType =
  | "update"
  | "law-identified"
  | "evidence-uploaded"
  | "report-submitted"
  | "case-opened"
  | "case-resolved";

// =============================================================================
// Incident Types
// =============================================================================

export interface Incident {
  id: string;
  title: string;
  type: IncidentType;
  status: IncidentStatus;
  createdAt: Date;
  updatedAt: Date;
  lawsIdentified: number;
  description?: string;
}

// =============================================================================
// Statistics Types
// =============================================================================

export interface UserStats {
  pendingReports: number;
  totalReports: number;
  resolvedCases: number;
  inProgressCases: number;
}

export interface GlobalStats {
  totalCasesSolved: number;
  activeUsers: number;
  affiliatedLawyers: number;
  caseTypesHandled: number;
}

export interface CaseTypeDistribution {
  type: IncidentType;
  label: string;
  count: number;
  percentage: number;
  color: string;
}

// =============================================================================
// Quick Links Types
// =============================================================================

export interface QuickLink {
  id: string;
  label: string;
  description: string;
  icon: string;
  href: string;
  type: QuickLinkType;
}

// =============================================================================
// Activity Feed Types
// =============================================================================

export interface ActivityItem {
  id: string;
  message: string;
  timestamp: Date;
  type: ActivityType;
  highlightText?: string;
}

// =============================================================================
// Navigation Types
// =============================================================================

export interface NavItem {
  id: string;
  label: string;
  icon: string;
  href: string;
  isActive?: boolean;
}

export interface NavSection {
  title?: string;
  items: NavItem[];
}

// =============================================================================
// Evidence Types
// =============================================================================

export type EvidenceType =
  | "image"
  | "video"
  | "document"
  | "audio"
  | "screenshot"
  | "other";

export interface Evidence {
  id: string;
  fileName: string;
  fileSize: number;
  fileType: EvidenceType;
  mimeType: string;
  uploadedAt: Date;
  description?: string;
  isEncrypted: boolean;
  thumbnailUrl?: string;
}

// =============================================================================
// Editable Timeline Types
// =============================================================================

export interface TimelineEventEditable {
  id: string;
  type:
    | "incident"
    | "evidence"
    | "communication"
    | "threat"
    | "report"
    | "ai-suggestion"
    | "custom";
  title: string;
  description: string;
  timestamp: Date;
  isEditing?: boolean;
  isAISuggested?: boolean;
  linkedEvidenceIds?: string[];
}

// =============================================================================
// Incident Draft Types (for in-progress incidents)
// =============================================================================

export interface IncidentDraft {
  id: string;
  type: IncidentType;
  title: string;
  description: string;
  dateOccurred: Date;
  platformsInvolved: string[];
  perpetratorInfo?: string;
  timeline: TimelineEventEditable[];
  evidence: Evidence[];
  identifiedLaws: LawViolation[];
  status: "draft" | "analyzing" | "ready" | "submitted";
  createdAt: Date;
  updatedAt: Date;
}

// =============================================================================
// Law Violation Types
// =============================================================================

export type ViolationSeverity = "critical" | "high" | "medium" | "low";

export interface LawViolation {
  id: string;
  name: string;
  section: string;
  description: string;
  jurisdiction: string;
  severity: ViolationSeverity;
  isViolated: boolean;
  confidence: number; // 0-100
  sourceUrl?: string;
  includedInReport: boolean;
}

// =============================================================================
// Wizard Types
// =============================================================================

export type WizardQuestionType =
  | "radio"
  | "checkbox"
  | "text"
  | "textarea"
  | "date"
  | "multiselect";

export interface WizardQuestionOption {
  value: string;
  label: string;
  description?: string;
  icon?: string;
}

export interface WizardQuestion {
  id: string;
  question: string;
  description?: string;
  type: WizardQuestionType;
  options?: WizardQuestionOption[];
  required: boolean;
  placeholder?: string;
  dependsOn?: {
    questionId: string;
    values: string[];
  };
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

// =============================================================================
// Lawbook Types
// =============================================================================

export interface LawbookSection {
  id: string;
  title: string;
  content: string; // Markdown supported
}

export interface LawbookChapter {
  id: string;
  title: string;
  icon?: string;
  sections: LawbookSection[];
}

export interface Bookmark {
  id: string;
  chapterId: string;
  sectionId: string;
  title: string;
  createdAt: Date;
}
