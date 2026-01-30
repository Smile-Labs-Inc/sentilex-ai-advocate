import type { LegalAnalysis } from '../services/lawbook.tsx';

/**
 * Formats the legal query response into a readable markdown string
 * @param analysis - The legal analysis from the API
 * @returns Formatted markdown string
 */
export function formatLegalResponse(analysis: LegalAnalysis): string {
    let formatted = '';

    // Add the main response (legal analysis)
    formatted += analysis.response;
    formatted += '\n\n---\n\n';

    // Add confidence note
    if (analysis.confidence_note) {
        formatted += analysis.confidence_note;
        formatted += '\n\n';
    }

    // Add metadata summary
    if (analysis.metadata) {
        formatted += '**Analysis Metadata:**\n';
        formatted += `- Sources: ${analysis.metadata.sources_count}\n`;
        formatted += `- Citations: ${analysis.metadata.citations_count}\n`;
        formatted += `- Validation: ${analysis.metadata.validation_status}\n`;
        formatted += `- Confidence: ${Math.round(analysis.metadata.reasoning_confidence * 100)}%\n`;
        formatted += '\n';
    }

    // Add disclaimer
    if (analysis.disclaimer) {
        formatted += analysis.disclaimer;
    }

    return formatted;
}
