import { DashboardLayout } from '../../components/templates/DashboardLayout/DashboardLayout';
import { EvidenceVaultGrid } from '../../components/organisms/EvidenceVaultGrid/EvidenceVaultGrid';
import { Button } from '../../components/atoms/Button/Button';
import { Icon } from '../../components/atoms/Icon/Icon';
import { useAuth } from '../../hooks/useAuth';
import { useEvidenceVault } from '../../hooks/useEvidenceVault';
import type { NavItem } from '../../types';
import type { Evidence } from '../../types';

export interface EvidenceVaultPageProps {
    onNavigate?: (item: NavItem) => void;
}

export function EvidenceVaultPage({ onNavigate }: EvidenceVaultPageProps) {
    const { user } = useAuth();
    const {
        evidence,
        isLoading,
        error,
        totalCount,
        deleteEvidence: deleteEvidenceById,
    } = useEvidenceVault();

    if (!user) {
        return null;
    }

    const handleDelete = async (id: string) => {
        if (confirm('Are you sure you want to delete this evidence? This action cannot be undone.')) {
            try {
                await deleteEvidenceById(parseInt(id));
            } catch (err) {
                alert(err instanceof Error ? err.message : 'Failed to delete evidence');
            }
        }
    };

    // Convert API evidence to component format
    const evidenceItems: Evidence[] = evidence.map((item) => ({
        id: item.id.toString(),
        fileName: item.file_name,
        fileSize: item.file_size || 0,
        fileType: getEvidenceTypeFromMime(item.file_type || ''),
        mimeType: item.file_type || '',
        uploadedAt: new Date(item.uploaded_at),
        description: item.description || '',
        isEncrypted: true,
        thumbnailUrl: item.thumbnail_url || undefined,
    }));

    // Helper to determine evidence type from MIME type
    function getEvidenceTypeFromMime(mimeType: string): Evidence['fileType'] {
        if (mimeType.startsWith('image/')) return 'image';
        if (mimeType.startsWith('video/')) return 'video';
        if (mimeType.startsWith('audio/')) return 'audio';
        if (mimeType.includes('pdf') || mimeType.includes('document')) return 'document';
        if (mimeType.startsWith('image/') && mimeType.includes('screenshot')) return 'screenshot';
        return 'other';
    }

    return (
        <DashboardLayout
            user={user}
            currentPath="/evidence"
            onNavigate={onNavigate}
        >
            <div className="flex flex-col h-full space-y-6">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-3xl font-bold text-foreground font-['Space_Grotesk'] tracking-tight">
                            Evidence Vault
                        </h1>
                        <p className="text-muted-foreground mt-1">
                            Secure storage for all your case-related files and documentation.
                        </p>
                    </div>
                    <Button className="gap-2 shadow-lg shadow-primary/20">
                        <Icon name="Upload" size="sm" />
                        Upload New Evidence
                    </Button>
                </div>

                {/* Stats / Quick Info */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-card/40 border border-border rounded-xl p-4 backdrop-blur-sm">
                        <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Total Files</div>
                        <div className="text-2xl font-bold font-['Space_Grotesk']">{totalCount}</div>
                    </div>
                    <div className="bg-card/40 border border-border rounded-xl p-4 backdrop-blur-sm">
                        <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Storage Used</div>
                        <div className="text-2xl font-bold font-['Space_Grotesk']">
                            {(evidence.reduce((acc, curr) => acc + (curr.file_size || 0), 0) / 1024 / 1024).toFixed(1)} MB
                        </div>
                    </div>
                    <div className="bg-card/40 border border-border rounded-xl p-4 backdrop-blur-sm">
                        <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Encrypted</div>
                        <div className="text-2xl font-bold font-['Space_Grotesk'] text-green-500">100%</div>
                    </div>
                    <div className="bg-card/40 border border-border rounded-xl p-4 backdrop-blur-sm">
                        <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Last Upload</div>
                        <div className="text-lg font-bold font-['Space_Grotesk'] truncate">
                            {evidence.length > 0
                                ? new Date(evidence[0].uploaded_at).toLocaleDateString()
                                : 'N/A'
                            }
                        </div>
                    </div>
                </div>

                {/* Grid */}
                <div className="flex-1 min-h-[500px] bg-card/20 border border-border/50 rounded-2xl p-6 backdrop-blur-sm">
                    {isLoading ? (
                        <div className="flex items-center justify-center h-full">
                            <div className="text-center">
                                <Icon name="Loader" size="lg" className="animate-spin mx-auto mb-4" />
                                <p className="text-muted-foreground">Loading evidence...</p>
                            </div>
                        </div>
                    ) : error ? (
                        <div className="flex items-center justify-center h-full">
                            <div className="text-center">
                                <Icon name="AlertCircle" size="lg" className="text-destructive mx-auto mb-4" />
                                <p className="text-destructive font-medium mb-2">Failed to load evidence</p>
                                <p className="text-muted-foreground text-sm">{error}</p>
                            </div>
                        </div>
                    ) : evidenceItems.length === 0 ? (
                        <div className="flex items-center justify-center h-full">
                            <div className="text-center">
                                <Icon name="FileX" size="lg" className="text-muted-foreground mx-auto mb-4" />
                                <p className="text-muted-foreground">No evidence files yet</p>
                                <p className="text-sm text-muted-foreground mt-2">Upload files to get started</p>
                            </div>
                        </div>
                    ) : (
                        <EvidenceVaultGrid
                            items={evidenceItems}
                            onDeleteItem={handleDelete}
                        />
                    )}
                </div>
            </div>
        </DashboardLayout>
    );
}
