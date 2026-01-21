// =============================================================================
// EvidenceSection Organism
// Complete evidence management section with upload and list
// =============================================================================

import { useState } from 'preact/hooks';
import { cn } from '../../../lib/utils';
import { Card, CardHeader, CardTitle } from '../../atoms/Card/Card';
import { Button } from '../../atoms/Button/Button';
import { Icon } from '../../atoms/Icon/Icon';
import { FileDropzone } from '../../atoms/FileDropzone/FileDropzone';
import { EvidenceItem } from '../../molecules/EvidenceItem/EvidenceItem';
import type { Evidence } from '../../../types';

export interface EvidenceSectionProps {
    evidence: Evidence[];
    onAddEvidence: (files: File[]) => void;
    onDeleteEvidence: (evidence: Evidence) => void;
    onViewEvidence?: (evidence: Evidence) => void;
    onAddNote?: (evidence: Evidence) => void;
    className?: string;
}



export function EvidenceSection({
    evidence,
    onAddEvidence,
    onDeleteEvidence,
    onViewEvidence,
    onAddNote,
    className,
}: EvidenceSectionProps) {
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
    const [showUpload, setShowUpload] = useState(evidence.length === 0);

    const handleFilesAdded = (files: File[]) => {
        onAddEvidence(files);
        setShowUpload(false);
    };

    return (
        <Card variant="default" padding="lg" className={cn('animate-slide-up', className)}>
            <CardHeader>
                <div className="flex items-center gap-2">
                    <Icon name="FileArchive" size="sm" className="text-blue-400" />
                    <CardTitle className="text-sm">Evidence</CardTitle>
                    <span className="ml-2 px-2 py-0.5 text-xs bg-secondary text-muted-foreground rounded-full">
                        {evidence.length} files
                    </span>
                    {evidence.length > 0 && (
                        <span className="flex items-center gap-1 text-xs text-green-400">
                            <Icon name="Lock" size="xs" />
                            Encrypted
                        </span>
                    )}
                </div>

                <div className="flex items-center gap-2">
                    {/* View mode toggle */}
                    <div className="flex bg-secondary rounded-lg p-0.5">
                        <button
                            className={cn(
                                'p-1.5 rounded transition-colors',
                                viewMode === 'grid' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'
                            )}
                            onClick={() => setViewMode('grid')}
                        >
                            <Icon name="Grid3X3" size="sm" />
                        </button>
                        <button
                            className={cn(
                                'p-1.5 rounded transition-colors',
                                viewMode === 'list' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'
                            )}
                            onClick={() => setViewMode('list')}
                        >
                            <Icon name="List" size="sm" />
                        </button>
                    </div>

                    {/* Add button */}
                    <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => setShowUpload(!showUpload)}
                    >
                        <Icon name={showUpload ? 'X' : 'Plus'} size="xs" />
                        {showUpload ? 'Cancel' : 'Add'}
                    </Button>
                </div>
            </CardHeader>

            {/* Upload dropzone */}
            {showUpload && (
                <div className="mb-4 animate-slide-up">
                    <FileDropzone onFilesAdded={handleFilesAdded} />
                </div>
            )}

            {/* Evidence list */}
            {evidence.length === 0 && !showUpload ? (
                <div className="text-center py-8">
                    <Icon name="FileArchive" size="lg" className="text-muted-foreground/50 mx-auto mb-3" />
                    <p className="text-sm text-muted-foreground mb-2">No evidence uploaded yet</p>
                    <p className="text-xs text-muted-foreground mb-4">
                        Upload screenshots, documents, or other files to support your case
                    </p>
                    <Button variant="secondary" size="sm" onClick={() => setShowUpload(true)}>
                        <Icon name="Upload" size="sm" />
                        Upload Evidence
                    </Button>
                </div>
            ) : evidence.length > 0 && (
                <div className={cn(
                    viewMode === 'grid'
                        ? 'grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3'
                        : 'space-y-2'
                )}>
                    {evidence.map((item) => (
                        <EvidenceItem
                            key={item.id}
                            evidence={item}
                            variant={viewMode}
                            onView={onViewEvidence}
                            onDelete={onDeleteEvidence}
                            onAddNote={onAddNote}
                        />
                    ))}
                </div>
            )}

            {/* Security note */}
            {evidence.length > 0 && (
                <div className="mt-4 p-3 bg-green-500/5 border border-green-500/20 rounded-lg">
                    <div className="flex items-start gap-2">
                        <Icon name="ShieldCheck" size="sm" className="text-green-400 mt-0.5" />
                        <div>
                            <p className="text-xs text-green-300 font-medium">
                                Evidence is encrypted and securely stored
                            </p>
                            <p className="text-xs text-muted-foreground mt-0.5">
                                Files are encrypted using AES-256 and can only be accessed by you and authorized parties.
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </Card>
    );
}

export default EvidenceSection;
