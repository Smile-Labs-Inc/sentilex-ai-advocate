// =============================================================================
// DonutChart Organism
// Case type distribution chart using visx
// =============================================================================

import { Group } from '@visx/group';
import { Pie, Bar } from '@visx/shape';
import { scaleOrdinal, scaleBand, scaleLinear } from '@visx/scale';
import { ParentSize } from '@visx/responsive';
import { AxisBottom } from '@visx/axis';
import { cn } from '../../../lib/utils';
import { Card, CardHeader, CardTitle } from '../../atoms/Card/Card';
import { Icon } from '../../atoms/Icon/Icon';
import type { CaseTypeDistribution } from '../../../types';

interface MonthlyStats {
    month: string;
    value: number;
}

const mockMonthlyStats: MonthlyStats[] = [
    { month: 'Aug', value: 45 },
    { month: 'Sep', value: 52 },
    { month: 'Oct', value: 48 },
    { month: 'Nov', value: 65 },
    { month: 'Dec', value: 78 },
    { month: 'Jan', value: 92 },
];

export interface DonutChartProps {
    data: CaseTypeDistribution[];
    className?: string;
}

// Inner donut chart component
function DonutChartInner({
    data,
    width,
    height
}: {
    data: CaseTypeDistribution[];
    width: number;
    height: number;
}) {
    // Calculate dimensions
    const margin = { top: 20, right: 20, bottom: 20, left: 20 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    const radius = Math.min(innerWidth, innerHeight) / 2;
    const innerRadius = radius * 0.65; // Creates the donut hole
    const centerX = innerWidth / 2;
    const centerY = innerHeight / 2;

    // Color scale
    const colorScale = scaleOrdinal({
        domain: data.map(d => d.type),
        range: data.map(d => d.color),
    });

    // Accessor functions
    const getValue = (d: CaseTypeDistribution) => d.count;

    return (
        <svg width={width} height={height}>
            <Group top={centerY + margin.top} left={centerX + margin.left}>
                <Pie
                    data={data}
                    pieValue={getValue}
                    outerRadius={radius}
                    innerRadius={innerRadius}
                    padAngle={0.02}
                    cornerRadius={3}
                >
                    {(pie) =>
                        pie.arcs.map((arc, index) => {
                            const arcPath = pie.path(arc);
                            const arcFill = colorScale(arc.data.type);

                            return (
                                <g key={`arc-${index}`}>
                                    <path
                                        d={arcPath || ''}
                                        fill={arcFill}
                                        className="transition-all duration-300 hover:opacity-80"
                                        style={{ cursor: 'pointer' }}
                                    />
                                </g>
                            );
                        })
                    }
                </Pie>

                {/* Center text */}
                <text
                    textAnchor="middle"
                    dy="0.1em"
                    className="fill-foreground text-2xl font-light"
                >
                    {data.reduce((sum, d) => sum + d.count, 0).toLocaleString()}
                </text>
                <text
                    textAnchor="middle"
                    dy="1.5em"
                    className="fill-muted-foreground text-xs"
                >
                    Total Cases
                </text>
            </Group>
        </svg>
    );
}

function BarChartInner({ width, height }: { width: number; height: number }) {
    const data = mockMonthlyStats;
    const margin = { top: 20, right: 0, bottom: 20, left: 0 };

    // Bounds
    const xMax = width - margin.left - margin.right;
    const yMax = height - margin.top - margin.bottom;

    // Scales
    const xScale = scaleBand<string>({
        range: [0, xMax],
        round: true,
        domain: data.map(d => d.month),
        padding: 0.4,
    });

    const yScale = scaleLinear<number>({
        range: [yMax, 0],
        round: true,
        domain: [0, Math.max(...data.map(d => d.value))],
    });

    return (
        <svg width={width} height={height}>
            <Group top={margin.top} left={margin.left}>
                {data.map((d) => {
                    const barWidth = xScale.bandwidth();
                    const barHeight = yMax - (yScale(d.value) ?? 0);
                    const barX = xScale(d.month);
                    const barY = yMax - barHeight;
                    return (
                        <Bar
                            key={`bar-${d.month}`}
                            x={barX}
                            y={barY}
                            width={barWidth}
                            height={barHeight}
                            fill="currentColor"
                            className="text-primary/20 hover:text-primary transition-colors duration-300"
                            rx={4}
                        />
                    );
                })}
                <AxisBottom
                    scale={xScale}
                    top={yMax}
                    tickLabelProps={() => ({
                        fill: 'currentColor',
                        fontSize: 10,
                        textAnchor: 'middle',
                        className: 'text-muted-foreground fill-muted-foreground'
                    })}
                    stroke="transparent"
                    tickStroke="transparent"
                />
            </Group>
        </svg>
    );
}

export function DonutChart({ data, className }: DonutChartProps) {
    // Take top 4 for legend
    const legendItems = data.slice(0, 4);

    return (
        <Card variant="default" padding="lg" className={cn('animate-slide-up', className)}>
            <CardHeader>
                <div className="flex items-center gap-2">
                    <Icon name="PieChart" size="sm" className="text-muted-foreground" />
                    <CardTitle className="text-sm">Global Insights</CardTitle>
                </div>
            </CardHeader>

            <div className="flex items-center gap-6">
                {/* Chart */}
                <div className="w-56 h-56 flex-shrink-0">
                    <ParentSize>
                        {({ width, height }) => (
                            <DonutChartInner data={data} width={width} height={height} />
                        )}
                    </ParentSize>
                </div>

                {/* Legend */}
                <div className="flex-1 space-y-3 min-w-[140px]">
                    {legendItems.map((item) => (
                        <div key={item.type}>
                            <div className="flex items-center gap-2 text-xs mb-1">
                                <span
                                    className="w-2 h-2 rounded-sm"
                                    style={{ backgroundColor: item.color }}
                                />
                                <span className="text-muted-foreground">{item.label}</span>
                            </div>
                            <div className="text-sm font-medium text-foreground pl-4">
                                {item.count.toLocaleString()} ({item.percentage}%)
                            </div>
                        </div>
                    ))}
                </div>

                {/* Divider */}
                <div className="w-px h-40 bg-border hidden md:block" />

                {/* Bar Chart Section */}
                <div className="flex-1 hidden md:block">
                    <div className="mb-4">
                        <div className="text-xs text-muted-foreground mb-1">Monthly Solution Rate</div>
                        <div className="text-2xl font-light text-foreground">+12.5%</div>
                    </div>
                    <div className="h-32 w-full">
                        <ParentSize>
                            {({ width, height }) => (
                                <BarChartInner width={width} height={height} />
                            )}
                        </ParentSize>
                    </div>
                </div>
            </div>
        </Card>
    );
}

export default DonutChart;
