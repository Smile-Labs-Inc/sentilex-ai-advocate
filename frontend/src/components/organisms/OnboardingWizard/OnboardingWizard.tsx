// =============================================================================
// OnboardingWizard Organism
// Multi-step wizard for reporting new incidents
// =============================================================================

import { useState } from 'preact/hooks';
import { cn } from '../../../lib/utils';
import { Button } from '../../atoms/Button/Button';
import { Icon, type IconName } from '../../atoms/Icon/Icon';
import { Input } from '../../atoms/Input/Input';
import { Textarea } from '../../atoms/Textarea/Textarea';
import { ProgressBar } from '../../atoms/ProgressBar/ProgressBar';
import { RadioGroup, type RadioOption } from '../../atoms/RadioGroup/RadioGroup';
import { Card } from '../../atoms/Card/Card';
import type { IncidentType } from '../../../types';

export interface WizardData {
    incidentType: IncidentType | '';
    title: string;
    description: string;
    dateOccurred: string;
    platformsInvolved: string;
    perpetratorInfo: string;
    evidenceNotes: string;
}

export interface OnboardingWizardProps {
    onComplete: (data: WizardData) => void;
    onCancel: () => void;
    className?: string;
}

const incidentTypeOptions: RadioOption[] = [
    {
        value: 'cyberbullying',
        label: 'Cyberbullying',
        description: 'Repeated harassment, threats, or intimidation online',
        icon: 'MessageSquareWarning',
    },
    {
        value: 'harassment',
        label: 'Harassment',
        description: 'Unwanted contact, threats, or offensive behavior',
        icon: 'AlertTriangle',
    },
    {
        value: 'stalking',
        label: 'Stalking',
        description: 'Persistent tracking, monitoring, or following',
        icon: 'Eye',
    },
    {
        value: 'non-consensual-leak',
        label: 'Non-consensual Intimate Images',
        description: 'Sharing private images without consent',
        icon: 'ImageOff',
    },
    {
        value: 'identity-theft',
        label: 'Identity Theft',
        description: 'Impersonation or misuse of personal information',
        icon: 'UserX',
    },
    {
        value: 'online-fraud',
        label: 'Online Fraud',
        description: 'Scams, phishing, or financial fraud',
        icon: 'CreditCard',
    },
    {
        value: 'other',
        label: 'Other',
        description: 'Another type of cybercrime not listed above',
        icon: 'FileQuestion',
    },
];

const steps = [
    { id: 1, title: 'Incident Type', icon: 'FileWarning' as IconName },
    { id: 2, title: 'Details', icon: 'FileText' as IconName },
    { id: 3, title: 'Evidence', icon: 'Upload' as IconName },
    { id: 4, title: 'Review', icon: 'CheckCircle' as IconName },
];

