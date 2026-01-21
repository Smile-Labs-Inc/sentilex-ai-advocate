import { useState } from 'preact/hooks';
import { cn } from '../../../lib/utils';
import { EvidenceVaultCard } from '../../molecules/EvidenceVaultCard/EvidenceVaultCard';
import { SearchInput } from '../../molecules/SearchInput/SearchInput';
import { Button } from '../../atoms/Button/Button';
import { Icon } from '../../atoms/Icon/Icon';
import type { Evidence } from '../../../types';

export interface EvidenceVaultGridProps {
    items: Evidence[];
    onDeleteItem: (id: string) => void;
    className?: string;
}

type SortOption = 'date-desc' | 'date-asc' | 'size-desc' | 'name-asc';
type FilterType = 'all' | 'image' | 'video' | 'document' | 'audio';

export function EvidenceVaultGrid({ items, onDeleteItem, className }: EvidenceVaultGridProps) {
    const [searchQuery, setSearchQuery] = useState('');
    const [sortOption] = useState<SortOption>('date-desc');
    const [filterType, setFilterType] = useState<FilterType>('all');
    const [isViewModeList, setIsViewModeList] = useState(false);

    // Filter and Sort Logic
    const filteredItems = items
        .filter(item => {
            const matchesSearch = item.fileName.toLowerCase().includes(searchQuery.toLowerCase()) ||
                (item.description?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false);
            const matchesType = filterType === 'all' || item.fileType === filterType;
            return matchesSearch && matchesType;
        })
        .sort((a, b) => {
            switch (sortOption) {
                case 'date-desc': return b.uploadedAt.getTime() - a.uploadedAt.getTime();
                case 'date-asc': return a.uploadedAt.getTime() - b.uploadedAt.getTime();
                case 'size-desc': return b.fileSize - a.fileSize;
                case 'name-asc': return a.fileName.localeCompare(b.fileName);
                default: return 0;
            }
        });

    return (
        <div className={cn('flex flex-col h-full gap-6', className)}>
            {/* Toolbar */}
            <div className="flex flex-col md:flex-row gap-4 items-center justify-between bg-card/50 p-4 rounded-xl border border-border backdrop-blur-sm">

                {/* Search */}
                <div className="w-full md:w-72">
                    <SearchInput
                        placeholder="Search evidence..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery((e.target as HTMLInputElement).value)}
                    />
                </div>

                {/* Actions */}
                <div className="flex items-center gap-3 w-full md:w-auto overflow-x-auto pb-2 md:pb-0">
                    {/* Filter Tabs (Simplified for this view) */}
                    <div className="flex items-center bg-secondary rounded-lg p-1 mr-2">
                        {(['all', 'image', 'video', 'document'] as const).map((type) => (
                            <button
                                key={type}
                                onClick={() => setFilterType(type as FilterType)}
                                className={cn(
                                    'px-3 py-1.5 text-xs font-medium rounded-md transition-all',
                                    filterType === type
                                        ? 'bg-background text-foreground shadow-sm'
                                        : 'text-muted-foreground hover:text-foreground'
                                )}
                            >
                                {type.charAt(0).toUpperCase() + type.slice(1)}
                            </button>
                        ))}
                    </div>

                    <div className="h-4 w-px bg-border mx-1" />

                    {/* Sort Dropdown (Mock visual) */}
                    <div className="relative group">
                        <Button variant="outline" size="sm" className="gap-2 text-xs h-9">
                            <Icon name="ArrowUpDown" size="xs" />
                            Sort
                        </Button>
                        {/* Simple dropdown content could go here, for now cycling sort or just static for MVP */}
                    </div>

                    {/* View Toggle */}
                    <div className="flex items-center bg-secondary rounded-lg p-1">
                        <button
                            onClick={() => setIsViewModeList(false)}
                            className={cn('p-1.5 rounded-md transition-colors', !isViewModeList ? 'bg-background shadow-sm' : 'text-muted-foreground')}
                        >
                            <Icon name="LayoutGrid" size="xs" />
                        </button>
                        <button
                            onClick={() => setIsViewModeList(true)}
                            className={cn('p-1.5 rounded-md transition-colors', isViewModeList ? 'bg-background shadow-sm' : 'text-muted-foreground')}
                        >
                            <Icon name="List" size="xs" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Grid Content */}
            {filteredItems.length === 0 ? (
                <div className="flex flex-col items-center justify-center p-12 border-2 border-dashed border-border/50 rounded-xl bg-secondary/20">
                    <div className="w-16 h-16 bg-secondary rounded-full flex items-center justify-center mb-4">
                        <Icon name="Search" size="lg" className="text-muted-foreground" />
                    </div>
                    <h3 className="text-lg font-medium text-foreground mb-1">No evidence found</h3>
                    <p className="text-sm text-muted-foreground">Try adjusting your search or filters</p>
                </div>
            ) : (
                <div className={cn(
                    'grid gap-4 animate-fade-in',
                    isViewModeList
                        ? 'grid-cols-1'
                        : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
                )}>
                    {filteredItems.map((item) => (
                        <EvidenceVaultCard
                            key={item.id}
                            evidence={item}
                            onDelete={onDeleteItem}
                            className={isViewModeList ? 'flex-row h-24' : ''} // basic handling for list view adaptation if card supports it, else grid
                        />
                    ))}
                </div>
            )}
        </div>
    );
}
