import { useEffect } from 'preact/hooks';
import ReactMarkdown from 'react-markdown';
import { cn } from '../../../lib/utils';
import { Icon } from '../../atoms/Icon/Icon';
import type { Bookmark } from '../../../types';

export interface LawbookViewerProps {
    lawId: string;
    lawTitle: string;
    markdownContent: string;
    isLoading: boolean;
    activeSectionId?: string;
    bookmarks: Bookmark[];
    onToggleBookmark: (lawId: string, sectionId: string, title: string) => void;
    className?: string;
}

export function LawbookViewer({
    lawId,
    lawTitle,
    markdownContent,
    isLoading,
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

    return (
        <div className={cn('flex flex-col h-full overflow-y-auto px-8 py-6', className)}>
            {/* Law Header */}
            <div className="mb-8 border-b border-border pb-6">
                <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-primary/10 rounded-lg text-primary">
                        <Icon name="BookOpen" size="md" />
                    </div>
                    <span className="text-xs font-semibold text-primary uppercase tracking-widest">
                        Law Document
                    </span>
                </div>
                <h1 className="text-3xl font-bold text-foreground font-['Space_Grotesk']">
                    {lawTitle}
                </h1>
            </div>

            {/* Content */}
            <div className="space-y-6 pb-20">
                {isLoading ? (
                    <div className="text-center text-muted-foreground py-8">
                        Loading content...
                    </div>
                ) : (
                    <div className="prose prose-zinc dark:prose-invert max-w-none text-foreground">
                        <ReactMarkdown
                            components={{
                                h1: ({ node, ...props }) => <h1 className="text-3xl font-bold text-foreground mt-8 mb-4" {...props} />,
                                h2: ({ node, ...props }) => <h2 className="text-2xl font-bold text-foreground mt-6 mb-3" {...props} />,
                                h3: ({ node, ...props }) => <h3 className="text-xl font-semibold text-foreground mt-5 mb-2" {...props} />,
                                h4: ({ node, ...props }) => <h4 className="text-lg font-semibold text-foreground mt-4 mb-2" {...props} />,
                                p: ({ node, ...props }) => <p className="text-muted-foreground mb-3 leading-relaxed" {...props} />,
                                ul: ({ node, ...props }) => <ul className="list-disc ml-6 mb-3 text-muted-foreground" {...props} />,
                                ol: ({ node, ...props }) => <ol className="list-decimal ml-6 mb-3 text-muted-foreground" {...props} />,
                                li: ({ node, ...props }) => <li className="mb-1" {...props} />,
                                strong: ({ node, ...props }) => <strong className="font-bold text-foreground" {...props} />,
                                em: ({ node, ...props }) => <em className="italic" {...props} />,
                                code: ({ node, ...props }) => <code className="bg-accent px-1.5 py-0.5 rounded text-sm font-mono" {...props} />,
                                pre: ({ node, ...props }) => <pre className="bg-accent p-4 rounded-lg overflow-x-auto mb-4" {...props} />,
                                blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-primary pl-4 italic my-4" {...props} />,
                                a: ({ node, ...props }) => <a className="text-primary hover:underline" {...props} />,
                                table: ({ node, ...props }) => <table className="border-collapse border border-border w-full my-4" {...props} />,
                                th: ({ node, ...props }) => <th className="border border-border px-4 py-2 bg-accent font-semibold text-left" {...props} />,
                                td: ({ node, ...props }) => <td className="border border-border px-4 py-2" {...props} />,
                            }}
                        >
                            {markdownContent}
                        </ReactMarkdown>
                    </div>
                )}
            </div>
        </div>
    );
}
