// =============================================================================
// IncidentDetail Page
// Detailed view of a specific incident with AI chat, laws, timeline
// =============================================================================

import { useState, useEffect } from 'preact/hooks';
import { DashboardLayout } from '../../components/templates/DashboardLayout/DashboardLayout';
import { IncidentHeader } from '../../components/organisms/IncidentHeader/IncidentHeader';
import { AIChatSection, type ChatMessage } from '../../components/organisms/AIChatSection/AIChatSection';
import { LawsSection } from '../../components/organisms/LawsSection/LawsSection';
import { TimelineSection } from '../../components/organisms/TimelineSection/TimelineSection';
import { Card, CardHeader, CardTitle } from '../../components/atoms/Card/Card';
import { Icon } from '../../components/atoms/Icon/Icon';
import type { NavItem, Incident } from '../../types';
import type { UserProfile } from '../../types/auth';

export interface IncidentDetailPageProps {
    user: UserProfile;
    incident: Incident;
    onNavigate: (item: NavItem) => void;
    onBack: () => void;
}


export function IncidentDetailPage({
    user,
    incident,
    onNavigate,
    onBack,
}: IncidentDetailPageProps) {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isAILoading, setIsAILoading] = useState(false);
    const [isLoadingHistory, setIsLoadingHistory] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Extract numeric ID from incident.id (format: "inc_123")
    const numericIncidentId = parseInt(incident.id.replace('inc_', ''), 10);

    // Load chat history on mount
    useEffect(() => {
        const loadChatHistory = async () => {
            try {
                setIsLoadingHistory(true);
                const { getIncidentChatMessages } = await import('../../services/incident');
                const chatMessages = await getIncidentChatMessages(numericIncidentId);

                // Convert API messages to ChatMessage format
                const formattedMessages: ChatMessage[] = chatMessages.map(msg => ({
                    id: msg.id.toString(),
                    role: msg.role as 'user' | 'assistant',
                    content: msg.content,
                    timestamp: new Date(msg.created_at),
                }));

                setMessages(formattedMessages);
            } catch (err) {
                setError('Failed to load chat history');
            } finally {
                setIsLoadingHistory(false);
            }
        };

        loadChatHistory();
    }, [incident.id]);

    const handleSendMessage = async (content: string) => {
        // Add user message optimistically
        const userMessage: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            content,
            timestamp: new Date(),
        };
        setMessages((prev) => [...prev, userMessage]);
        setError(null);

        // Call real API
        setIsAILoading(true);
        try {
            const { sendIncidentChatMessage } = await import('../../services/incident');
            const response = await sendIncidentChatMessage(numericIncidentId, content);

            // Add AI response
            const aiMessage: ChatMessage = {
                id: response.assistant_message.id.toString(),
                role: 'assistant',
                content: response.assistant_message.content,
                timestamp: new Date(response.assistant_message.created_at),
            };

            // Update user message with actual ID from server
            setMessages((prev) => {
                const updated = [...prev];
                const userMsgIndex = updated.findIndex(m => m.id === userMessage.id);
                if (userMsgIndex !== -1) {
                    updated[userMsgIndex] = {
                        ...updated[userMsgIndex],
                        id: response.user_message.id.toString(),
                    };
                }
                return [...updated, aiMessage];
            });
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to send message');

            // Remove optimistic user message on error
            setMessages((prev) => prev.filter(m => m.id !== userMessage.id));
        } finally {
            setIsAILoading(false);
        }
    };

    return (
        <DashboardLayout
            user={user}
            currentPath="/incidents"
            onNavigate={onNavigate}
        >
            <div className="py-6">
                {/* Header */}
                <IncidentHeader incident={incident} onBack={onBack} />

                {/* Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left column - AI Chat */}
                    <div className="lg:col-span-2">
                        <AIChatSection
                            messages={messages}
                            onSendMessage={handleSendMessage}
                            isLoading={isAILoading}
                        />
                    </div>

                    {/* Right column - Laws & Timeline */}
                    <div className="space-y-6">
                        <LawsSection laws={[]} />

                        {/* Case Summary */}
                        <Card variant="default" padding="lg" className="animate-slide-up">
                            <CardHeader>
                                <div className="flex items-center gap-2">
                                    <Icon name="FileText" size="sm" className="text-muted-foreground" />
                                    <CardTitle className="text-sm">Case Summary</CardTitle>
                                </div>
                            </CardHeader>
                            <div className="text-sm text-muted-foreground space-y-3">
                                <p>
                                    {incident.description || 'This case involves reported cyberbullying incidents across multiple platforms. Evidence has been collected and applicable laws have been identified.'}
                                </p>
                                <div className="grid grid-cols-2 gap-3 text-xs">
                                    <div>
                                        <span className="text-muted-foreground/80">Evidence Items</span>
                                        <div className="text-foreground font-medium">5 files</div>
                                    </div>
                                    <div>
                                        <span className="text-muted-foreground/80">Last Update</span>
                                        <div className="text-foreground font-medium">2 hours ago</div>
                                    </div>
                                </div>
                            </div>
                        </Card>
                    </div>
                </div>

                {/* Timeline - Full width */}
                <div className="mt-6">
                    <TimelineSection events={[]} />
                </div>
            </div>
        </DashboardLayout>
    );
}

export default IncidentDetailPage;
