import { useState, useEffect } from 'preact/hooks';
import { Button } from '../../atoms/Button/Button';
import { Icon } from '../../atoms/Icon/Icon';
import { FileDropzone } from '../../atoms/FileDropzone/FileDropzone';
import type { JSX } from 'preact';
import './EvidenceUploadModal.css';

export interface EvidenceUploadModalProps {
    isOpen: boolean;
    onClose: () => void;
    onUpload: (files: File[], incidentId: number) => Promise<void>;
    incidents?: Array<{ id: number; title: string }>;
    isLoading?: boolean;
}

export function EvidenceUploadModal({
    isOpen,
    onClose,
    onUpload,
    incidents = [],
    isLoading = false,
}: EvidenceUploadModalProps) {
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
    const [selectedIncidentId, setSelectedIncidentId] = useState<number | null>(
        incidents.length > 0 ? incidents[0].id : null
    );
    const [uploadError, setUploadError] = useState<string | null>(null);
    const [isUploading, setIsUploading] = useState(false);

    // Auto-select first incident when incidents load
    useEffect(() => {
        if (incidents.length > 0 && selectedIncidentId === null) {
            setSelectedIncidentId(incidents[0].id);
        }
    }, [incidents]);

    const handleFilesSelected = (files: File[]) => {
        setSelectedFiles([...selectedFiles, ...files]);
        setUploadError(null);
    };

    const handleRemoveFile = (index: number) => {
        setSelectedFiles(selectedFiles.filter((_, i) => i !== index));
    };

    const handleUpload = async () => {
        if (selectedFiles.length === 0) {
            setUploadError('Please select at least one file');
            return;
        }

        if (!selectedIncidentId) {
            setUploadError('Please select an incident');
            return;
        }

        try {
            setIsUploading(true);
            setUploadError(null);
            await onUpload(selectedFiles, selectedIncidentId);
            setSelectedFiles([]);
            onClose();
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to upload evidence';
            setUploadError(message);
        } finally {
            setIsUploading(false);
        }
    };

    if (!isOpen) return null;

    const totalSize = selectedFiles.reduce((acc, file) => acc + file.size, 0);
    const maxSize = 100 * 1024 * 1024; // 100MB total
    const isOverLimit = totalSize > maxSize;

    return (
        <>
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-black/50 z-40"
                onClick={onClose}
                aria-hidden="true"
            />

            {/* Modal */}
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                <div className="bg-card rounded-lg shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                    {/* Header */}
                    <div className="flex items-center justify-between p-6 border-b border-border sticky top-0 bg-card">
                        <h2 className="text-xl font-bold text-foreground">Upload Evidence</h2>
                        <button
                            onClick={onClose}
                            className="p-1 hover:bg-accent rounded-md transition-colors"
                            aria-label="Close"
                        >
                            <Icon name="X" size="sm" />
                        </button>
                    </div>

                    {/* Content */}
                    <div className="p-6 space-y-6">
                        {/* Incident Selection */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-2">
                                Select Incident
                            </label>
                            {isLoading ? (
                                <div className="flex items-center gap-3 p-4 bg-muted/50 rounded-lg">
                                    <Icon name="Loader" size="sm" className="animate-spin" />
                                    <span className="text-muted-foreground text-sm">Loading incidents...</span>
                                </div>
                            ) : incidents.length > 0 ? (
                                <select
                                    value={selectedIncidentId || ''}
                                    onChange={(e: JSX.TargetedEvent<HTMLSelectElement>) =>
                                        setSelectedIncidentId(parseInt(e.currentTarget.value))
                                    }
                                    className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                                >
                                    {incidents.map((incident) => (
                                        <option key={incident.id} value={incident.id}>
                                            {incident.title}
                                        </option>
                                    ))}
                                </select>
                            ) : (
                                <div className="p-4 bg-muted/50 rounded-lg text-muted-foreground text-sm">
                                    No incidents found. Create an incident first to upload evidence.
                                </div>
                            )}
                        </div>

                        {/* File Upload Area */}
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-2">
                                Upload Files
                            </label>
                            <FileDropzone
                                onFilesAdded={handleFilesSelected}
                                disabled={isUploading || incidents.length === 0}
                                maxFiles={10}
                                maxSize={50 * 1024 * 1024}
                                accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.xls,.xlsx"
                            />
                        </div>

                        {/* Selected Files List */}
                        {selectedFiles.length > 0 && (
                            <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                    <h3 className="text-sm font-medium text-foreground">
                                        Selected Files ({selectedFiles.length})
                                    </h3>
                                    <span className="text-xs text-muted-foreground">
                                        {(totalSize / 1024 / 1024).toFixed(2)} MB
                                    </span>
                                </div>

                                <div className="space-y-2 max-h-48 overflow-y-auto">
                                    {selectedFiles.map((file, index) => (
                                        <div
                                            key={`${file.name}-${index}`}
                                            className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                                        >
                                            <div className="flex items-center gap-3 flex-1 min-w-0">
                                                <Icon name="File" size="sm" className="flex-shrink-0" />
                                                <div className="min-w-0">
                                                    <p className="text-sm font-medium text-foreground truncate">
                                                        {file.name}
                                                    </p>
                                                    <p className="text-xs text-muted-foreground">
                                                        {(file.size / 1024 / 1024).toFixed(2)} MB
                                                    </p>
                                                </div>
                                            </div>
                                            <button
                                                onClick={() => handleRemoveFile(index)}
                                                className="p-1 hover:bg-destructive/10 rounded transition-colors flex-shrink-0"
                                                aria-label="Remove file"
                                            >
                                                <Icon name="X" size="sm" className="text-destructive" />
                                            </button>
                                        </div>
                                    ))}
                                </div>

                                {isOverLimit && (
                                    <div className="flex items-center gap-2 p-3 bg-destructive/10 rounded-lg">
                                        <Icon name="AlertCircle" size="sm" className="text-destructive flex-shrink-0" />
                                        <p className="text-sm text-destructive">
                                            Total file size exceeds 100MB limit
                                        </p>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Error Message */}
                        {uploadError && (
                            <div className="flex items-center gap-2 p-3 bg-destructive/10 rounded-lg">
                                <Icon name="AlertCircle" size="sm" className="text-destructive flex-shrink-0" />
                                <p className="text-sm text-destructive">{uploadError}</p>
                            </div>
                        )}
                    </div>

                    {/* Footer */}
                    <div className="flex items-center justify-end gap-3 p-6 border-t border-border sticky bottom-0 bg-card">
                        <Button variant="outline" onClick={onClose} disabled={isUploading}>
                            Cancel
                        </Button>
                        <Button
                            onClick={handleUpload}
                            disabled={selectedFiles.length === 0 || isUploading || isOverLimit || incidents.length === 0}
                            className="gap-2"
                        >
                            {isUploading ? (
                                <>
                                    <Icon name="Loader" size="sm" className="animate-spin" />
                                    Uploading...
                                </>
                            ) : (
                                <>
                                    <Icon name="Upload" size="sm" />
                                    Upload Files
                                </>
                            )}
                        </Button>
                    </div>
                </div>
            </div>
        </>
    );
}
