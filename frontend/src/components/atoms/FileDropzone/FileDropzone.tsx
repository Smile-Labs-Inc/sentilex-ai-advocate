// =============================================================================
// FileDropzone Atom
// Drag-and-drop file upload component with visual feedback
// =============================================================================

import { useState, useRef } from 'preact/hooks';
import { cn } from '../../../lib/utils';
import { Icon } from '../Icon/Icon';
import { Button } from '../Button/Button';

export interface FileDropzoneProps {
    onFilesAdded: (files: File[]) => void;
    accept?: string;
    maxSize?: number; // in bytes
    maxFiles?: number;
    disabled?: boolean;
    className?: string;
}

const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export function FileDropzone({
    onFilesAdded,
    accept = 'image/*,.pdf,.doc,.docx,.txt',
    maxSize = 10 * 1024 * 1024, // 10MB default
    maxFiles = 10,
    disabled = false,
    className,
}: FileDropzoneProps) {
    const [isDragActive, setIsDragActive] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    const validateFiles = (files: File[]): File[] => {
        const validFiles: File[] = [];

        for (const file of files) {
            if (file.size > maxSize) {
                setError(`${file.name} exceeds ${formatFileSize(maxSize)} limit`);
                continue;
            }
            validFiles.push(file);
        }

        if (validFiles.length > maxFiles) {
            setError(`Maximum ${maxFiles} files allowed`);
            return validFiles.slice(0, maxFiles);
        }

        return validFiles;
    };

    const handleDrag = (e: DragEvent) => {
        e.preventDefault();
        e.stopPropagation();

        if (disabled) return;

        if (e.type === 'dragenter' || e.type === 'dragover') {
            setIsDragActive(true);
        } else if (e.type === 'dragleave') {
            setIsDragActive(false);
        }
    };

    const handleDrop = (e: DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragActive(false);
        setError(null);

        if (disabled) return;

        const files = Array.from(e.dataTransfer?.files || []);
        const validFiles = validateFiles(files);

        if (validFiles.length > 0) {
            onFilesAdded(validFiles);
        }
    };

    const handleChange = (e: Event) => {
        setError(null);
        const target = e.target as HTMLInputElement;
        const files = Array.from(target.files || []);
        const validFiles = validateFiles(files);

        if (validFiles.length > 0) {
            onFilesAdded(validFiles);
        }

        // Reset input
        if (inputRef.current) {
            inputRef.current.value = '';
        }
    };

    const handleButtonClick = () => {
        inputRef.current?.click();
    };

    return (
        <div
            className={cn(
                'relative border-2 border-dashed rounded-xl transition-all duration-300',
                isDragActive
                    ? 'border-primary bg-primary/5 scale-[1.02]'
                    : 'border-border hover:border-input',
                disabled && 'opacity-50 cursor-not-allowed',
                className
            )}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
        >
            <input
                ref={inputRef}
                type="file"
                accept={accept}
                multiple={maxFiles > 1}
                onChange={handleChange}
                disabled={disabled}
                className="hidden"
            />

            <div className="p-8 text-center">
                {/* Icon */}
                <div className={cn(
                    'w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center transition-all duration-300',
                    isDragActive
                        ? 'bg-primary/10 scale-110'
                        : 'bg-secondary'
                )}>
                    <Icon
                        name={isDragActive ? 'Download' : 'Upload'}
                        size="lg"
                        className={cn(
                            'transition-colors',
                            isDragActive ? 'text-primary' : 'text-muted-foreground'
                        )}
                    />
                </div>

                {/* Text */}
                <p className={cn(
                    'text-sm mb-2 transition-colors',
                    isDragActive ? 'text-primary' : 'text-muted-foreground'
                )}>
                    {isDragActive
                        ? 'Drop files here...'
                        : 'Drag and drop files here, or click to browse'
                    }
                </p>

                <p className="text-xs text-muted-foreground mb-4">
                    Supports images, PDFs, and documents up to {formatFileSize(maxSize)}
                </p>

                {/* Browse button */}
                <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={handleButtonClick}
                    disabled={disabled}
                >
                    <Icon name="FolderOpen" size="sm" />
                    Browse Files
                </Button>

                {/* Error message */}
                {error && (
                    <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                        <p className="text-xs text-red-400 flex items-center justify-center gap-2">
                            <Icon name="AlertCircle" size="xs" />
                            {error}
                        </p>
                    </div>
                )}
            </div>

            {/* Drag overlay */}
            {isDragActive && (
                <div className="absolute inset-0 bg-background/5 rounded-xl pointer-events-none animate-pulse" />
            )}
        </div>
    );
}

export default FileDropzone;
