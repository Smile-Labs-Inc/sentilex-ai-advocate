// =============================================================================
// EnhancedLawsSection Organism
// Display identified laws with violation status and include toggles
// =============================================================================

import { useState } from 'preact/hooks';
import { cn } from '../../../lib/utils';
import { Card, CardHeader, CardTitle } from '../../atoms/Card/Card';
import { Button } from '../../atoms/Button/Button';
import { Icon } from '../../atoms/Icon/Icon';
import type { LawViolation, ViolationSeverity } from '../../../types';

export interface EnhancedLawsSectionProps {
    laws: LawViolation[];
    onToggleInclude: (lawId: string, included: boolean) => void;
    isAnalyzing?: boolean;
    className?: string;
}

const severityConfig: Record<ViolationSeverity, { label: string; color: string; bgColor: string }> = {
    critical: {
        label: 'Critical',
        color: 'text-red-400',
        bgColor: 'bg-red-500/10 border-red-500/20'
    },
    high: {
        label: 'High',
        color: 'text-orange-400',
        bgColor: 'bg-orange-500/10 border-orange-500/20'
    },
    medium: {
        label: 'Medium',
        color: 'text-yellow-400',
        bgColor: 'bg-yellow-500/10 border-yellow-500/20'
    },
    low: {
        label: 'Low',
        color: 'text-muted-foreground',
        bgColor: 'bg-secondary border-border'
    },
};

