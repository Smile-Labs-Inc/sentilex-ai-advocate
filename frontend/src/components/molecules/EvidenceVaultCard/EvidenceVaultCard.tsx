import { cn } from '../../../lib/utils';
import { Icon } from '../../atoms/Icon/Icon';
import { Button } from '../../atoms/Button/Button';
import type { Evidence } from '../../../types';

export interface EvidenceVaultCardProps {
    evidence: Evidence;
    onDelete?: (id: string) => void;
    onView?: (id: string) => void;
    onDownload?: (id: string) => void;
    className?: string;
}

export function EvidenceVaultCard({ evidence, onDelete, onView, onDownload, className }: EvidenceVaultCardProps) {
    const formatDate = (date: Date) => {
        return new Intl.DateTimeFormat('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        }).format(date);
    };

    const getIconForType = (type: string) => {
        switch (type) {
            case 'image': return 'Image';
            case 'video': return 'Video';
            case 'audio': return 'Mic';
            case 'document': return 'FileText';
            case 'screenshot': return 'Monitor'; // Using Monitor as proxy for screenshot/device
            default: return 'File';
        }
    };

    return (
        <div className={cn(
            'group relative flex flex-col',
            'bg-card hover:bg-secondary/50 border border-border rounded-xl',
            'transition-all duration-300 overflow-hidden',
            className
        )}>
            {/* Thumbnail / Preview Area */}
            <div className="aspect-video w-full bg-secondary relative overflow-hidden flex items-center justify-center">
                {evidence.thumbnailUrl ? (
                    <img
                        src={evidence.thumbnailUrl}
                        alt={evidence.description || evidence.fileName}
                        className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                    />
                ) : (
                    <Icon
                        name={getIconForType(evidence.fileType)}
                        size="xl"
                        className="text-muted-foreground/30"
                    />
                )}

                {/* Overlay actions */}
                <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center gap-2">
                    <Button
                        size="icon"
                        variant="ghost"
                        className="text-white hover:bg-white/20"
                        onClick={() => onView?.(evidence.id)}
                        title="View Evidence"
                    >
                        <Icon name="Eye" size="sm" />
                    </Button>
                    <Button
                        size="icon"
                        variant="ghost"
                        className="text-white hover:bg-white/20"
                        onClick={() => onDownload?.(evidence.id)}
                        title="Download Evidence"
                    >
                        <Icon name="Download" size="sm" />
                    </Button>
                </div>

                {/* Type Badge */}
                <div className="absolute top-2 left-2 px-2 py-0.5 rounded-full bg-black/50 backdrop-blur-md text-[10px] font-medium text-white uppercase tracking-wider">
                    {evidence.fileType}
                </div>
            </div>

            {/* Content Details */}
            <div className="p-3 flex-1 flex flex-col">
                <div className="flex justify-between items-start gap-2 mb-1">
                    <h3 className="text-sm font-medium text-foreground line-clamp-1" title={evidence.fileName}>
                        {evidence.fileName}
                    </h3>
                    {evidence.isEncrypted && (
                        <Icon name="Lock" size="xs" className="text-green-500 flex-shrink-0" title="Encrypted" />
                    )}
                </div>

                <p className="text-xs text-muted-foreground line-clamp-2 mb-3 flex-1">
                    {evidence.description || 'No description provided'}
                </p>

                <div className="flex items-center justify-between text-[10px] text-muted-foreground mt-auto pt-2 border-t border-border/50">
                    <span>{(evidence.fileSize / 1024 / 1024).toFixed(2)} MB</span>
                    <span>{formatDate(evidence.uploadedAt)}</span>
                </div>
            </div>

            {/* Quick Actions (visible on hover or always accessible via menu - simplified here for atomicity) */}
            {onDelete && (
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        onDelete(evidence.id);
                    }}
                    className="absolute top-2 right-2 p-1.5 rounded-lg bg-red-500/10 text-red-500 opacity-0 group-hover:opacity-100 hover:bg-red-500 hover:text-white transition-all duration-200"
                    title="Delete Evidence"
                >
                    <Icon name="Trash2" size="sm" />
                </button>
            )}
        </div>
    );
}
