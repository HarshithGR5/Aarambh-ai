'use client';
import { cn } from '@/lib/utils';
import type { RiskLevel } from '@/lib/types';

interface PDRSGaugeProps {
  score: number;
  riskLevel: RiskLevel;
  size?: 'sm' | 'md' | 'lg';
}

export function PDRSGauge({ score, riskLevel, size = 'md' }: PDRSGaugeProps) {
  const radius = size === 'lg' ? 60 : size === 'md' ? 48 : 36;
  const strokeWidth = size === 'lg' ? 8 : 6;
  const circumference = 2 * Math.PI * radius;
  const clampedScore = Math.max(0, Math.min(100, score));
  const dashOffset = circumference * (1 - clampedScore / 100);

  const colorMap: Record<RiskLevel, { stroke: string; text: string; bg: string; label: string }> = {
    GREEN: { stroke: '#16a34a', text: 'text-green-700',  bg: 'bg-green-50',  label: 'On Track' },
    AMBER: { stroke: '#d97706', text: 'text-amber-700', bg: 'bg-amber-50',  label: 'Monitor' },
    RED:   { stroke: '#dc2626', text: 'text-red-700',   bg: 'bg-red-50',    label: 'High Risk' },
  };

  const c = colorMap[riskLevel];
  const svgSize = (radius + strokeWidth) * 2 + 4;
  const cx = svgSize / 2;
  const cy = svgSize / 2;

  const fontSize = size === 'lg' ? 'text-3xl' : size === 'md' ? 'text-2xl' : 'text-xl';
  const labelSize = size === 'lg' ? 'text-sm' : 'text-xs';

  return (
    <div className={cn('inline-flex flex-col items-center gap-2')}>
      <div className="relative flex items-center justify-center">
        <svg width={svgSize} height={svgSize} className="-rotate-90">
          <circle
            cx={cx} cy={cy} r={radius}
            fill="none" stroke="#e2e8f0" strokeWidth={strokeWidth}
          />
          <circle
            cx={cx} cy={cy} r={radius}
            fill="none"
            stroke={c.stroke}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 1s ease-out' }}
          />
        </svg>
        <div className="absolute flex flex-col items-center">
          <span className={cn('font-bold font-display leading-none', fontSize, c.text)}>{score}</span>
          <span className={cn('font-medium text-muted-foreground', labelSize)}>/100</span>
        </div>
      </div>
      <span className={cn('font-semibold px-3 py-1 rounded-full text-xs', c.bg, c.text)}>
        {c.label}
      </span>
    </div>
  );
}
