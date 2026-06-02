'use client';
import { ResponsiveContainer, RadarChart as RechartsRadar, PolarGrid, PolarAngleAxis, Radar, Tooltip } from 'recharts';
import { DOMAIN_META } from '@/lib/utils';

interface RadarChartProps {
  domainScores: Record<string, number>;
  size?: number;
}

export function DDTRadarChart({ domainScores, size = 280 }: RadarChartProps) {
  const data = Object.entries(domainScores).map(([key, score]) => ({
    domain: DOMAIN_META[key]?.label ?? key,
    score: Math.round(score),
    fullMark: 100,
  }));

  if (!data.length) return null;

  return (
    <ResponsiveContainer width="100%" height={size}>
      <RechartsRadar data={data} cx="50%" cy="50%" outerRadius="75%">
        <PolarGrid gridType="polygon" stroke="#e2e8f0" />
        <PolarAngleAxis
          dataKey="domain"
          tick={{ fill: '#64748b', fontSize: 11, fontWeight: 500 }}
          tickLine={false}
        />
        <Tooltip
          formatter={(val: number) => [`${val}%`, 'Score']}
          contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0', fontSize: 12 }}
        />
        <Radar
          name="Score"
          dataKey="score"
          stroke="#0d8ee8"
          fill="#0d8ee8"
          fillOpacity={0.25}
          strokeWidth={2}
          dot={{ r: 4, fill: '#0d8ee8', strokeWidth: 0 }}
        />
      </RechartsRadar>
    </ResponsiveContainer>
  );
}
