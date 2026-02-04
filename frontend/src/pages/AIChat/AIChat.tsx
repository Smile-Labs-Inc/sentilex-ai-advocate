// =============================================================================
// AI Chat Page
// Full-screen ChatGPT-like interface with chat history sidebar
// =============================================================================

import { useState, useRef, useEffect } from 'preact/hooks';
import { route } from 'preact-router';
import ReactMarkdown from 'react-markdown';
import { Icon } from '../../components/atoms/Icon/Icon';
import { Button } from '../../components/atoms/Button/Button';
import { authService } from '../../services/auth';
import { cn } from '../../lib/utils';
import { useAuth } from '../../hooks/useAuth';
import { BackgroundGradientAnimation } from '../../components/atoms/BackgroundGradientAnimation/BackgroundGradientAnimation';
import { API_CONFIG, APP_CONFIG } from '../../config';

interface ChatMessage {
    id: number | string | null;
    role: 'user' | 'assistant';
    content: string;
    created_at?: string;
    timestamp?: Date;
    metadata?: Record<string, any>;
}

interface ChatSession {
    id: string;
    title: string;
    last_message?: string;
    lastMessage?: string;
    message_count?: number;
    updated_at?: string;
    created_at?: string;
    timestamp?: Date;
    messages?: ChatMessage[];
}

export interface AIChatPageProps {
    path?: string;
}

const suggestedPrompts = [
    {
        icon: 'Shield' as const,
        title: 'Legal Rights',
        prompt: 'What are my rights in a cybercrime case?'
    },
    {
        icon: 'FileText' as const,
        title: 'Evidence Collection',
        prompt: 'How should I collect and preserve digital evidence?'
    },
    {
        icon: 'Scale' as const,
        title: 'Legal Process',
        prompt: 'What is the process for filing a cybercrime complaint?'
    },
    {
        icon: 'AlertCircle' as const,
        title: 'Urgent Action',
        prompt: 'What should I do immediately after a cyber attack?'
    }
];