export function OnboardingWizard({ onComplete, onCancel, className }: OnboardingWizardProps) {
    const [currentStep, setCurrentStep] = useState(1);
    const [data, setData] = useState<WizardData>({
        incidentType: '',
        title: '',
        description: '',
        dateOccurred: '',
        platformsInvolved: '',
        perpetratorInfo: '',
        evidenceNotes: '',
    });

    const updateData = (field: keyof WizardData, value: string) => {
        setData((prev) => ({ ...prev, [field]: value }));
    };

    const canProceed = () => {
        switch (currentStep) {
            case 1:
                return data.incidentType !== '';
            case 2:
                return data.title.trim() !== '' && data.description.trim() !== '';
            case 3:
                return true; // Evidence is optional
            case 4:
                return true;
            default:
                return false;
        }
    };

    const handleNext = () => {
        if (currentStep < steps.length) {
            setCurrentStep(currentStep + 1);
        } else {
            onComplete(data);
        }
    };

    const handleBack = () => {
        if (currentStep > 1) {
            setCurrentStep(currentStep - 1);
        } else {
            onCancel();
        }
    };

    return (
        <div className={cn('max-w-2xl mx-auto', className)}>
            {/* Header */}
            <div className="mb-8 animate-fade-in">
                <h1 className="text-2xl font-semibold text-foreground mb-2">
                    Report an Incident
                </h1>
                <p className="text-muted-foreground">
                    We'll guide you through documenting your case step by step.
                </p>
            </div>

            {/* Progress */}
            <div className="mb-8">
                <ProgressBar currentStep={currentStep} totalSteps={steps.length} />

                {/* Step indicators */}
                <div className="flex justify-between mt-4">
                    {steps.map((step) => (
                        <div
                            key={step.id}
                            className={cn(
                                'flex items-center gap-2',
                                step.id === currentStep
                                    ? 'text-foreground'
                                    : step.id < currentStep
                                        ? 'text-green-500'
                                        : 'text-muted-foreground'
                            )}
                        >
                            <div className={cn(
                                'w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium',
                                step.id === currentStep
                                    ? 'bg-foreground text-background'
                                    : step.id < currentStep
                                        ? 'bg-green-500/20 text-green-500'
                                        : 'bg-secondary text-muted-foreground'
                            )}>
                                {step.id < currentStep ? (
                                    <Icon name="Check" size="xs" />
                                ) : (
                                    step.id
                                )}
                            </div>
                            <span className="text-xs hidden sm:block">{step.title}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Step Content */}
            <Card variant="default" padding="lg" className="mb-6 animate-slide-up">
                {currentStep === 1 && (
                    <div className="space-y-4">
                        <h2 className="text-lg font-medium text-foreground mb-4">
                            What type of incident are you reporting?
                        </h2>
                        <RadioGroup
                            name="incidentType"
                            options={incidentTypeOptions}
                            value={data.incidentType}
                            onChange={(value) => updateData('incidentType', value)}
                        />
                    </div>
                )}

                {currentStep === 2 && (
                    <div className="space-y-6">
                        <h2 className="text-lg font-medium text-foreground mb-4">
                            Tell us about the incident
                        </h2>
                        <Input
                            label="Title"
                            placeholder="Brief title for this incident"
                            value={data.title}
                            onInput={(e) => updateData('title', (e.target as HTMLInputElement).value)}
                        />
                        <Textarea
                            label="Description"
                            placeholder="Describe what happened in detail. Include dates, times, and any relevant context."
                            rows={5}
                            value={data.description}
                            onInput={(e) => updateData('description', (e.target as HTMLTextAreaElement).value)}
                        />
                        <Input
                            label="When did this occur?"
                            type="date"
                            value={data.dateOccurred}
                            onInput={(e) => updateData('dateOccurred', (e.target as HTMLInputElement).value)}
                        />
                        <Input
                            label="Platforms involved"
                            placeholder="e.g., Instagram, Facebook, WhatsApp"
                            value={data.platformsInvolved}
                            onInput={(e) => updateData('platformsInvolved', (e.target as HTMLInputElement).value)}
                        />
                    </div>
                )}

                {currentStep === 3 && (
                    <div className="space-y-6">
                        <h2 className="text-lg font-medium text-foreground mb-4">
                            Evidence & Additional Information
                        </h2>
                        <Textarea
                            label="Perpetrator Information (if known)"
                            placeholder="Any information about who did this - usernames, accounts, etc."
                            rows={3}
                            value={data.perpetratorInfo}
                            onInput={(e) => updateData('perpetratorInfo', (e.target as HTMLTextAreaElement).value)}
                        />
                        <Textarea
                            label="Evidence Notes"
                            placeholder="List any screenshots, messages, or other evidence you have"
                            rows={3}
                            value={data.evidenceNotes}
                            onInput={(e) => updateData('evidenceNotes', (e.target as HTMLTextAreaElement).value)}
                        />

                        {/* Upload area (placeholder) */}
                        <div className="border-2 border-dashed border-border rounded-xl p-8 text-center">
                            <Icon name="Upload" size="lg" className="text-muted-foreground mx-auto mb-3" />
                            <p className="text-sm text-muted-foreground mb-2">
                                Drag and drop files here, or click to browse
                            </p>
                            <p className="text-xs text-muted-foreground">
                                Supports images, PDFs, and documents up to 10MB
                            </p>
                            <Button variant="secondary" size="sm" className="mt-4">
                                Browse Files
                            </Button>
                        </div>
                    </div>
                )}

                {currentStep === 4 && (
                    <div className="space-y-6">
                        <h2 className="text-lg font-medium text-foreground mb-4">
                            Review Your Report
                        </h2>

                        <div className="space-y-4">
                            <div className="p-4 bg-secondary/50 rounded-lg">
                                <div className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                                    Incident Type
                                </div>
                                <div className="text-foreground">
                                    {incidentTypeOptions.find(o => o.value === data.incidentType)?.label || '-'}
                                </div>
                            </div>

                            <div className="p-4 bg-secondary/50 rounded-lg">
                                <div className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                                    Title
                                </div>
                                <div className="text-foreground">{data.title || '-'}</div>
                            </div>

                            <div className="p-4 bg-secondary/50 rounded-lg">
                                <div className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                                    Description
                                </div>
                                <div className="text-foreground text-sm">{data.description || '-'}</div>
                            </div>

                            {data.dateOccurred && (
                                <div className="p-4 bg-secondary/50 rounded-lg">
                                    <div className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                                        Date Occurred
                                    </div>
                                    <div className="text-foreground">{data.dateOccurred}</div>
                                </div>
                            )}

                            {data.platformsInvolved && (
                                <div className="p-4 bg-secondary/50 rounded-lg">
                                    <div className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                                        Platforms
                                    </div>
                                    <div className="text-foreground">{data.platformsInvolved}</div>
                                </div>
                            )}
                        </div>

                        <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                            <div className="flex items-start gap-3">
                                <Icon name="Info" size="sm" className="text-blue-400 mt-0.5" />
                                <div className="text-sm text-blue-300">
                                    After submitting, our AI will analyze your case and identify applicable laws.
                                    You can add more evidence and details at any time.
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </Card>

            {/* Navigation */}
            <div className="flex justify-between">
                <Button variant="ghost" onClick={handleBack}>
                    <Icon name="ArrowLeft" size="sm" />
                    {currentStep === 1 ? 'Cancel' : 'Back'}
                </Button>

                <Button
                    onClick={handleNext}
                    disabled={!canProceed()}
                    className="gap-2"
                >
                    {currentStep === steps.length ? (
                        <>
                            Submit Report
                            <Icon name="Send" size="sm" />
                        </>
                    ) : (
                        <>
                            Continue
                            <Icon name="ArrowRight" size="sm" />
                        </>
                    )}
                </Button>
            </div>
        </div>
    );
}

export default OnboardingWizard;
