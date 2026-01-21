import { AIChatSection, type ChatMessage } from '../AIChatSection/AIChatSection';

export interface LawbookChatProps {
    messages: ChatMessage[];
    onSendMessage: (text: string) => void;
    isLoading?: boolean;
    className?: string;
}

export function LawbookChat({ messages, onSendMessage, isLoading, className }: LawbookChatProps) {
    // We reuse AIChatSection but wrapper allows us to inject Lawbook specific context/styles if needed later
    return (
        <AIChatSection
            messages={messages}
            onSendMessage={onSendMessage}
            isLoading={isLoading}
            className={className}
        />
    );
}