export function AIChatPage({ }: AIChatPageProps) {
    const { user } = useAuth();
    const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
    const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const messagesContainerRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    if (!user) {
        return null;
    }

    // Load chat history on mount
    useEffect(() => {
        loadChatHistory();
    }, []);

    const loadChatHistory = async () => {
        try {
            const token = localStorage.getItem(APP_CONFIG.TOKEN_STORAGE_KEY);
            const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CHAT.HISTORY}?limit=50`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.status === 401) {
                // Token expired, try to refresh
                try {
                    const newToken = await authService.refreshToken();
                    // Retry the request with new token
                    const retryResponse = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CHAT.HISTORY}?limit=50`, {
                        headers: {
                            'Authorization': `Bearer ${newToken}`
                        }
                    });
                    if (retryResponse.ok) {
                        const sessions = await retryResponse.json();
                        setChatSessions(sessions.map((s: any) => ({
                            ...s,
                            lastMessage: s.last_message,
                            timestamp: new Date(s.updated_at)
                        })));
                    }
                } catch (refreshError) {
                    console.error('Token refresh failed:', refreshError);
                    window.location.href = '/auth';
                }
                return;
            }

            if (response.ok) {
                const sessions = await response.json();
                setChatSessions(sessions.map((s: any) => ({
                    ...s,
                    lastMessage: s.last_message,
                    timestamp: new Date(s.updated_at)
                })));
            }
        } catch (error) {
            console.error('Failed to load chat history:', error);
        }
    };

    const loadSessionMessages = async (sessionId: string) => {
        try {
            const token = localStorage.getItem(APP_CONFIG.TOKEN_STORAGE_KEY);
            const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CHAT.SESSION(sessionId)}?limit=100`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.status === 401) {
                // Token expired, try to refresh
                try {
                    const newToken = await authService.refreshToken();
                    // Retry the request with new token
                    const retryResponse = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CHAT.SESSION(sessionId)}?limit=100`, {
                        headers: {
                            'Authorization': `Bearer ${newToken}`
                        }
                    });
                    if (retryResponse.ok) {
                        const sessionData = await retryResponse.json();
                        setChatSessions(prev => prev.map(s =>
                            s.id === sessionId
                                ? { ...s, messages: sessionData.messages }
                                : s
                        ));
                    }
                } catch (refreshError) {
                    console.error('Token refresh failed:', refreshError);
                    window.location.href = '/auth';
                }
                return;
            }

            if (response.ok) {
                const sessionData = await response.json();
                setChatSessions(prev => prev.map(s =>
                    s.id === sessionId
                        ? { ...s, messages: sessionData.messages }
                        : s
                ));
            }
        } catch (error) {
            console.error('Failed to load session messages:', error);
        }
    };

    const currentSession = chatSessions.find(s => s.id === currentSessionId);
    const messages = currentSession?.messages || [];

    const scrollToBottom = () => {
        if (messagesEndRef.current && messagesContainerRef.current) {
            messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
        }
    };

    useEffect(() => {
        // Small delay to ensure DOM is updated
        const timer = setTimeout(() => {
            scrollToBottom();
        }, 100);
        return () => clearTimeout(timer);
    }, [messages, isLoading]);

    const createNewChat = () => {
        // Just set null session ID - backend will create new session when message is sent
        setCurrentSessionId(null);
        // Clear messages for new chat
        setChatSessions(prev => {
            const newSession: ChatSession = {
                id: 'temp-' + Date.now(),
                title: 'New Chat',
                lastMessage: '',
                timestamp: new Date(),
                messages: []
            };
            return [newSession, ...prev];
        });
        setCurrentSessionId('temp-' + Date.now());
    };

    const deleteChat = async (sessionId: string, e: Event) => {
        e.stopPropagation();

        if (sessionId.startsWith('temp-')) {
            // Just remove from local state
            setChatSessions(prev => prev.filter(s => s.id !== sessionId));
            if (currentSessionId === sessionId) {
                setCurrentSessionId(null);
            }
            return;
        }

        try {
            const token = sessionStorage.getItem(APP_CONFIG.TOKEN_STORAGE_KEY);
            await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CHAT.DELETE_SESSION(sessionId)}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            setChatSessions(prev => prev.filter(s => s.id !== sessionId));
            if (currentSessionId === sessionId) {
                setCurrentSessionId(null);
            }
        } catch (error) {
            console.error('Failed to delete chat:', error);
        }
    };

    const handleSendMessage = async (message?: string) => {
        const messageText = message || inputValue.trim();
        if (!messageText || isLoading) return;

        // Create new session locally if none exists
        let sessionId = currentSessionId;
        if (!sessionId || sessionId.startsWith('temp-')) {
            sessionId = null;
        }

        setInputValue('');
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }

        setIsLoading(true);

        try {
            const token = localStorage.getItem(APP_CONFIG.TOKEN_STORAGE_KEY);
            const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CHAT.SEND}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    message: messageText,
                    session_id: sessionId,
                    metadata: {}
                })
            });

            if (response.ok) {
                const data = await response.json();

                // Update sessions list
                setChatSessions(prev => {
                    const filtered = prev.filter(s => !s.id.startsWith('temp-'));
                    const existingIndex = filtered.findIndex(s => s.id === data.session.id);

                    const updatedSession: ChatSession = {
                        id: data.session.id,
                        title: data.session.title,
                        lastMessage: data.session.last_message,
                        message_count: data.session.message_count,
                        updated_at: data.session.updated_at,
                        created_at: data.session.created_at,
                        timestamp: new Date(data.session.updated_at),
                        messages: [data.user_message, data.assistant_message]
                    };

                    if (existingIndex >= 0) {
                        filtered[existingIndex] = {
                            ...filtered[existingIndex],
                            ...updatedSession,
                            messages: [...(filtered[existingIndex].messages || []), data.user_message, data.assistant_message]
                        };
                        return filtered;
                    } else {
                        return [updatedSession, ...filtered];
                    }
                });

                setCurrentSessionId(data.session.id);
            } else {
                throw new Error('Failed to send message');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            alert('Failed to send message. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    const handleSuggestedPrompt = (prompt: string) => {
        handleSendMessage(prompt);
    };

    const handleTextareaInput = (e: Event) => {
        const target = e.target as HTMLTextAreaElement;
        setInputValue(target.value);
        target.style.height = 'auto';
        target.style.height = `${Math.min(target.scrollHeight, 200)}px`;
    };

    return (
        <BackgroundGradientAnimation
            containerClassName="h-screen w-screen overflow-hidden"
            className="h-full w-full flex"
            gradientBackgroundStart="rgb(0, 0, 0)"
            gradientBackgroundEnd="rgb(0, 0, 0)"
            firstColor="4, 23, 51"
            secondColor="51, 13, 13"
            thirdColor="51, 32, 24"
            fourthColor="44, 15, 51"
            fifthColor="20, 44, 51"
            pointerColor="28, 20, 51"
            interactive={false}
        >
            <div className="flex h-screen w-screen relative z-10">

                {/* Left Sidebar - Chat History */}
                <div className={cn(
                    "flex flex-col h-full bg-black/30 backdrop-blur-xl border-r border-white/10 transition-all duration-300",
                    sidebarOpen ? "w-80" : "w-0"
                )}>
                    {sidebarOpen && (
                        <div className="flex flex-col h-full p-4">
                            {/* Sidebar Header */}
                            <div className="flex items-center justify-between mb-6">
                                <div className="flex items-center gap-2 text-foreground font-bold text-lg tracking-wider">
                                    <Icon name="Scale" size="md" />
                                    <span className="font-['Space_Grotesk']">VERITAS</span>
                                </div>
                                <button
                                    onClick={() => setSidebarOpen(false)}
                                    className="p-1.5 hover:bg-white/10 rounded-lg transition-colors"
                                >
                                    <Icon name="PanelLeftClose" size="sm" className="text-muted-foreground" />
                                </button>
                            </div>

                            {/* New Chat Button */}
                            <Button
                                onClick={createNewChat}
                                variant="primary"
                                className="w-full mb-4 gap-2"
                            >
                                <Icon name="Plus" size="sm" />
                                New Chat
                            </Button>

                            {/* Chat Sessions List */}
                            <div className="flex-1 overflow-y-auto space-y-2 scrollbar-thin">
                                {chatSessions.length === 0 ? (
                                    <div className="text-center text-muted-foreground text-sm py-8">
                                        No chat history yet.<br />Start a new conversation!
                                    </div>
                                ) : (
                                    chatSessions.map((session) => (
                                        <button
                                            key={session.id}
                                            onClick={() => {
                                                setCurrentSessionId(session.id);
                                                if (!session.messages && !session.id.startsWith('temp-')) {
                                                    loadSessionMessages(session.id);
                                                }
                                            }}
                                            className={cn(
                                                "w-full text-left p-3 rounded-lg transition-all group",
                                                "hover:bg-white/10",
                                                currentSessionId === session.id
                                                    ? "bg-white/20 border border-white/10"
                                                    : "border border-transparent"
                                            )}
                                        >
                                            <div className="flex items-start justify-between gap-2">
                                                <div className="flex-1 min-w-0">
                                                    <h3 className="text-sm font-medium text-foreground truncate">
                                                        {session.title}
                                                    </h3>
                                                    <p className="text-xs text-muted-foreground truncate mt-1">
                                                        {session.lastMessage || session.last_message || 'No messages yet'}
                                                    </p>
                                                    <p className="text-xs text-muted-foreground mt-1">
                                                        {session.timestamp ? session.timestamp.toLocaleDateString() : new Date(session.updated_at || session.created_at || Date.now()).toLocaleDateString()}
                                                    </p>
                                                </div>
                                                <button
                                                    onClick={(e) => deleteChat(session.id, e as any)}
                                                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/20 rounded transition-all"
                                                >
                                                    <Icon name="Trash2" size="sm" className="text-red-400" />
                                                </button>
                                            </div>
                                        </button>
                                    ))
                                )}
                            </div>

                            {/* Sidebar Footer */}
                            <div className="border-t border-white/10 pt-4 mt-4">
                                <button
                                    onClick={() => route('/dashboard')}
                                    className="w-full flex items-center gap-2 p-2 hover:bg-white/10 rounded-lg transition-colors text-muted-foreground hover:text-foreground"
                                >
                                    <Icon name="ArrowLeft" size="sm" />
                                    <span className="text-sm">Back to Dashboard</span>
                                </button>
                            </div>
                        </div>
                    )}
                </div>

                {/* Main Chat Area */}
                <div className="flex-1 flex flex-col h-full">

                    {/* Top Header */}
                    <div className="flex items-center justify-between px-6 py-4 bg-black/20 backdrop-blur-md border-b border-white/10">
                        <div className="flex items-center gap-3">
                            {!sidebarOpen && (
                                <button
                                    onClick={() => setSidebarOpen(true)}
                                    className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                                >
                                    <Icon name="PanelLeft" size="sm" className="text-muted-foreground" />
                                </button>
                            )}
                            <div className="flex items-center gap-2">
                                <Icon name="Scale" size="md" className="text-foreground" />
                                <div>
                                    <h1 className="text-lg font-bold text-foreground font-['Space_Grotesk']">
                                        AI Legal Assistant
                                    </h1>
                                    <div className="flex items-center gap-1.5">
                                        <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                                        <span className="text-xs text-muted-foreground">Online</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="text-sm text-muted-foreground">
                                {user.first_name} {user.last_name}
                            </div>
                            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-primary-foreground font-semibold text-xs">
                                {user.first_name[0]}{user.last_name[0]}
                            </div>
                        </div>
                    </div>

                    {/* Messages Area - Fixed Height with Scroll */}
                    <div
                        ref={messagesContainerRef}
                        className="flex-1 overflow-y-auto px-6 py-6"
                        style={{ height: 'calc(100vh - 180px)' }}
                    >
                        {messages.length === 0 ? (
                            <div className="h-full flex flex-col items-center justify-center text-center max-w-3xl mx-auto">
                                <div className="mb-6">
                                    <Icon name="Scale" size="lg" className="text-foreground" />
                                </div>
                                <h2 className="text-2xl font-semibold text-foreground mb-2">
                                    How can I assist you today?
                                </h2>
                                <p className="text-muted-foreground mb-8">
                                    I'm your AI legal assistant specialized in Sri Lankan cyber law. Ask me anything about your case, legal rights, or next steps.
                                </p>

                                {/* Suggested Prompts */}
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full">
                                    {suggestedPrompts.map((suggestion, index) => (
                                        <button
                                            key={index}
                                            onClick={() => handleSuggestedPrompt(suggestion.prompt)}
                                            className={cn(
                                                "flex items-start gap-3 p-4 rounded-xl text-left",
                                                "bg-white/5 border border-white/10",
                                                "hover:bg-white/10 hover:border-white/20",
                                                "transition-all duration-200 group"
                                            )}
                                        >
                                            <div className="w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0 group-hover:bg-white/20 transition-colors">
                                                <Icon name={suggestion.icon} size="sm" className="text-muted-foreground group-hover:text-foreground transition-colors" />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <h3 className="text-sm font-medium text-foreground mb-1">
                                                    {suggestion.title}
                                                </h3>
                                                <p className="text-xs text-muted-foreground">
                                                    {suggestion.prompt}
                                                </p>
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        ) : (
                            <div className="max-w-4xl mx-auto space-y-6">
                                {messages.map((message) => (
                                    <div
                                        key={message.id}
                                        className={cn(
                                            'flex gap-4',
                                            message.role === 'user' ? 'justify-end' : 'justify-start'
                                        )}
                                    >
                                        {message.role === 'assistant' && (
                                            <div className="flex items-center justify-center flex-shrink-0">
                                                <Icon name="Scale" size="md" className="text-foreground" />
                                            </div>
                                        )}

                                        <div
                                            className={cn(
                                                'flex flex-col gap-1 max-w-[75%]',
                                                message.role === 'user' && 'items-end'
                                            )}
                                        >
                                            <div
                                                className={cn(
                                                    'rounded-xl px-3 py-2',
                                                    message.role === 'user'
                                                        ? 'bg-primary text-primary-foreground'
                                                        : 'bg-white/10 border border-white/10'
                                                )}
                                            >
                                                <div className={cn(
                                                    'text-xs leading-relaxed prose prose-xs max-w-none',
                                                    message.role === 'user'
                                                        ? 'text-primary-foreground prose-invert'
                                                        : 'text-foreground prose-invert'
                                                )}>
                                                    {message.role === 'assistant' ? (
                                                        <ReactMarkdown>{message.content}</ReactMarkdown>
                                                    ) : (
                                                        <p className="whitespace-pre-wrap m-0">{message.content}</p>
                                                    )}
                                                </div>
                                            </div>
                                            <span className="text-[10px] text-muted-foreground px-2">
                                                {(message.timestamp || new Date(message.created_at || Date.now())).toLocaleTimeString([], {
                                                    hour: '2-digit',
                                                    minute: '2-digit'
                                                })}
                                            </span>
                                        </div>

                                        {message.role === 'user' && (
                                            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center flex-shrink-0 text-primary-foreground font-semibold text-xs">
                                                {user.first_name[0]}{user.last_name[0]}
                                            </div>
                                        )}
                                    </div>
                                ))}

                                {isLoading && (
                                    <div className="flex gap-4">
                                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-yellow-500 to-orange-500 flex items-center justify-center flex-shrink-0">
                                            <Icon name="Sparkles" size="sm" className="text-white" />
                                        </div>
                                        <div className="flex items-center gap-2 px-4 py-3 rounded-2xl bg-white/10 border border-white/10">
                                            <div className="flex gap-1">
                                                <div className="w-2 h-2 rounded-full bg-foreground animate-bounce" style={{ animationDelay: '0ms' }} />
                                                <div className="w-2 h-2 rounded-full bg-foreground animate-bounce" style={{ animationDelay: '150ms' }} />
                                                <div className="w-2 h-2 rounded-full bg-foreground animate-bounce" style={{ animationDelay: '300ms' }} />
                                            </div>
                                        </div>
                                    </div>
                                )}

                                <div ref={messagesEndRef} />
                            </div>
                        )}
                    </div>

                    {/* Input Area - Fixed at Bottom */}
                    <div className="px-4 py-2 bg-black/20 backdrop-blur-md border-t border-white/10">
                        <div className="max-w-4xl mx-auto">
                            <div className="flex gap-2 items-center">
                                <div className="flex-1 relative">
                                    <textarea
                                        ref={textareaRef}
                                        value={inputValue}
                                        onInput={handleTextareaInput}
                                        onKeyDown={handleKeyDown}
                                        placeholder="Ask me anything about your legal case..."
                                        disabled={isLoading}
                                        rows={1}
                                        className={cn(
                                            'w-full px-3 py-2',
                                            'bg-white/10 border border-white/10 rounded-lg',
                                            'text-xs text-foreground placeholder:text-muted-foreground',
                                            'focus:outline-none focus:ring-2 focus:ring-primary/50',
                                            'resize-none overflow-hidden',
                                            'disabled:opacity-50 disabled:cursor-not-allowed'
                                        )}
                                        style={{
                                            minHeight: '36px',
                                            maxHeight: '150px'
                                        }}
                                    />
                                </div>
                                <Button
                                    onClick={() => handleSendMessage()}
                                    disabled={!inputValue.trim() || isLoading}
                                    size="sm"
                                    className="gap-1.5 px-4 flex-shrink-0 h-9"
                                >
                                    {isLoading ? (
                                        <>
                                            <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                            <span className="text-xs">Sending</span>
                                        </>
                                    ) : (
                                        <>
                                            <Icon name="Send" size="sm" />
                                            <span className="text-xs">Send</span>
                                        </>
                                    )}
                                </Button>
                            </div>
                            <p className="text-[10px] text-muted-foreground text-center mt-1.5">
                                Press <kbd className="px-1.5 py-0.5 rounded bg-white/10 text-foreground text-xs">Enter</kbd> to send, <kbd className="px-1.5 py-0.5 rounded bg-white/10 text-foreground text-xs">Shift + Enter</kbd> for new line
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </BackgroundGradientAnimation>
    );
}

export default AIChatPage;
