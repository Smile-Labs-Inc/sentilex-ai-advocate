// =============================================================================
// IncidentDetail Page
// Detailed view of a specific incident with AI chat, laws, timeline
// =============================================================================

import { useState } from 'preact/hooks';
import { DashboardLayout } from '../../components/templates/DashboardLayout/DashboardLayout';
import { IncidentHeader } from '../../components/organisms/IncidentHeader/IncidentHeader';
import { AIChatSection, type ChatMessage } from '../../components/organisms/AIChatSection/AIChatSection';
import { LawsSection, type IdentifiedLaw } from '../../components/organisms/LawsSection/LawsSection';
import { TimelineSection, type TimelineEvent } from '../../components/organisms/TimelineSection/TimelineSection';
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

// Mock data for demo
const mockLaws: IdentifiedLaw[] = [
    {
        id: '1',
        name: 'Computer Crimes Act No. 24 of 2007',
        section: 'Section 6',
        description: 'Illegal interception of data - Whoever intentionally and without lawful authority intercepts by technical means, any non-public transmission of computer data.',
        relevance: 'high',
        jurisdiction: 'Sri Lanka',
    },
    {
        id: '2',
        name: 'Penal Code of Sri Lanka',
        section: 'Section 345',
        description: 'Criminal intimidation - Threatening another with injury to person, reputation, or property with intent to cause alarm.',
        relevance: 'high',
        jurisdiction: 'Sri Lanka',
    },
    {
        id: '3',
        name: 'Prevention of Domestic Violence Act No. 34 of 2005',
        section: 'Section 2',
        description: 'Definition of domestic violence includes emotional abuse, harassment, and intimidation through any means including electronic communication.',
        relevance: 'medium',
        jurisdiction: 'Sri Lanka',
    },
];

const mockTimeline: TimelineEvent[] = [
    {
        id: '1',
        type: 'created',
        title: 'Case Created',
        description: 'You created this incident report',
        timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
    },
    {
        id: '2',
        type: 'ai-analysis',
        title: 'AI Analysis Complete',
        description: '3 applicable laws identified',
        timestamp: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000),
    },
    {
        id: '3',
        type: 'law-identified',
        title: 'New Law Added',
        description: 'IT Act Section 66A added to case',
        timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
    },
    {
        id: '4',
        type: 'evidence-added',
        title: 'Evidence Uploaded',
        description: '3 screenshots added',
        timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    },
    {
        id: '5',
        type: 'status-change',
        title: 'Status Updated',
        description: 'Case marked as In Progress',
        timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    },
];

const initialMessages: ChatMessage[] = [
    {
        id: '1',
        role: 'assistant',
        content: "Hello! I've analyzed your case and identified 3 applicable laws. Based on the nature of the cyberbullying incident, I recommend documenting all evidence with timestamps. Would you like me to explain the legal remedies available to you?",
        timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    },
];

export function IncidentDetailPage({
    user,
    incident,
    onNavigate,
    onBack,
}: IncidentDetailPageProps) {
    const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
    const [isAILoading, setIsAILoading] = useState(false);

    const handleSendMessage = (content: string) => {
        // Add user message
        const userMessage: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            content,
            timestamp: new Date(),
        };
        setMessages((prev) => [...prev, userMessage]);

        // Simulate AI response
        setIsAILoading(true);
        setTimeout(() => {
            const aiResponses: Record<string, string> = {
                default: "I understand your concern. Based on the evidence you've provided, the strongest case can be made under Section 6 of the Computer Crimes Act No. 24 of 2007. This provision specifically addresses illegal interception and unauthorized access. Would you like me to help you prepare a formal complaint?",
                legal: "In Sri Lanka, you can report cyber crimes to the Computer Crimes Division of the CID. I can help you draft the complaint, gather necessary evidence, and identify the right authorities to approach. Shall I outline the step-by-step process?",
                evidence: "For building a strong case, I recommend collecting: 1) Screenshots with timestamps, 2) URLs of offensive content, 3) Any direct messages or communications, 4) Witness statements if available. Would you like guidance on preserving digital evidence?",
            };

            const keywords = content.toLowerCase();
            let response = aiResponses.default;
            if (keywords.includes('legal') || keywords.includes('process') || keywords.includes('police')) {
                response = aiResponses.legal;
            } else if (keywords.includes('evidence') || keywords.includes('screenshot') || keywords.includes('proof')) {
                response = aiResponses.evidence;
            }

            const aiMessage: ChatMessage = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: response,
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, aiMessage]);
            setIsAILoading(false);
        }, 1500);
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
                        <LawsSection laws={mockLaws} />

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
                    <TimelineSection events={mockTimeline} />
                </div>
            </div>
        </DashboardLayout>
    );
}

export default IncidentDetailPage;
