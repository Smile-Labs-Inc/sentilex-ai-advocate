// =============================================================================
// ProgressBar Atom
// Step progress indicator for wizards
// =============================================================================

import { cn } from '../../../lib/utils';

export interface ProgressBarProps {
    currentStep: number;
    totalSteps: number;
    className?: string;
}

export function ProgressBar({ currentStep, totalSteps, className }: ProgressBarProps) {
    const progress = (currentStep / totalSteps) * 100;

    return (
        <div className={cn('space-y-2', className)}>
            {/* Progress bar */}
            <div className="h-1 bg-secondary rounded-full overflow-hidden">
                <div
                    className="h-full bg-primary rounded-full transition-all duration-500 ease-out"
                    style={{ width: `${progress}%` }}
                />
            </div>

            {/* Step indicators */}
            <div className="flex justify-between">
                <span className="text-xs text-muted-foreground">
                    Step {currentStep} of {totalSteps}
                </span>
                <span className="text-xs text-muted-foreground">
                    {Math.round(progress)}% complete
                </span>
            </div>
        </div>
    );
}

export default ProgressBar;
