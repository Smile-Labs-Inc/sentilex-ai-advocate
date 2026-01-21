// =============================================================================
// EditableTimeline Organism
// Editable crime timeline with add/edit/delete capabilities
// =============================================================================

import { useState } from 'preact/hooks';
import { cn } from '../../../lib/utils';
import { Card, CardHeader, CardTitle } from '../../atoms/Card/Card';
import { Button } from '../../atoms/Button/Button';
import { Icon, type IconName } from '../../atoms/Icon/Icon';
import { Input } from '../../atoms/Input/Input';
import { Textarea } from '../../atoms/Textarea/Textarea';
import type { TimelineEventEditable } from '../../../types';

export interface EditableTimelineProps {
    events: TimelineEventEditable[];
    onAddEvent: (event: Omit<TimelineEventEditable, 'id'>) => void;
    onUpdateEvent: (event: TimelineEventEditable) => void;
    onDeleteEvent: (eventId: string) => void;
    onAcceptSuggestion?: (eventId: string) => void;
    className?: string;
}

const eventTypeConfig: Record<TimelineEventEditable['type'], { icon: IconName; color: string; label: string }> = {
    'incident': { icon: 'AlertTriangle', color: 'text-red-400 bg-red-500/10', label: 'Incident' },
    'evidence': { icon: 'FileCheck', color: 'text-blue-400 bg-blue-500/10', label: 'Evidence' },
    'communication': { icon: 'MessageCircle', color: 'text-purple-400 bg-purple-500/10', label: 'Communication' },
    'threat': { icon: 'AlertOctagon', color: 'text-orange-400 bg-orange-500/10', label: 'Threat' },
    'report': { icon: 'Flag', color: 'text-green-400 bg-green-500/10', label: 'Report' },
    'ai-suggestion': { icon: 'Sparkles', color: 'text-yellow-400 bg-yellow-500/10', label: 'AI Suggestion' },
    'custom': { icon: 'Circle', color: 'text-muted-foreground bg-muted/10', label: 'Event' },
};

const formatDate = (date: Date): string => {
    return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    }).format(date);
};

interface EditingState {
    eventId: string | null;
    title: string;
    description: string;
    timestamp: string;
    type: TimelineEventEditable['type'];
}

