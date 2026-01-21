// =============================================================================
// RadioGroup Atom
// Radio button group for single selection
// =============================================================================

import { cn } from '../../../lib/utils';
import { Icon, type IconName } from '../Icon/Icon';

export interface RadioOption {
    value: string;
    label: string;
    description?: string;
    icon?: IconName;
}

export interface RadioGroupProps {
    name: string;
    options: RadioOption[];
    value: string;
    onChange: (value: string) => void;
    label?: string;
    className?: string;
}

export function RadioGroup({
    name,
    options,
    value,
    onChange,
    label,
    className,
}: RadioGroupProps) {
    return (
        <div className={cn('space-y-3', className)}>
            {label && (
                <label className="block text-sm font-medium text-foreground/80 mb-3">
                    {label}
                </label>
            )}
            <div className="space-y-2">
                {options.map((option) => {
                    const isSelected = value === option.value;
                    return (
                        <label
                            key={option.value}
                            className={cn(
                                'flex items-start gap-3 p-4 rounded-lg cursor-pointer',
                                'border transition-all duration-200',
                                isSelected
                                    ? 'bg-accent/50 border-ring'
                                    : 'bg-secondary/30 border-border hover:border-accent'
                            )}
                        >
                            <input
                                type="radio"
                                name={name}
                                value={option.value}
                                checked={isSelected}
                                onChange={() => onChange(option.value)}
                                className="sr-only"
                            />

                            {/* Radio indicator */}
                            <div className={cn(
                                'w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5',
                                isSelected
                                    ? 'border-primary bg-primary'
                                    : 'border-muted-foreground bg-transparent'
                            )}>
                                {isSelected && (
                                    <div className="w-2 h-2 rounded-full bg-primary-foreground" />
                                )}
                            </div>

                            {/* Icon */}
                            {option.icon && (
                                <Icon
                                    name={option.icon}
                                    size="md"
                                    className={cn(
                                        'flex-shrink-0 mt-0.5',
                                        isSelected ? 'text-foreground' : 'text-muted-foreground'
                                    )}
                                />
                            )}

                            {/* Content */}
                            <div className="flex-1">
                                <div className={cn(
                                    'text-sm font-medium',
                                    isSelected ? 'text-foreground' : 'text-foreground/80'
                                )}>
                                    {option.label}
                                </div>
                                {option.description && (
                                    <div className="text-xs text-muted-foreground mt-0.5">
                                        {option.description}
                                    </div>
                                )}
                            </div>
                        </label>
                    );
                })}
            </div>
        </div>
    );
}

export default RadioGroup;
