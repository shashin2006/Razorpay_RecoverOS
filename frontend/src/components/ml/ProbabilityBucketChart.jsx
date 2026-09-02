import React from 'react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid,
  Legend
} from 'recharts';
import { formatPercentage } from '../../utils/currency.js';

export default function ProbabilityBucketChart({ buckets = [], isLoading = false }) {
  if (isLoading) {
    return (
      <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs h-80 flex flex-col justify-between">
        <div className="animate-pulse space-y-2">
          <div className="h-4 w-48 bg-slate-200 rounded" />
          <div className="h-3 w-64 bg-slate-100 rounded" />
        </div>
        <div className="h-48 bg-slate-100/60 rounded-lg animate-pulse" />
      </div>
    );
  }

  if (!buckets || buckets.length === 0) {
    return (
      <div className="bg-white p-8 rounded-xl border border-slate-200/80 shadow-xs text-center text-xs text-slate-500">
        Probability bucket distribution data is not available from the backend yet.
      </div>
    );
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-slate-900 text-slate-100 p-3 rounded-lg text-xs shadow-xl border border-slate-800 space-y-1">
          <p className="font-bold text-white">{data.label || data.bucket}</p>
          <div className="flex justify-between gap-4 text-slate-300">
            <span>Total Predicted Cases:</span>
            <span className="font-mono font-semibold text-white">{data.count}</span>
          </div>
          {data.recovered_count !== undefined && (
            <div className="flex justify-between gap-4 text-emerald-400">
              <span>Actual Recovered:</span>
              <span className="font-mono font-semibold">{data.recovered_count}</span>
            </div>
          )}
          {data.conversion_rate !== undefined && (
            <div className="flex justify-between gap-4 text-indigo-300 pt-1 border-t border-slate-800">
              <span>Empirical Conversion:</span>
              <span className="font-mono font-semibold">{formatPercentage(data.conversion_rate)}</span>
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">
            Probability Distribution Calibration
          </h3>
          <p className="text-xs text-slate-500">
            Model confidence tiers vs. real recovered conversion.
          </p>
        </div>
        <span className="text-[11px] font-mono text-slate-500 bg-slate-100 px-2.5 py-1 rounded-md">
          5 Confidence Intervals
        </span>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={buckets} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
            <XAxis 
              dataKey="bucket" 
              tick={{ fontSize: 11, fill: '#64748b' }}
              axisLine={{ stroke: '#e2e8f0' }}
              tickLine={false}
            />
            <YAxis 
              tick={{ fontSize: 11, fill: '#64748b' }}
              axisLine={{ stroke: '#e2e8f0' }}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              wrapperStyle={{ fontSize: 12, paddingTop: 10 }}
              iconType="circle"
            />
            <Bar dataKey="count" name="Cases Scored" fill="#6366f1" radius={[4, 4, 0, 0]} barSize={24} />
            <Bar dataKey="recovered_count" name="Verified Recovered" fill="#10b981" radius={[4, 4, 0, 0]} barSize={24} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
