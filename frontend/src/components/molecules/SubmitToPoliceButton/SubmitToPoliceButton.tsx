// =============================================================================
// SubmitToPoliceButton Molecule
// Conditionally visible button for submitting case to police
// =============================================================================

import { useState } from 'preact/hooks';
import { cn } from '../../../lib/utils';

import { Icon } from '../../atoms/Icon/Icon';

export interface SubmitToPoliceButtonProps {
    isEnabled: boolean;
    violationsCount: number;
    onSubmit: () => void;
    className?: string;
}

export function SubmitToPoliceButton({
    isEnabled,
    violationsCount,
    onSubmit,
    className,
}: SubmitToPoliceButtonProps) {
    const [isHovered, setIsHovered] = useState(false);

    if (!isEnabled) {
        return (
            <div className={cn(
                'p-4 bg-secondary/50 border border-border rounded-xl',
                'opacity-60',
                className
            )}>
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center">
                        <Icon name="ShieldOff" size="sm" className="text-muted-foreground" />
                    </div>
                    <div>
                        <p className="text-sm text-muted-foreground font-medium">Submit to Police</p>
                        <p className="text-xs text-muted-foreground/80">
                            No violations identified yet
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <button
            className={cn(
                'w-full p-4 rounded-xl transition-all duration-300',
                'bg-gradient-to-r from-red-600/20 to-orange-600/20',
                'border border-red-500/30',
                'hover:from-red-600/30 hover:to-orange-600/30',
                'hover:border-red-500/50 hover:scale-[1.02]',
                'active:scale-[0.99]',
                'group cursor-pointer',
                'animate-fade-in',
                className
            )}
            onClick={onSubmit}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            <div className="flex items-center gap-4">
                {/* Icon with pulse animation */}
                <div className={cn(
                    'relative w-12 h-12 rounded-full flex items-center justify-center',
                    'bg-red-500/20',
                    'transition-transform duration-300',
                    isHovered && 'scale-110'
                )}>
                    <Icon name="Shield" size="md" className="text-red-400" />
                    {/* Pulse ring */}
                    <div className="absolute inset-0 rounded-full bg-red-500/20 animate-ping" />
                </div>

                {/* Text */}
                <div className="flex-1 text-left">
                    <p className="text-base font-semibold text-white flex items-center gap-2">
                        Submit to Police
                        <Icon
                            name="ArrowRight"
                            size="sm"
                            className={cn(
                                'transition-transform duration-300',
                                isHovered && 'translate-x-1'
                            )}
                        />
                    </p>
                    <p className="text-xs text-red-300/80">
                        {violationsCount} potential violation{violationsCount !== 1 ? 's' : ''} identified
                    </p>
                </div>

                {/* Badge */}
                <div className="px-3 py-1.5 bg-red-500/20 rounded-full">
                    <span className="text-xs font-medium text-red-300">Ready</span>
                </div>
            </div>

            {/* Bottom note */}
            <div className="mt-3 pt-3 border-t border-red-500/10">
                <p className="text-[10px] text-zinc-500 flex items-center gap-1.5">
                    <Icon name="Info" size="xs" />
                    Your evidence will be securely transmitted to law enforcement
                </p>
            </div>
        </button>
    );
}

export default SubmitToPoliceButton;
