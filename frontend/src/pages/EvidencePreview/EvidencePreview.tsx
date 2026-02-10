import { useEffect, useState } from 'preact/hooks';
import { Button } from '../../components/atoms/Button/Button';
import { Icon } from '../../components/atoms/Icon/Icon';
import { getEvidenceById, downloadEvidence, getEvidencePreviewUrl, type EvidenceItem } from '../../services/evidence';

export function EvidencePreview({ id }: { id?: string }) {
    const [evidence, setEvidence] = useState<EvidenceItem | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);

    const evidenceId = id;

    useEffect(() => {
        if (!evidenceId) return;

        const loadEvidence = async () => {
            try {
                setIsLoading(true);
                const data = await getEvidenceById(parseInt(evidenceId));
                setEvidence(data);
                setPreviewUrl(getEvidencePreviewUrl(parseInt(evidenceId)));
                setError(null);
            } catch (err) {
                const errorMessage = err instanceof Error ? err.message : 'Failed to load evidence';
                setError(errorMessage);
            } finally {
                setIsLoading(false);
            }
        };

        loadEvidence();
    }, [evidenceId]);

    const handleDownload = async () => {
        if (!evidence) return;
        try {
            await downloadEvidence(evidence.id);
        } catch (err) {
            alert(err instanceof Error ? err.message : 'Failed to download');
        }
    };

    const getPreviewComponent = () => {
        if (!evidence || !previewUrl) return null;

        const mimeType = evidence.file_type || '';

        // Image preview
        if (mimeType.startsWith('image/')) {
            return (
                <div className="flex items-center justify-center bg-black h-full">
                    <img
                        src={previewUrl}
                        alt={evidence.file_name}
                        className="max-w-full max-h-full object-contain"
                    />
                </div>
            );
        }

        // Video preview
        if (mimeType.startsWith('video/')) {
            return (
                <div className="flex items-center justify-center bg-black h-full">
                    <video
                        controls
                        className="max-w-full max-h-full"
                        style="max-height: 90vh; max-width: 90vw;"
                    >
                        <source src={previewUrl} type={mimeType} />
                        Your browser does not support the video tag.
                    </video>
                </div>
            );
        }

        // Audio preview
        if (mimeType.startsWith('audio/')) {
            return (
                <div className="flex items-center justify-center h-full">
                    <div className="bg-card p-8 rounded-xl border border-border">
                        <Icon name="Mic" size="xl" className="text-primary mx-auto mb-4" />
                        <p className="text-foreground mb-4 font-medium">{evidence.file_name}</p>
                        <audio controls className="w-96">
                            <source src={previewUrl} type={mimeType} />
                            Your browser does not support the audio tag.
                        </audio>
                    </div>
                </div>
            );
        }

        // PDF and document preview
        if (mimeType.includes('pdf') || mimeType.includes('document')) {
            return (
                <div className="flex items-center justify-center h-full bg-gray-900">
                    <iframe
                        src={previewUrl}
                        className="w-full h-full"
                        title={evidence.file_name}
                    />
                </div>
            );
        }

        // Fallback for unsupported types
        return (
            <div className="flex flex-col items-center justify-center h-full">
                <Icon name="FileX" size="xl" className="text-muted-foreground mb-4" />
                <p className="text-foreground mb-2">Preview not available</p>
                <p className="text-muted-foreground text-sm mb-4">{evidence.file_type || 'Unknown type'}</p>
                <Button onClick={handleDownload} className="gap-2">
                    <Icon name="Download" size="sm" />
                    Download File
                </Button>
            </div>
        );
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-screen bg-background">
                <div className="text-center">
                    <Icon name="Loader" size="lg" className="animate-spin mx-auto mb-4 text-primary" />
                    <p className="text-muted-foreground">Loading evidence...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-screen bg-background">
                <div className="text-center max-w-md">
                    <Icon name="AlertCircle" size="lg" className="text-destructive mx-auto mb-4" />
                    <p className="text-destructive font-medium mb-2">Failed to load evidence</p>
                    <p className="text-muted-foreground text-sm mb-4">{error}</p>
                    <Button onClick={() => window.history.back()} variant="outline">
                        Go Back
                    </Button>
                </div>
            </div>
        );
    }

    if (!evidence) {
        return (
            <div className="flex items-center justify-center h-screen bg-background">
                <div className="text-center">
                    <Icon name="FileX" size="lg" className="text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">Evidence not found</p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-screen bg-background">
            {/* Header */}
            <div className="bg-card border-b border-border p-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Button
                        size="icon"
                        variant="ghost"
                        onClick={() => window.history.back()}
                        title="Go Back"
                    >
                        <Icon name="ChevronLeft" size="sm" />
                    </Button>
                    <div>
                        <h1 className="text-lg font-semibold text-foreground truncate">{evidence.file_name}</h1>
                        <p className="text-xs text-muted-foreground">
                            {evidence.file_size ? (evidence.file_size / 1024 / 1024).toFixed(2) + ' MB • ' : ''}{evidence.file_type}
                        </p>
                    </div>
                </div>
                <Button onClick={handleDownload} className="gap-2">
                    <Icon name="Download" size="sm" />
                    Download
                </Button>
            </div>

            {/* Preview Content */}
            <div className="flex-1 overflow-auto bg-secondary/5">
                {getPreviewComponent()}
            </div>
        </div>
    );
}
