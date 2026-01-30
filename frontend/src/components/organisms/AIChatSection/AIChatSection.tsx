// =============================================================================
// AIChatSection Organism
// AI assistant chat interface for case analysis
// =============================================================================

import { useState } from 'preact/hooks';
import ReactMarkdown from 'react-markdown';
import { cn } from '../../../lib/utils';
import { Card, CardHeader, CardTitle } from '../../atoms/Card/Card';
import { Button } from '../../atoms/Button/Button';
import { Icon } from '../../atoms/Icon/Icon';

export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

export interface AIChatSectionProps {
    messages: ChatMessage[];
    onSendMessage: (message: string) => void;
    isLoading?: boolean;
    className?: string;
}

export function AIChatSection({
    messages,
    onSendMessage,
    isLoading = false,
    className,
}: AIChatSectionProps) {
    const [inputValue, setInputValue] = useState('');

    const handleSend = () => {
        if (inputValue.trim() && !isLoading) {
            onSendMessage(inputValue.trim());
            setInputValue('');
        }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <Card variant="default" padding="none" className={cn('flex flex-col h-[500px] animate-slide-up', className)}>
            <CardHeader className="px-6 py-4 border-b border-border">
                <div className="flex items-center gap-2">
                    <Icon name="Sparkles" size="sm" className="text-yellow-500" />
                    <CardTitle className="text-sm">AI Legal Assistant</CardTitle>
                </div>
                <div className="flex items-center gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-xs text-muted-foreground">Online</span>
                </div>
            </CardHeader>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center">
                        <Icon name="Sparkles" size="lg" className="text-muted-foreground mb-3" />
                        <p className="text-sm text-muted-foreground mb-1">
                            Your AI Legal Assistant
                        </p>
                        <p className="text-xs text-muted-foreground max-w-xs">
                            Ask questions about your case, applicable laws, or next steps
                        </p>
                    </div>
                ) : (
                    messages.map((message) => (
                        <div
                            key={message.id}
                            className={cn(
                                'flex gap-3',
                                message.role === 'user' && 'flex-row-reverse'
                            )}
                        >
                            {/* Avatar */}
                            <div className={cn(
                                'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
                                message.role === 'assistant'
                                    ? 'bg-yellow-500/20'
                                    : 'bg-secondary'
                            )}>
                                <Icon
                                    name={message.role === 'assistant' ? 'Sparkles' : 'User'}
                                    size="sm"
                                    className={message.role === 'assistant' ? 'text-yellow-500' : 'text-muted-foreground'}
                                />
                            </div>

                            {/* Message bubble */}
                            <div className={cn(
                                'max-w-[80%] rounded-xl px-4 py-2.5',
                                message.role === 'assistant'
                                    ? 'bg-secondary text-foreground'
                                    : 'bg-primary text-primary-foreground'
                            )}>
                                {message.role === 'assistant' ? (
                                    <div className="prose prose-sm prose-zinc dark:prose-invert max-w-none">
                                        <ReactMarkdown
                                            components={{
                                                h1: ({ node, ...props }) => <h1 className="text-lg font-bold text-foreground mt-2 mb-1" {...props} />,
                                                h2: ({ node, ...props }) => <h2 className="text-base font-bold text-foreground mt-2 mb-1" {...props} />,
                                                h3: ({ node, ...props }) => <h3 className="text-sm font-semibold text-foreground mt-1 mb-1" {...props} />,
                                                p: ({ node, ...props }) => <p className="text-sm text-foreground mb-2 leading-relaxed" {...props} />,
                                                ul: ({ node, ...props }) => <ul className="list-disc ml-4 mb-2 text-sm" {...props} />,
                                                ol: ({ node, ...props }) => <ol className="list-decimal ml-4 mb-2 text-sm" {...props} />,
                                                li: ({ node, ...props }) => <li className="mb-0.5" {...props} />,
                                                strong: ({ node, ...props }) => <strong className="font-bold" {...props} />,
                                                code: ({ node, ...props }) => <code className="bg-accent px-1 py-0.5 rounded text-xs font-mono" {...props} />,
                                                blockquote: ({ node, ...props }) => <blockquote className="border-l-2 border-primary pl-2 italic my-2" {...props} />,
                                                hr: ({ node, ...props }) => <hr className="my-2 border-border" {...props} />,
                                            }}
                                        >
                                            {message.content}
                                        </ReactMarkdown>
                                    </div>
                                ) : (
                                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                                )}
                            </div>
                        </div>
                    ))
                )}

                {isLoading && (
                    <div className="flex gap-3">
                        <div className="w-8 h-8 rounded-full bg-yellow-500/20 flex items-center justify-center">
                            <Icon name="Sparkles" size="sm" className="text-yellow-500" />
                        </div>
                        <div className="bg-secondary/50 rounded-xl px-4 py-3">
                            <div className="flex gap-1">
                                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-border">
                <div className="flex gap-2">
                    <input
                        type="text"
                        placeholder="Ask about your case..."
                        value={inputValue}
                        onInput={(e) => setInputValue((e.target as HTMLInputElement).value)}
                        onKeyDown={handleKeyDown}
                        className={cn(
                            'flex-1 bg-secondary text-foreground rounded-lg px-4 py-2.5 text-sm',
                            'border border-border',
                            'focus:outline-none focus:border-ring',
                            'placeholder:text-muted-foreground'
                        )}
                    />
                    <Button
                        onClick={handleSend}
                        disabled={!inputValue.trim() || isLoading}
                        size="icon"
                    >
                        <Icon name="Send" size="sm" />
                    </Button>
                </div>
                <p className="text-[10px] text-muted-foreground mt-2 text-center">
                    AI responses are for guidance only. Consult a licensed attorney for legal advice.
                </p>
            </div>
        </Card>
    );
}

export default AIChatSection;