export function EditableTimeline({
    events,
    onAddEvent,
    onUpdateEvent,
    onDeleteEvent,
    onAcceptSuggestion,
    className,
}: EditableTimelineProps) {
    const [isAdding, setIsAdding] = useState(false);
    const [editing, setEditing] = useState<EditingState | null>(null);
    const [newEvent, setNewEvent] = useState({
        title: '',
        description: '',
        timestamp: new Date().toISOString().slice(0, 16),
        type: 'incident' as TimelineEventEditable['type'],
    });

    const handleStartEdit = (event: TimelineEventEditable) => {
        setEditing({
            eventId: event.id,
            title: event.title,
            description: event.description,
            timestamp: event.timestamp.toISOString().slice(0, 16),
            type: event.type,
        });
    };

    const handleSaveEdit = () => {
        if (!editing) return;

        const event = events.find(e => e.id === editing.eventId);
        if (!event) return;

        onUpdateEvent({
            ...event,
            title: editing.title,
            description: editing.description,
            timestamp: new Date(editing.timestamp),
            type: editing.type,
        });
        setEditing(null);
    };

    const handleAddEvent = () => {
        if (!newEvent.title.trim()) return;

        onAddEvent({
            title: newEvent.title,
            description: newEvent.description,
            timestamp: new Date(newEvent.timestamp),
            type: newEvent.type,
        });

        setNewEvent({
            title: '',
            description: '',
            timestamp: new Date().toISOString().slice(0, 16),
            type: 'incident',
        });
        setIsAdding(false);
    };

    const sortedEvents = [...events].sort((a, b) =>
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );

    return (
        <Card variant="default" padding="lg" className={cn('animate-slide-up', className)}>
            <CardHeader>
                <div className="flex items-center gap-2">
                    <Icon name="GitBranch" size="sm" className="text-muted-foreground" />
                    <CardTitle className="text-sm">Crime Timeline</CardTitle>
                    <span className="ml-2 px-2 py-0.5 text-xs bg-secondary text-muted-foreground rounded-full">
                        {events.length} events
                    </span>
                </div>
                <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => setIsAdding(!isAdding)}
                >
                    <Icon name={isAdding ? 'X' : 'Plus'} size="xs" />
                    {isAdding ? 'Cancel' : 'Add Event'}
                </Button>
            </CardHeader>

            {/* Add new event form */}
            {isAdding && (
                <div className="mb-4 p-4 bg-secondary/50 rounded-lg border border-border animate-slide-up">
                    <h4 className="text-sm font-medium text-foreground mb-4">Add Timeline Event</h4>

                    <div className="space-y-4">
                        {/* Event type selector */}
                        <div className="flex flex-wrap gap-2">
                            {Object.entries(eventTypeConfig).filter(([key]) => key !== 'ai-suggestion').map(([type, config]) => (
                                <button
                                    key={type}
                                    className={cn(
                                        'px-3 py-1.5 rounded-lg text-xs font-medium transition-all',
                                        'flex items-center gap-1.5',
                                        newEvent.type === type
                                            ? 'bg-foreground text-background'
                                            : 'bg-secondary text-muted-foreground hover:text-foreground'
                                    )}
                                    onClick={() => setNewEvent({ ...newEvent, type: type as TimelineEventEditable['type'] })}
                                >
                                    <Icon name={config.icon} size="xs" />
                                    {config.label}
                                </button>
                            ))}
                        </div>

                        <Input
                            label="Event Title"
                            value={newEvent.title}
                            onInput={(e) => setNewEvent({ ...newEvent, title: (e.target as HTMLInputElement).value })}
                            placeholder="What happened?"
                        />

                        <Textarea
                            label="Description"
                            value={newEvent.description}
                            onInput={(e) => setNewEvent({ ...newEvent, description: (e.target as HTMLTextAreaElement).value })}
                            placeholder="Describe this event in detail..."
                            rows={3}
                        />

                        <Input
                            label="Date & Time"
                            type="datetime-local"
                            value={newEvent.timestamp}
                            onInput={(e) => setNewEvent({ ...newEvent, timestamp: (e.target as HTMLInputElement).value })}
                        />

                        <div className="flex justify-end gap-2">
                            <Button variant="ghost" size="sm" onClick={() => setIsAdding(false)}>
                                Cancel
                            </Button>
                            <Button size="sm" onClick={handleAddEvent} disabled={!newEvent.title.trim()}>
                                <Icon name="Plus" size="xs" />
                                Add to Timeline
                            </Button>
                        </div>
                    </div>
                </div>
            )}

            {/* Timeline */}
            {sortedEvents.length === 0 ? (
                <div className="text-center py-8">
                    <Icon name="GitBranch" size="lg" className="text-muted-foreground/50 mx-auto mb-3" />
                    <p className="text-sm text-muted-foreground mb-2">No timeline events yet</p>
                    <p className="text-xs text-muted-foreground">
                        Add events to build a timeline of what happened
                    </p>
                </div>
            ) : (
                <div className="space-y-0">
                    {sortedEvents.map((event, index) => {
                        const config = eventTypeConfig[event.type];
                        const isLast = index === sortedEvents.length - 1;
                        const isEditing = editing?.eventId === event.id;

                        return (
                            <div key={event.id} className="relative pl-8 group">
                                {/* Timeline line */}
                                {!isLast && (
                                    <div className="absolute left-[11px] top-8 bottom-0 w-px bg-border" />
                                )}

                                {/* Icon */}
                                <div className={cn(
                                    'absolute left-0 top-1 w-6 h-6 rounded-full flex items-center justify-center',
                                    config.color,
                                    event.isAISuggested && 'ring-2 ring-yellow-500/30'
                                )}>
                                    <Icon name={config.icon} size="xs" />
                                </div>

                                {/* Content */}
                                <div className={cn(
                                    'pb-4 pl-2',
                                    event.isAISuggested && 'opacity-80'
                                )}>
                                    {isEditing ? (
                                        <div className="p-3 bg-secondary/50 rounded-lg border border-border space-y-3">
                                            <Input
                                                value={editing.title}
                                                onInput={(e) => setEditing({ ...editing, title: (e.target as HTMLInputElement).value })}
                                                placeholder="Event title"
                                            />
                                            <Textarea
                                                value={editing.description}
                                                onInput={(e) => setEditing({ ...editing, description: (e.target as HTMLTextAreaElement).value })}
                                                placeholder="Description"
                                                rows={2}
                                            />
                                            <Input
                                                type="datetime-local"
                                                value={editing.timestamp}
                                                onInput={(e) => setEditing({ ...editing, timestamp: (e.target as HTMLInputElement).value })}
                                            />
                                            <div className="flex justify-end gap-2">
                                                <Button variant="ghost" size="sm" onClick={() => setEditing(null)}>
                                                    Cancel
                                                </Button>
                                                <Button size="sm" onClick={handleSaveEdit}>
                                                    Save
                                                </Button>
                                            </div>
                                        </div>
                                    ) : (
                                        <>
                                            <div className="flex items-start justify-between gap-2">
                                                <div>
                                                    <p className="text-sm font-medium text-foreground flex items-center gap-2">
                                                        {event.title}
                                                        {event.isAISuggested && (
                                                            <span className="px-1.5 py-0.5 text-[10px] bg-yellow-500/20 text-yellow-400 rounded">
                                                                AI Suggested
                                                            </span>
                                                        )}
                                                    </p>
                                                    <p className="text-xs text-muted-foreground mt-1">
                                                        {formatDate(event.timestamp)}
                                                    </p>
                                                </div>

                                                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                                    {event.isAISuggested && onAcceptSuggestion && (
                                                        <Button
                                                            variant="ghost"
                                                            size="icon"
                                                            className="w-7 h-7"
                                                            onClick={() => onAcceptSuggestion(event.id)}
                                                        >
                                                            <Icon name="Check" size="xs" className="text-green-400" />
                                                        </Button>
                                                    )}
                                                    <Button
                                                        variant="ghost"
                                                        size="icon"
                                                        className="w-7 h-7"
                                                        onClick={() => handleStartEdit(event)}
                                                    >
                                                        <Icon name="Pencil" size="xs" />
                                                    </Button>
                                                    <Button
                                                        variant="ghost"
                                                        size="icon"
                                                        className="w-7 h-7"
                                                        onClick={() => onDeleteEvent(event.id)}
                                                    >
                                                        <Icon name="Trash2" size="xs" className="text-red-400" />
                                                    </Button>
                                                </div>
                                            </div>

                                            {event.description && (
                                                <p className="text-xs text-muted-foreground mt-2 leading-relaxed">
                                                    {event.description}
                                                </p>
                                            )}
                                        </>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </Card>
    );
}

export default EditableTimeline;
