// =============================================================================
// EvidenceItem Molecule
// Displays a single piece of evidence with actions
// =============================================================================

import { cn } from '../../../lib/utils';
import { Icon, type IconName } from '../../atoms/Icon/Icon';
import { Button } from '../../atoms/Button/Button';
import type { Evidence, EvidenceType } from '../../../types';

export interface EvidenceItemProps {
    evidence: Evidence;
    onView?: (evidence: Evidence) => void;
    onDelete?: (evidence: Evidence) => void;
    onAddNote?: (evidence: Evidence) => void;
    variant?: 'grid' | 'list';
    className?: string;
}

const fileTypeIcons: Record<EvidenceType, IconName> = {
    image: 'Image',
    video: 'Video',
    document: 'FileText',
    audio: 'Music',
    screenshot: 'Monitor',
    other: 'File',
};

const fileTypeColors: Record<EvidenceType, string> = {
    image: 'text-blue-400 bg-blue-500/10',
    video: 'text-purple-400 bg-purple-500/10',
    document: 'text-orange-400 bg-orange-500/10',
    audio: 'text-green-400 bg-green-500/10',
    screenshot: 'text-cyan-400 bg-cyan-500/10',
    other: 'text-muted-foreground bg-secondary',
};

const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};

const formatDate = (date: Date): string => {
    return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    }).format(date);
};

export function EvidenceItem({
    evidence,
    onView,
    onDelete,
    onAddNote,
    variant = 'grid',
    className,
}: EvidenceItemProps) {
    const iconName = fileTypeIcons[evidence.fileType];
    const colorClass = fileTypeColors[evidence.fileType];

    if (variant === 'list') {
        return (
            <div
                className={cn(
                    'flex items-center gap-4 p-4 rounded-lg',
                    'bg-secondary/30 border border-border',
                    'hover:border-input transition-all duration-300',
                    'group',
                    className
                )}
            >
                {/* Icon */}
                <div className={cn(
                    'w-10 h-10 rounded-lg flex items-center justify-center',
                    colorClass
                )}>
                    <Icon name={iconName} size="sm" />
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                        <p className="text-sm font-medium text-foreground truncate">
                            {evidence.fileName}
                        </p>
                        {evidence.isEncrypted && (
                            <Icon name="Lock" size="xs" className="text-green-400" />
                        )}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                        <span>{formatFileSize(evidence.fileSize)}</span>
                        <span>•</span>
                        <span>{formatDate(evidence.uploadedAt)}</span>
                    </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    {onView && (
                        <Button variant="ghost" size="icon" onClick={() => onView(evidence)}>
                            <Icon name="Eye" size="sm" />
                        </Button>
                    )}
                    {onAddNote && (
                        <Button variant="ghost" size="icon" onClick={() => onAddNote(evidence)}>
                            <Icon name="MessageSquare" size="sm" />
                        </Button>
                    )}
                    {onDelete && (
                        <Button variant="ghost" size="icon" onClick={() => onDelete(evidence)}>
                            <Icon name="Trash2" size="sm" className="text-red-400" />
                        </Button>
                    )}
                </div>
            </div>
        );
    }

    // Grid variant
    return (
        <div
            className={cn(
                'relative p-4 rounded-xl',
                'bg-secondary/30 border border-border',
                'hover:border-input transition-all duration-300',
                'group cursor-pointer',
                className
            )}
            onClick={() => onView?.(evidence)}
        >
            {/* Thumbnail or Icon */}
            <div className={cn(
                'w-full aspect-square rounded-lg mb-3 flex items-center justify-center overflow-hidden',
                colorClass
            )}>
                {evidence.thumbnailUrl ? (
                    <img
                        src={evidence.thumbnailUrl}
                        alt={evidence.fileName}
                        className="w-full h-full object-cover"
                    />
                ) : (
                    <Icon name={iconName} size="xl" />
                )}
            </div>

            {/* File info */}
            <div className="space-y-1">
                <p className="text-sm font-medium text-foreground truncate">
                    {evidence.fileName}
                </p>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{formatFileSize(evidence.fileSize)}</span>
                    {evidence.isEncrypted && (
                        <span className="flex items-center gap-1 text-green-400">
                            <Icon name="Lock" size="xs" />
                            Encrypted
                        </span>
                    )}
                </div>
            </div>

            {/* Description badge */}
            {evidence.description && (
                <div className="mt-2 p-2 bg-secondary/50 rounded text-xs text-muted-foreground line-clamp-2">
                    {evidence.description}
                </div>
            )}

            {/* Hover actions */}
            <div className={cn(
                'absolute top-2 right-2 flex gap-1',
                'opacity-0 group-hover:opacity-100 transition-opacity'
            )}>
                {onAddNote && (
                    <Button
                        variant="secondary"
                        size="icon"
                        onClick={(e) => { e.stopPropagation(); onAddNote(evidence); }}
                        className="w-7 h-7"
                    >
                        <Icon name="MessageSquare" size="xs" />
                    </Button>
                )}
                {onDelete && (
                    <Button
                        variant="secondary"
                        size="icon"
                        onClick={(e) => { e.stopPropagation(); onDelete(evidence); }}
                        className="w-7 h-7"
                    >
                        <Icon name="Trash2" size="xs" className="text-red-400" />
                    </Button>
                )}
            </div>
        </div>
    );
}

export default EvidenceItem;