export function EnhancedLawsSection({
    laws,
    onToggleInclude,
    isAnalyzing = false,
    className,
}: EnhancedLawsSectionProps) {
    const [expandedLaws, setExpandedLaws] = useState<Set<string>>(new Set());

    const violatedLaws = laws.filter(l => l.isViolated);
    const potentialLaws = laws.filter(l => !l.isViolated);

    const toggleExpand = (lawId: string) => {
        const newExpanded = new Set(expandedLaws);
        if (newExpanded.has(lawId)) {
            newExpanded.delete(lawId);
        } else {
            newExpanded.add(lawId);
        }
        setExpandedLaws(newExpanded);
    };

    const renderLawCard = (law: LawViolation) => {
        const severity = severityConfig[law.severity];
        const isExpanded = expandedLaws.has(law.id);

        return (
            <div
                key={law.id}
                className={cn(
                    'p-4 rounded-lg border transition-all duration-300',
                    law.isViolated
                        ? 'bg-red-500/5 border-red-500/20 hover:border-red-500/40'
                        : 'bg-secondary/30 border-border hover:border-input',
                    law.includedInReport && 'ring-1 ring-green-500/30'
                )}
            >
                <div className="flex items-start gap-3">
                    {/* Include checkbox */}
                    <button
                        onClick={() => onToggleInclude(law.id, !law.includedInReport)}
                        className={cn(
                            'w-5 h-5 rounded flex items-center justify-center shrink-0 mt-0.5',
                            'border transition-all duration-200',
                            law.includedInReport
                                ? 'bg-green-500 border-green-500 text-black'
                                : 'border-muted-foreground hover:border-foreground'
                        )}
                    >
                        {law.includedInReport && <Icon name="Check" size="xs" />}
                    </button>

                    <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2 mb-1">
                            <div>
                                <h4 className="text-sm font-medium text-foreground flex items-center gap-2">
                                    {law.name}
                                    {law.isViolated && (
                                        <span className="px-1.5 py-0.5 text-[10px] bg-red-500/20 text-red-400 rounded animate-pulse">
                                            VIOLATED
                                        </span>
                                    )}
                                </h4>
                                <p className="text-xs text-muted-foreground mt-0.5">
                                    {law.section} • {law.jurisdiction}
                                </p>
                            </div>

                            <div className="flex items-center gap-2 shrink-0">
                                {/* Confidence */}
                                <div className="text-right">
                                    <div className="text-[10px] text-muted-foreground">Confidence</div>
                                    <div className={cn(
                                        'text-xs font-medium',
                                        law.confidence >= 80 ? 'text-green-400' :
                                            law.confidence >= 50 ? 'text-yellow-400' : 'text-muted-foreground'
                                    )}>
                                        {law.confidence}%
                                    </div>
                                </div>

                                {/* Severity badge */}
                                <span className={cn(
                                    'text-[10px] px-2 py-0.5 rounded border',
                                    severity.bgColor,
                                    severity.color
                                )}>
                                    {severity.label}
                                </span>
                            </div>
                        </div>

                        {/* Description preview or full */}
                        <p className={cn(
                            'text-xs text-muted-foreground leading-relaxed mt-2',
                            !isExpanded && 'line-clamp-2'
                        )}>
                            {law.description}
                        </p>

                        {/* Expand/collapse and source */}
                        <div className="flex items-center justify-between mt-2">
                            <button
                                onClick={() => toggleExpand(law.id)}
                                className="text-xs text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
                            >
                                <Icon name={isExpanded ? 'ChevronUp' : 'ChevronDown'} size="xs" />
                                {isExpanded ? 'Show less' : 'Read more'}
                            </button>

                            {law.sourceUrl && (
                                <a
                                    href={law.sourceUrl}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
                                >
                                    <Icon name="ExternalLink" size="xs" />
                                    View Source
                                </a>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <Card variant="default" padding="lg" className={cn('animate-slide-up', className)}>
            <CardHeader>
                <div className="flex items-center gap-2">
                    <Icon name="Scale" size="sm" className="text-purple-400" />
                    <CardTitle className="text-sm">Identified Laws</CardTitle>
                    {isAnalyzing && (
                        <span className="flex items-center gap-1.5 text-xs text-yellow-400">
                            <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse" />
                            Analyzing...
                        </span>
                    )}
                </div>
                <div className="flex items-center gap-2">
                    {violatedLaws.length > 0 && (
                        <span className="px-2 py-0.5 text-xs bg-red-500/20 text-red-400 rounded-full">
                            {violatedLaws.length} violated
                        </span>
                    )}
                    <span className="px-2 py-0.5 text-xs bg-secondary text-muted-foreground rounded-full">
                        {laws.length} total
                    </span>
                </div>
            </CardHeader>

            {laws.length === 0 ? (
                <div className="text-center py-8">
                    <Icon name="Scale" size="lg" className="text-muted-foreground/50 mx-auto mb-3" />
                    <p className="text-sm text-muted-foreground mb-2">No laws identified yet</p>
                    <p className="text-xs text-muted-foreground">
                        {isAnalyzing
                            ? 'The AI is analyzing your case against the legal database...'
                            : 'Provide more details to help identify applicable laws'
                        }
                    </p>
                    {isAnalyzing && (
                        <div className="mt-4 flex justify-center">
                            <div className="flex gap-1">
                                <div className="w-2 h-2 bg-yellow-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                <div className="w-2 h-2 bg-yellow-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                <div className="w-2 h-2 bg-yellow-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                            </div>
                        </div>
                    )}
                </div>
            ) : (
                <div className="space-y-6">
                    {/* Violated laws section */}
                    {violatedLaws.length > 0 && (
                        <div>
                            <h4 className="text-xs font-medium text-red-400 uppercase tracking-wide mb-3 flex items-center gap-2">
                                <Icon name="AlertTriangle" size="xs" />
                                Potentially Violated
                            </h4>
                            <div className="space-y-2">
                                {violatedLaws.map(renderLawCard)}
                            </div>
                        </div>
                    )}

                    {/* Other applicable laws */}
                    {potentialLaws.length > 0 && (
                        <div>
                            <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-3">
                                May Also Apply
                            </h4>
                            <div className="space-y-2">
                                {potentialLaws.map(renderLawCard)}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Selection summary */}
            {laws.length > 0 && (
                <div className="mt-4 pt-4 border-t border-border">
                    <div className="flex items-center justify-between text-xs">
                        <span className="text-muted-foreground">
                            {laws.filter(l => l.includedInReport).length} of {laws.length} included in report
                        </span>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                                const allIncluded = laws.every(l => l.includedInReport);
                                laws.forEach(l => onToggleInclude(l.id, !allIncluded));
                            }}
                        >
                            {laws.every(l => l.includedInReport) ? 'Deselect All' : 'Select All'}
                        </Button>
                    </div>
                </div>
            )}
        </Card>
    );
}

export default EnhancedLawsSection;
