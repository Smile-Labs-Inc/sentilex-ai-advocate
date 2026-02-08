// =============================================================================
// IncidentWorkspace Page
// Main workspace for incident analysis, AI chat, timeline, and evidence
// =============================================================================

import { useState } from 'preact/hooks';
import { DashboardLayout } from '../../components/templates/DashboardLayout/DashboardLayout';
import { EditableTimeline } from '../../components/organisms/EditableTimeline/EditableTimeline';
import { EvidenceSection } from '../../components/organisms/EvidenceSection/EvidenceSection';
import { EnhancedLawsSection } from '../../components/organisms/EnhancedLawsSection/EnhancedLawsSection';
import { AIChatSection } from '../../components/organisms/AIChatSection/AIChatSection';
import { SubmitConfirmationModal } from '../../components/organisms/SubmitConfirmationModal/SubmitConfirmationModal';
import { OccurrenceModal } from '../../components/organisms/OccurrenceModal/OccurrenceModal';
import { SubmitToPoliceButton } from '../../components/molecules/SubmitToPoliceButton/SubmitToPoliceButton';
import { FindLawyersButton } from '../../components/molecules/FindLawyersButton/FindLawyersButton';
import { Card, CardHeader, CardTitle } from '../../components/atoms/Card/Card';
import { Button } from '../../components/atoms/Button/Button';
import { Icon } from '../../components/atoms/Icon/Icon';
import { Badge, getStatusVariant, getStatusLabel } from '../../components/atoms/Badge/Badge';
import { useIncidentWorkspace } from '../../hooks/useIncidentWorkspace';
import type { NavItem } from '../../types';
import type { UserProfile } from '../../types/auth';
import type { WizardData } from '../../components/organisms/OnboardingWizard/OnboardingWizard';

export interface IncidentWorkspacePageProps {
    user: UserProfile;
    wizardData?: WizardData;
    onNavigate: (item: NavItem) => void;
    onBack: () => void;
    onFindLawyers: () => void;
}

