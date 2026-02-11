// =============================================================================
// OccurrenceModal Organism
// Modal for recording new occurrences within an incident
// =============================================================================

import { useState } from 'preact/hooks';
import { Card } from '../../atoms/Card/Card';
import { Button } from '../../atoms/Button/Button';
import { Icon } from '../../atoms/Icon/Icon';
import { Input } from '../../atoms/Input/Input';
import { Textarea } from '../../atoms/Textarea/Textarea';
import { createOccurrence, uploadEvidenceToOccurrence } from '../../../services/incident';

export interface OccurrenceModalProps {
    incidentId: number;
    isOpen: boolean;
    onClose: () => void;
    onOccurrenceCreated: () => void;
}

export function OccurrenceModal({
    incidentId,
    isOpen,
    onClose,
    onOccurrenceCreated,
}: OccurrenceModalProps) {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [dateOccurred, setDateOccurred] = useState(new Date().toISOString().split('T')[0]);
    const [evidenceFiles, setEvidenceFiles] = useState<File[]>([]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    if (!isOpen) return null;

    const handleFileSelect = (e: Event) => {
        const target = e.target as HTMLInputElement;
        if (target.files) {
            setEvidenceFiles(Array.from(target.files));
        }
    };

    const handleSubmit = async () => {
        if (!title || !description) {
            setError('Please fill in all required fields');
            return;
        }

        setIsSubmitting(true);
        setError(null);

        try {
            // 1. Create the occurrence
            const occurrence = await createOccurrence(incidentId, {
                title,
                description,
                date_occurred: dateOccurred
            });

            // 2. Upload evidence if any
            if (evidenceFiles.length > 0) {
                await uploadEvidenceToOccurrence(incidentId, occurrence.id, evidenceFiles);
            }

            // Success - notify parent and close
            onOccurrenceCreated();
            onClose();

            // Reset form
            setTitle('');
            setDescription('');
            setDateOccurred(new Date().toISOString().split('T')[0]);
            setEvidenceFiles([]);
        } catch (err) {
            
            setError(err instanceof Error ? err.message : 'Failed to record occurrence. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/80 backdrop-blur-sm animate-fade-in"
                onClick={onClose}
            />

            {/* Modal */}
            <Card
                variant="elevated"
                padding="lg"
                className="relative w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto animate-scale-in"
            >
                {/* Header */}
                <div className="flex items-start justify-between mb-6">
                    <div className="flex items-start gap-4">
                        <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                            <Icon name="Plus" size="md" className="text-primary" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-foreground">
                                Record New Occurrence
                            </h2>
                            <p className="text-sm text-muted-foreground mt-1">
                                Document a new event related to this ongoing case. Each occurrence can have its own evidence files.
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-muted-foreground hover:text-foreground transition-colors"
                        disabled={isSubmitting}
                    >
                        <Icon name="X" size="sm" />
                    </button>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                        <div className="flex items-start gap-2">
                            <Icon name="AlertCircle" size="sm" className="text-red-400 mt-0.5" />
                            <p className="text-sm text-red-400">{error}</p>
                        </div>
                    </div>
                )}

                {/* Form */}
                <div className="space-y-4">
                    <Input
                        label="Title *"
                        placeholder="e.g., Threatening DM on Instagram"
                        value={title}
                        onChange={(e) => setTitle(e.currentTarget.value)}
                    />

                    <Input
                        type="date"
                        label="Date of Occurrence *"
                        value={dateOccurred}
                        onChange={(e) => setDateOccurred(e.currentTarget.value)}
                    />

                    <Textarea
                        label="Description *"
                        placeholder="Describe what happened in detail..."
                        value={description}
                        onChange={(e) => setDescription(e.currentTarget.value)}
                        rows={6}
                    />

                    <div>
                        <label className="block text-sm font-medium mb-2 text-foreground">
                            Evidence Files (Optional)
                        </label>
                        <input
                            type="file"
                            multiple
                            onChange={handleFileSelect}
                            disabled={isSubmitting}
                            className="block w-full text-sm text-muted-foreground
                                file:mr-4 file:py-2 file:px-4
                                file:rounded-lg file:border-0
                                file:text-sm file:font-semibold
                                file:bg-primary file:text-primary-foreground
                                hover:file:bg-primary/90
                                disabled:opacity-50 disabled:cursor-not-allowed"
                        />
                        {evidenceFiles.length > 0 && (
                            <div className="mt-2 space-y-1">
                                <p className="text-xs text-muted-foreground">
                                    {evidenceFiles.length} file(s) selected:
                                </p>
                                {evidenceFiles.map((file, idx) => (
                                    <div key={idx} className="flex items-center gap-2 text-xs text-muted-foreground">
                                        <Icon name="File" size="xs" />
                                        <span>{file.name}</span>
                                        <span className="text-muted-foreground/60">
                                            ({(file.size / 1024).toFixed(1)} KB)
                                        </span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Info Box */}
                <div className="mt-6 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                    <div className="flex items-start gap-2">
                        <Icon name="Info" size="sm" className="text-blue-400 mt-0.5" />
                        <div>
                            <p className="text-xs text-blue-300 font-medium">
                                Why record occurrences?
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">
                                Recording each incident separately helps build a stronger case by showing a pattern of behavior.
                                This is especially important for harassment and stalking cases.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Actions */}
                <div className="flex justify-end gap-3 mt-6">
                    <Button
                        variant="ghost"
                        onClick={onClose}
                        disabled={isSubmitting}
                    >
                        Cancel
                    </Button>
                    <Button
                        variant="primary"
                        onClick={handleSubmit}
                        disabled={isSubmitting || !title || !description}
                        isLoading={isSubmitting}
                    >
                        <Icon name="Plus" size="sm" />
                        Record Occurrence
                    </Button>
                </div>
            </Card>
        </div>
    );
}

export default OccurrenceModal;
