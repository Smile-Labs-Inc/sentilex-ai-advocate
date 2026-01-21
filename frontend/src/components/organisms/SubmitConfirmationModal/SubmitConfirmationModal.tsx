// =============================================================================
// SubmitConfirmationModal Organism
// Confirmation modal before submitting case to police
// =============================================================================

import { useState } from 'preact/hooks';

import { Card } from '../../atoms/Card/Card';
import { Button } from '../../atoms/Button/Button';
import { Icon } from '../../atoms/Icon/Icon';
import type { IncidentDraft } from '../../../types';

export interface SubmitConfirmationModalProps {
    isOpen: boolean;
    incident: IncidentDraft;
    onConfirm: () => void;
    onCancel: () => void;
    isSubmitting?: boolean;
}

export function SubmitConfirmationModal({
    isOpen,
    incident,
    onConfirm,
    onCancel,
    isSubmitting = false,
}: SubmitConfirmationModalProps) {
    const [acceptedTerms, setAcceptedTerms] = useState(false);

    if (!isOpen) return null;

    const violatedLaws = incident.identifiedLaws.filter(l => l.isViolated);
    const includedLaws = incident.identifiedLaws.filter(l => l.includedInReport);

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/80 backdrop-blur-sm animate-fade-in"
                onClick={onCancel}
            />

            {/* Modal */}
            <Card
                variant="elevated"
                padding="lg"
                className="relative w-full max-w-lg mx-4 animate-scale-in"
            >
                {/* Header */}
                <div className="flex items-start gap-4 mb-6">
                    <div className="w-12 h-12 rounded-full bg-red-500/20 flex items-center justify-center">
                        <Icon name="Shield" size="md" className="text-red-400" />
                    </div>
                    <div>
                        <h2 className="text-lg font-semibold text-foreground">
                            Submit Case to Police
                        </h2>
                        <p className="text-sm text-muted-foreground mt-1">
                            Your case will be forwarded to law enforcement for review.
                        </p>
                    </div>
                </div>

                {/* Case Summary */}
                <div className="p-4 bg-secondary/50 rounded-lg border border-border mb-4 space-y-3">
                    <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground uppercase tracking-wide">Case Title</span>
                        <span className="text-sm text-foreground">{incident.title}</span>
                    </div>
                    <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground uppercase tracking-wide">Evidence Files</span>
                        <span className="text-sm text-foreground">{incident.evidence.length} files</span>
                    </div>
                    <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground uppercase tracking-wide">Timeline Events</span>
                        <span className="text-sm text-foreground">{incident.timeline.length} events</span>
                    </div>
                    <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground uppercase tracking-wide">Laws Violated</span>
                        <span className="text-sm text-red-400 font-medium">{violatedLaws.length} identified</span>
                    </div>
                </div>

                {/* Laws included */}
                {includedLaws.length > 0 && (
                    <div className="mb-4">
                        <p className="text-xs text-muted-foreground uppercase tracking-wide mb-2">
                            Laws Included in Report
                        </p>
                        <div className="space-y-1">
                            {includedLaws.slice(0, 3).map((law) => (
                                <div key={law.id} className="flex items-center gap-2 text-sm">
                                    <Icon name="CheckCircle" size="xs" className="text-green-400" />
                                    <span className="text-muted-foreground/80">{law.name} - {law.section}</span>
                                </div>
                            ))}
                            {includedLaws.length > 3 && (
                                <p className="text-xs text-muted-foreground pl-5">
                                    +{includedLaws.length - 3} more
                                </p>
                            )}
                        </div>
                    </div>
                )}

                {/* Warning */}
                <div className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg mb-6">
                    <div className="flex items-start gap-2">
                        <Icon name="AlertTriangle" size="sm" className="text-yellow-400 mt-0.5" />
                        <div>
                            <p className="text-xs text-yellow-300 font-medium">
                                Important Notice
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">
                                Filing a false report is a criminal offense. Ensure all information
                                provided is accurate and truthful to the best of your knowledge.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Terms checkbox */}
                <label className="flex items-start gap-3 p-4 bg-secondary/30 rounded-lg border border-border cursor-pointer hover:border-input transition-colors mb-6">
                    <input
                        type="checkbox"
                        checked={acceptedTerms}
                        onChange={(e) => setAcceptedTerms((e.target as HTMLInputElement).checked)}
                        className="w-4 h-4 mt-0.5 rounded border-muted-foreground bg-secondary text-primary focus:ring-primary/20"
                    />
                    <div>
                        <p className="text-sm text-foreground">
                            I confirm that the information provided is accurate
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                            I understand that false reports may result in legal consequences and
                            I consent to sharing this information with law enforcement.
                        </p>
                    </div>
                </label>

                {/* Actions */}
                <div className="flex justify-end gap-3">
                    <Button
                        variant="ghost"
                        onClick={onCancel}
                        disabled={isSubmitting}
                    >
                        Cancel
                    </Button>
                    <Button
                        variant="destructive"
                        onClick={onConfirm}
                        disabled={!acceptedTerms || isSubmitting}
                        isLoading={isSubmitting}
                    >
                        <Icon name="Send" size="sm" />
                        Submit Report
                    </Button>
                </div>
            </Card>
        </div>
    );
}

export default SubmitConfirmationModal;
