import { useState, useEffect } from 'preact/hooks';
import { DashboardLayout } from '../../components/templates/DashboardLayout/DashboardLayout';
import { LawbookViewer } from '../../components/organisms/LawbookViewer/LawbookViewer';
import { LawbookChat } from '../../components/organisms/LawbookChat/LawbookChat';
import { useAuth } from '../../hooks/useAuth';
import type { NavItem, Bookmark, ChatMessage } from '../../types';
import { formatLegalResponse } from '../../lib/formatters';
import { fetchLaws, fetchLawContent, submitQuery, type Law } from '../../services/lawbook.tsx';

export interface LawbookPageProps {
    onNavigate?: (item: NavItem) => void;
}

export function LawbookPage({ onNavigate }: LawbookPageProps) {
    const { user } = useAuth();
    const [laws, setLaws] = useState<Law[]>([]);
    const [activeLawId, setActiveLawId] = useState<string | null>(null);
    const [lawContent, setLawContent] = useState<string>('');
    const [isLoading, setIsLoading] = useState(true);
    const [isContentLoading, setIsContentLoading] = useState(false);
    const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
    const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
        {
            id: 'msg_welcome',
            role: 'assistant',
            content: 'Hello! I know every page of the Lawbook. Don\'t scroll just tell me what you\'re looking for, and I\'ll take you there.',
            timestamp: new Date()
        }
    ]);
    const [isChatLoading, setIsChatLoading] = useState(false);

    if (!user) {
        return null;
    }

    // Fetch list of laws on mount
    useEffect(() => {
        const loadLaws = async () => {
            try {
                setIsLoading(true);
                const lawsData = await fetchLaws();
                setLaws(lawsData);

                // Set first law as active by default
                if (lawsData.length > 0) {
                    setActiveLawId(lawsData[0].id);
                }
            } catch (error) {
                // Error fetching laws
            } finally {
                setIsLoading(false);
            }
        };

        loadLaws();
    }, []);

    // Fetch content when active law changes
    useEffect(() => {
        if (!activeLawId) return;

        const loadLawContent = async () => {
            try {
                setIsContentLoading(true);
                const content = await fetchLawContent(activeLawId);
                setLawContent(content);
            } catch (error) {
                setLawContent('Error loading content. Please try again.');
            } finally {
                setIsContentLoading(false);
            }
        };

        loadLawContent();
    }, [activeLawId]);

    const handleToggleBookmark = (lawId: string, sectionId: string, title: string) => {
        setBookmarks(prev => {
            const exists = prev.find(b => b.chapterId === lawId && b.sectionId === sectionId);
            if (exists) {
                return prev.filter(b => b.id !== exists.id);
            } else {
                return [...prev, {
                    id: `bm_${Math.random().toString(36).substr(2, 9)}`,
                    chapterId: lawId,
                    sectionId,
                    title,
                    createdAt: new Date()
                }];
            }
        });
    };

    const handleChatSend = async (text: string) => {
        // Add user message
        const userMsg: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: text,
            timestamp: new Date()
        };
        setChatMessages(prev => [...prev, userMsg]);
        setIsChatLoading(true);

        try {
            const response = await submitQuery({ question: text });

            if (response.status === 'success' && response.data) {
                const formattedContent = formatLegalResponse(response.data);

                const aiMsg: ChatMessage = {
                    id: (Date.now() + 1).toString(),
                    role: 'assistant',
                    content: formattedContent,
                    timestamp: new Date()
                };
                setChatMessages(prev => [...prev, aiMsg]);
            } else {
                throw new Error('Query refused or failed');
            }
        } catch (error) {
            const errorMsg: ChatMessage = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: "I'm sorry, I encountered an error while connecting to the legal assistant.",
                timestamp: new Date()
            };
            setChatMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsChatLoading(false);
        }
    };

    return (
        <DashboardLayout
            user={user}
            currentPath="/lawbook"
            onNavigate={onNavigate}
        >
            <div className="flex h-[calc(100vh-8rem)] gap-6">

                {/* Left Panel: Table of Contents (25%) */}
                <div className="w-1/4 hidden lg:flex flex-col gap-4">
                    <div className="bg-card/40 border border-border rounded-xl p-4 backdrop-blur-sm h-full flex flex-col">
                        <h2 className="text-sm font-bold text-muted-foreground uppercase tracking-widest mb-4 px-2">
                            Table of Contents
                        </h2>
                        <div className="space-y-1 flex-1 overflow-y-auto pr-2 custom-scrollbar">
                            {isLoading ? (
                                <div className="text-center text-muted-foreground py-4">Loading laws...</div>
                            ) : (
                                laws.map(law => (
                                    <button
                                        key={law.id}
                                        onClick={() => setActiveLawId(law.id)}
                                        className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${law.id === activeLawId
                                            ? 'bg-primary/20 text-primary font-semibold'
                                            : 'text-muted-foreground hover:bg-accent hover:text-foreground'
                                            }`}
                                    >
                                        {law.title}
                                    </button>
                                ))
                            )}
                        </div>

                        {/* Bookmarks Section */}
                        {bookmarks.length > 0 && (
                            <div className="mt-6 pt-4 border-t border-border">
                                <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-3 px-2">
                                    Bookmarks
                                </h2>
                                <div className="space-y-2">
                                    {bookmarks.map(bm => (
                                        <button
                                            key={bm.id}
                                            onClick={() => {
                                                setActiveLawId(bm.chapterId);
                                                // Ideally scroll to section
                                            }}
                                            className="w-full text-left px-3 py-2 rounded-lg text-xs bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20 transition-colors truncate"
                                        >
                                            {bm.title}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Center: Content Viewer (50%) */}
                <div className="flex-1 lg:w-2/4 bg-card border border-border rounded-xl shadow-lg relative overflow-hidden flex flex-col">
                    <LawbookViewer
                        lawId={activeLawId || ''}
                        lawTitle={laws.find(l => l.id === activeLawId)?.title || ''}
                        markdownContent={lawContent}
                        isLoading={isContentLoading}
                        bookmarks={bookmarks}
                        onToggleBookmark={handleToggleBookmark}
                    />
                </div>

                {/* Right Panel: AI Chat (25%) */}
                <div className="w-1/4 hidden xl:block">
                    <div className="h-full bg-card/40 border border-border rounded-xl backdrop-blur-sm overflow-hidden flex flex-col">
                        <div className="p-3 border-b border-white/5 bg-white/5">
                            <h3 className="font-semibold text-sm text-center">Legal Assistant</h3>
                        </div>
                        <LawbookChat
                            messages={chatMessages}
                            onSendMessage={handleChatSend}
                            isLoading={isChatLoading}
                            className="flex-1 border-0 shadow-none bg-transparent"
                        />
                    </div>
                </div>

                {/* Mobile/Tablet Fallbacks/Adjustments could go here */}
            </div>
        </DashboardLayout>
    );
}
