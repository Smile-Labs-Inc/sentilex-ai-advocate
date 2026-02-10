import { useState } from 'preact/hooks';
import { Button } from '../../atoms/Button/Button';
import { Icon } from '../../atoms/Icon/Icon';
import { cn } from '../../../lib/utils';
import {
    exportPoliceStatement,
    exportCERTReport,
    exportEvidenceManifest,
    exportCaseFile
} from '../../../services/documents';

export interface ExportButtonProps {
    incidentId: number;
    className?: string;
    variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive';
    size?: 'sm' | 'md' | 'lg';
}

type ExportType = 'police' | 'cert' | 'manifest' | 'case-file';

export function ExportButton({ incidentId, className, variant = 'primary', size = 'sm' }: ExportButtonProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [isExporting, setIsExporting] = useState(false);
    const [exportingType, setExportingType] = useState<ExportType | null>(null);

    const handleExport = async (type: ExportType) => {
        setIsExporting(true);
        setExportingType(type);
        setIsOpen(false);

        try {
            switch (type) {
                case 'police':
                    await exportPoliceStatement(incidentId);
                    break;
                case 'cert':
                    await exportCERTReport(incidentId);
                    break;
                case 'manifest':
                    await exportEvidenceManifest(incidentId);
                    break;
                case 'case-file':
                    await exportCaseFile(incidentId);
                    break;
            }
        } catch (error) {
            console.error('Export failed:', error);
            alert(error instanceof Error ? error.message : 'Failed to export document');
        } finally {
            setIsExporting(false);
            setExportingType(null);
        }
    };

    return (
        <div className={cn('relative', className)}>
            <Button
                variant={variant}
                size={size}
                className="gap-1.5 text-xs"
                onClick={() => setIsOpen(!isOpen)}
                disabled={isExporting}
            >
                {isExporting ? (
                    <>
                        <Icon name="Loader" size="xs" className="animate-spin" />
                        Exporting...
                    </>
                ) : (
                    <>
                        <Icon name="Download" size="xs" />
                        Export
                        <Icon name="ChevronDown" size="xs" className={cn(
                            'transition-transform',
                            isOpen && 'rotate-180'
                        )} />
                    </>
                )}
            </Button>

            {isOpen && !isExporting && (
                <>
                    {/* Backdrop */}
                    <div
                        className="fixed inset-0 z-40"
                        onClick={() => setIsOpen(false)}
                    />

                    {/* Dropdown Menu */}
                    <div className="absolute right-0 mt-2 w-72 bg-card border border-border rounded-xl shadow-2xl z-50 overflow-hidden">
                        <div className="p-2 space-y-1">
                            {/* Police Statement */}
                            <button
                                onClick={() => handleExport('police')}
                                className="w-full flex items-start gap-3 p-3 rounded-lg hover:bg-secondary transition-colors text-left"
                            >
                                <Icon name="FileText" size="sm" className="text-primary mt-0.5" />
                                <div className="flex-1">
                                    <div className="font-medium text-foreground">Police Statement</div>
                                    <div className="text-xs text-muted-foreground mt-0.5">
                                        C-Form equivalent for law enforcement
                                    </div>
                                </div>
                            </button>

                            {/* CERT Report */}
                            <button
                                onClick={() => handleExport('cert')}
                                className="w-full flex items-start gap-3 p-3 rounded-lg hover:bg-secondary transition-colors text-left"
                            >
                                <Icon name="Shield" size="sm" className="text-primary mt-0.5" />
                                <div className="flex-1">
                                    <div className="font-medium text-foreground">CERT Technical Report</div>
                                    <div className="text-xs text-muted-foreground mt-0.5">
                                        Technical analysis for Sri Lanka CERT
                                    </div>
                                </div>
                            </button>

                            {/* Evidence Manifest */}
                            <button
                                onClick={() => handleExport('manifest')}
                                className="w-full flex items-start gap-3 p-3 rounded-lg hover:bg-secondary transition-colors text-left"
                            >
                                <Icon name="List" size="sm" className="text-primary mt-0.5" />
                                <div className="flex-1">
                                    <div className="font-medium text-foreground">Evidence Manifest</div>
                                    <div className="text-xs text-muted-foreground mt-0.5">
                                        Detailed listing of all evidence files
                                    </div>
                                </div>
                            </button>

                            {/* Divider */}
                            <div className="h-px bg-border my-2" />

                            {/* Complete Case File */}
                            <button
                                onClick={() => handleExport('case-file')}
                                className="w-full flex items-start gap-3 p-3 rounded-lg hover:bg-secondary transition-colors text-left bg-primary/5"
                            >
                                <Icon name="Package" size="sm" className="text-primary mt-0.5" />
                                <div className="flex-1">
                                    <div className="font-medium text-foreground">Complete Case File</div>
                                    <div className="text-xs text-muted-foreground mt-0.5">
                                        ZIP with all documents and evidence
                                    </div>
                                </div>
                            </button>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
