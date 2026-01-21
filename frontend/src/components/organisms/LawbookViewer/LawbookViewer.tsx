import { useEffect } from 'preact/hooks';
import { cn } from '../../../lib/utils';
import { Button } from '../../atoms/Button/Button';
import { Icon } from '../../atoms/Icon/Icon';
import type { LawbookChapter, Bookmark } from '../../../types';
import type { IconName } from '../../atoms/Icon/Icon';

export interface LawbookViewerProps {
    chapter: LawbookChapter;
    activeSectionId?: string;
    bookmarks: Bookmark[];
    onToggleBookmark: (chapterId: string, sectionId: string, title: string) => void;
    className?: string;
}

export function LawbookViewer({
    chapter,
    activeSectionId,
    bookmarks,
    onToggleBookmark,
    className
}: LawbookViewerProps) {

    // Simple scroll to section logic could happen here
    useEffect(() => {
        if (activeSectionId) {
            const el = document.getElementById(activeSectionId);
            if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    }, [activeSectionId]);

    const isBookmarked = (sectionId: string) => {
        return bookmarks.some(b => b.chapterId === chapter.id && b.sectionId === sectionId);
    };

    return (
        <div className={cn('flex flex-col h-full overflow-y-auto px-8 py-6', className)}>
            {/* Chapter Header */}
            <div className="mb-8 border-b border-border pb-6">
                <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-primary/10 rounded-lg text-primary">
                        <Icon name={(chapter.icon as IconName) || 'BookOpen'} size="md" />
                    </div>
                    <span className="text-xs font-semibold text-primary uppercase tracking-widest">
                        Chapter
                    </span>
                </div>
                <h1 className="text-3xl font-bold text-foreground font-['Space_Grotesk']">
                    {chapter.title}
                </h1>
            </div>

            {/* Sections */}
            <div className="space-y-12 pb-20">
                {chapter.sections.map((section) => (
                    <div
                        key={section.id}
                        id={section.id}
                        className="group relative scroll-mt-24" // scroll margin for sticky headers
                    >
                        {/* Section Actions (Bookmark) */}
                        <div className="absolute -left-12 top-0 opacity-0 group-hover:opacity-100 transition-opacity hidden lg:block">
                            <Button
                                size="icon"
                                variant="ghost"
                                className={cn(
                                    "hover:bg-accent",
                                    isBookmarked(section.id) ? "text-yellow-500" : "text-muted-foreground"
                                )}
                                onClick={() => onToggleBookmark(chapter.id, section.id, section.title)}
                                title={isBookmarked(section.id) ? "Remove Bookmark" : "Bookmark this section"}
                            >
                                <Icon name="Bookmark" size="sm" className={isBookmarked(section.id) ? "fill-current" : ""} />
                            </Button>
                        </div>

                        {/* Mobile bookmark button (visible always or simplistic) */}
                        <div className="lg:hidden flex justify-end mb-2">
                            <Button
                                size="sm"
                                variant="ghost"
                                className={cn("gap-2", isBookmarked(section.id) ? "text-yellow-500" : "text-muted-foreground")}
                                onClick={() => onToggleBookmark(chapter.id, section.id, section.title)}
                            >
                                <Icon name="Bookmark" size="xs" className={isBookmarked(section.id) ? "fill-current" : ""} />
                                {isBookmarked(section.id) ? "Bookmarked" : "Bookmark"}
                            </Button>
                        </div>

                        {/* Content Rendering */}
                        <div className="prose prose-zinc dark:prose-invert max-w-none">
                            {/* 
                                Since we don't have a markdown parser installed yet, 
                                we'll use a simple strategy to render the text content 
                                preserving whitespace and basic structure.
                            */}
                            <div className="whitespace-pre-wrap font-sans text-base leading-relaxed text-muted-foreground">
                                {section.content.split('\n').map((line, i) => {
                                    // Ultra-simple "markdown" styling
                                    if (line.trim().startsWith('# ')) {
                                        return <h2 key={i} className="text-2xl font-bold text-foreground mt-6 mb-4">{line.replace('# ', '')}</h2>;
                                    }
                                    if (line.trim().startsWith('## ')) {
                                        return <h3 key={i} className="text-xl font-bold text-foreground mt-5 mb-3">{line.replace('## ', '')}</h3>;
                                    }
                                    if (line.trim().startsWith('### ')) {
                                        return <h4 key={i} className="text-lg font-semibold text-foreground mt-4 mb-2">{line.replace('### ', '')}</h4>;
                                    }
                                    if (line.trim().startsWith('- ')) {
                                        return <li key={i} className="ml-4 list-disc marker:text-primary">{line.replace('- ', '')}</li>;
                                    }
                                    if (line.trim().startsWith('**') && line.trim().endsWith('**')) {
                                        // Very rough bold handling for full lines
                                        return <p key={i} className="font-bold text-foreground my-2">{line.replace(/\*\*/g, '')}</p>;
                                    }

                                    return <p key={i} className="mb-2">{line}</p>;
                                })}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