export function IncidentWorkspacePage({
    user,
    wizardData,
    onNavigate,
    onBack,
    onFindLawyers,
}: IncidentWorkspacePageProps) {
    const {
        incident,
        isAnalyzing,
        addTimelineEvent,
        updateTimelineEvent,
        deleteTimelineEvent,
        acceptSuggestion,
        addEvidence,
        deleteEvidence,
        toggleLawIncluded,
        canSubmit,
        submitToPolice,
        saveDraft,
        sendMessage,
        chatMessages,
        isChatLoading,
    } = useIncidentWorkspace(wizardData);

    const [showSubmitModal, setShowSubmitModal] = useState(false);
    const [showOccurrenceModal, setShowOccurrenceModal] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isSaving, setIsSaving] = useState(false);

    const violatedLaws = incident.identifiedLaws.filter(l => l.isViolated);

    const handleSubmit = async () => {
        setIsSubmitting(true);
        await submitToPolice();
        setIsSubmitting(false);
        setShowSubmitModal(false);
    };

    const handleSaveDraft = async () => {
        setIsSaving(true);
        await saveDraft();
        setIsSaving(false);
    };

    const handleViewEvidence = (evidence: any) => {
        console.log('View evidence:', evidence);
    };

    const handleAddNote = (evidence: any) => {
        console.log('Add note to evidence:', evidence);
    };

    // Map incident status to badge status
    const getBadgeStatus = () => {
        switch (incident.status) {
            case 'draft': return 'pending';
            case 'analyzing': return 'in-progress';
            case 'ready': return 'in-progress';
            case 'submitted': return 'submitted-to-police';
            default: return 'pending';
        }
    };

    return (
        <DashboardLayout
            user={user}
            currentPath="/workspace"
            onNavigate={onNavigate}
        >
            {/* Header */}
            <div className="mb-6 animate-fade-in">
                <div className="flex items-start justify-between">
                    <div className="flex items-center gap-4">
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={onBack}
                            className="shrink-0"
                        >
                            <Icon name="ArrowLeft" size="sm" />
                        </Button>
                        <div>
                            <div className="flex items-center gap-3">
                                <h1 className="text-2xl font-semibold text-foreground">
                                    {incident.title}
                                </h1>
                                <Badge
                                    variant={getStatusVariant(getBadgeStatus())}
                                    className="capitalize"
                                >
                                    {incident.status === 'analyzing' ? 'Analyzing...' : getStatusLabel(getBadgeStatus())}
                                </Badge>
                            </div>
                            <p className="text-sm text-muted-foreground mt-1">
                                Case #{incident.id.slice(0, 8).toUpperCase()} • Created {incident.createdAt.toLocaleDateString()}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setShowOccurrenceModal(true)}
                        >
                            <Icon name="Plus" size="xs" />
                            Record Occurrence
                        </Button>
                        <Button variant="outline" size="sm">
                            <Icon name="Download" size="xs" />
                            Export
                        </Button>
                        <Button
                            variant="secondary"
                            size="sm"
                            onClick={handleSaveDraft}
                            disabled={isSaving}
                        >
                            <Icon name="Save" size="xs" />
                            {isSaving ? 'Saving...' : 'Save Draft'}
                        </Button>
                    </div>
                </div>
            </div>

            {/* Main content grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left column - Timeline & Chat */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Case summary card */}
                    <Card variant="default" padding="lg" className="animate-slide-up">
                        <CardHeader>
                            <div className="flex items-center gap-2">
                                <Icon name="FileText" size="sm" className="text-muted-foreground" />
                                <CardTitle className="text-sm">Case Summary</CardTitle>
                            </div>
                            <Button variant="ghost" size="sm">
                                <Icon name="Pencil" size="xs" />
                                Edit
                            </Button>
                        </CardHeader>
                        <p className="text-sm text-muted-foreground leading-relaxed">
                            {incident.description || 'No description provided. Click edit to add details about your case.'}
                        </p>
                        <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-border">
                            <div>
                                <p className="text-xs text-muted-foreground">Type</p>
                                <p className="text-sm text-foreground capitalize">{incident.type.replace('-', ' ')}</p>
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground">Date Occurred</p>
                                <p className="text-sm text-foreground">{incident.dateOccurred.toLocaleDateString()}</p>
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground">Platforms</p>
                                <p className="text-sm text-foreground">
                                    {incident.platformsInvolved.length > 0
                                        ? incident.platformsInvolved.join(', ')
                                        : 'Not specified'
                                    }
                                </p>
                            </div>
                        </div>
                    </Card>

                    {/* Editable Timeline */}
                    <EditableTimeline
                        events={incident.timeline}
                        onAddEvent={addTimelineEvent}
                        onUpdateEvent={updateTimelineEvent}
                        onDeleteEvent={deleteTimelineEvent}
                        onAcceptSuggestion={acceptSuggestion}
                    />

                    {/* AI Chat */}
                    <AIChatSection
                        messages={chatMessages}
                        onSendMessage={sendMessage}
                        isLoading={isChatLoading}
                    />
                </div>

                {/* Right column - Laws, Evidence, Actions */}
                <div className="space-y-6">
                    {/* Action buttons */}
                    <div className="space-y-3">
                        <SubmitToPoliceButton
                            isEnabled={canSubmit}
                            violationsCount={violatedLaws.length}
                            onSubmit={() => setShowSubmitModal(true)}
                        />
                        <FindLawyersButton
                            nearbyCount={12}
                            onClick={onFindLawyers}
                        />
                    </div>

                    {/* Laws section */}
                    <EnhancedLawsSection
                        laws={incident.identifiedLaws}
                        onToggleInclude={toggleLawIncluded}
                        isAnalyzing={isAnalyzing}
                    />

                    {/* Evidence section */}
                    <EvidenceSection
                        evidence={incident.evidence}
                        onAddEvidence={addEvidence}
                        onDeleteEvidence={deleteEvidence}
                        onViewEvidence={handleViewEvidence}
                        onAddNote={handleAddNote}
                    />

                    {/* Quick help card */}
                    <Card variant="default" padding="lg" className="animate-slide-up">
                        <div className="flex items-start gap-3">
                            <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center shrink-0">
                                <Icon name="HelpCircle" size="sm" className="text-blue-400" />
                            </div>
                            <div>
                                <h4 className="text-sm font-medium text-foreground mb-1">Need Help?</h4>
                                <p className="text-xs text-muted-foreground">
                                    Ask the AI assistant for guidance on documenting your case,
                                    understanding applicable laws, or next steps.
                                </p>
                                <Button variant="ghost" size="sm" className="mt-2 -ml-2">
                                    <Icon name="MessageCircle" size="xs" />
                                    Chat with AI
                                </Button>
                            </div>
                        </div>
                    </Card>
                </div>
            </div>

            {/* Submit confirmation modal */}
            <SubmitConfirmationModal
                isOpen={showSubmitModal}
                incident={incident}
                onConfirm={handleSubmit}
                onCancel={() => setShowSubmitModal(false)}
                isSubmitting={isSubmitting}
            />

            {/* Occurrence modal */}
            <OccurrenceModal
                incidentId={parseInt(incident.id)}
                isOpen={showOccurrenceModal}
                onClose={() => setShowOccurrenceModal(false)}
                onOccurrenceCreated={() => {
                    setShowOccurrenceModal(false);
                    // TODO: Reload occurrences and refresh timeline
                    console.log('Occurrence created successfully');
                }}
            />
        </DashboardLayout>
    );
}

export default IncidentWorkspacePage;
