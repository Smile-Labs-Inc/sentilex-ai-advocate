import { useState } from 'preact/hooks';
import { DashboardLayout } from '../../components/templates/DashboardLayout/DashboardLayout';
import { EvidenceVaultGrid } from '../../components/organisms/EvidenceVaultGrid/EvidenceVaultGrid';
import { Button } from '../../components/atoms/Button/Button';
import { Icon } from '../../components/atoms/Icon/Icon';
import { mockEvidenceVaultItems } from '../../data/mockEvidenceVault';
import { mockUser } from '../../data/mockData';
import type { NavItem } from '../../types';

export interface EvidenceVaultPageProps {
    onNavigate?: (item: NavItem) => void;
}

export function EvidenceVaultPage({ onNavigate }: EvidenceVaultPageProps) {
    const [items, setItems] = useState(mockEvidenceVaultItems);

    const handleDelete = (id: string) => {
        // In a real app, this would delete via API
        if (confirm('Are you sure you want to delete this evidence? This action cannot be undone.')) {
            setItems(prev => prev.filter(item => item.id !== id));
        }
    };

    return (
        <DashboardLayout
            user={mockUser}
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

                {/* Stats / Quick Info (Optional) */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-card/40 border border-border rounded-xl p-4 backdrop-blur-sm">
                        <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Total Files</div>
                        <div className="text-2xl font-bold font-['Space_Grotesk']">{items.length}</div>
                    </div>
                    <div className="bg-card/40 border border-border rounded-xl p-4 backdrop-blur-sm">
                        <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Storage Used</div>
                        <div className="text-2xl font-bold font-['Space_Grotesk']">
                            {(items.reduce((acc, curr) => acc + curr.fileSize, 0) / 1024 / 1024).toFixed(1)} MB
                        </div>
                    </div>
                    <div className="bg-card/40 border border-border rounded-xl p-4 backdrop-blur-sm">
                        <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Encrypted</div>
                        <div className="text-2xl font-bold font-['Space_Grotesk'] text-green-500">100%</div>
                    </div>
                    <div className="bg-card/40 border border-border rounded-xl p-4 backdrop-blur-sm">
                        <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Last Upload</div>
                        <div className="text-lg font-bold font-['Space_Grotesk'] truncate">
                            {new Date().toLocaleDateString()}
                        </div>
                    </div>
                </div>

                {/* Grid */}
                <div className="flex-1 min-h-[500px] bg-card/20 border border-border/50 rounded-2xl p-6 backdrop-blur-sm">
                    <EvidenceVaultGrid
                        items={items}
                        onDeleteItem={handleDelete}
                    />
                </div>
            </div>
        </DashboardLayout>
    );
}
