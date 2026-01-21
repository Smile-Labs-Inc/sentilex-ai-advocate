// =============================================================================
// FindLawyersButton Molecule
// Button to navigate to lawyer finder
// =============================================================================

import { useState } from 'preact/hooks';
import { cn } from '../../../lib/utils';
import { Icon } from '../../atoms/Icon/Icon';

export interface FindLawyersButtonProps {
    nearbyCount?: number;
    onClick: () => void;
    className?: string;
}

export function FindLawyersButton({
    nearbyCount = 0,
    onClick,
    className,
}: FindLawyersButtonProps) {
    const [isHovered, setIsHovered] = useState(false);

    return (
        <button
            className={cn(
                'w-full p-4 rounded-xl transition-all duration-300',
                'bg-gradient-to-r from-purple-600/10 to-blue-600/10',
                'border border-purple-500/20',
                'hover:from-purple-600/20 hover:to-blue-600/20',
                'hover:border-purple-500/40 hover:scale-[1.02]',
                'active:scale-[0.99]',
                'group cursor-pointer',
                className
            )}
            onClick={onClick}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            <div className="flex items-center gap-4">
                {/* Icon */}
                <div className={cn(
                    'w-12 h-12 rounded-full flex items-center justify-center',
                    'bg-purple-500/20',
                    'transition-transform duration-300',
                    isHovered && 'scale-110'
                )}>
                    <Icon name="Scale" size="md" className="text-purple-400" />
                </div>

                {/* Text */}
                <div className="flex-1 text-left">
                    <p className="text-base font-semibold text-foreground flex items-center gap-2">
                        Find Nearby Lawyers
                        <Icon
                            name="ArrowRight"
                            size="sm"
                            className={cn(
                                'transition-transform duration-300',
                                isHovered && 'translate-x-1'
                            )}
                        />
                    </p>
                    <p className="text-xs text-purple-300/80">
                        {nearbyCount > 0
                            ? `${nearbyCount} verified lawyers in your area`
                            : 'Connect with legal professionals'}
                    </p>
                </div>

                {/* Location indicator */}
                <div className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-500/10 rounded-full">
                    <Icon name="MapPin" size="xs" className="text-purple-400" />
                    <span className="text-xs font-medium text-purple-300">Nearby</span>
                </div>
            </div>
        </button>
    );
}

export default FindLawyersButton;
