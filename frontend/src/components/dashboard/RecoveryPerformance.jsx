import React from 'react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Cell 
} from 'recharts';
import { formatMinorUnitsToINR, formatPercentage } from '../../utils/currency.js';
import { ShieldCheck, TrendingUp, AlertOctagon } from 'lucide-react';

export default function RecoveryPerformance({ 
  metrics = null, 
  isLoading = false 
}) {
  if (isLoading) {
    return (
      <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs h-80 flex flex-col justify-between">
        <div className="animate-pulse space-y-2">
          <div className="h-4 w-40 bg-slate-200 rounded" />
          <div className="h-3 w-64 bg-slate-100 rounded" />
        </div>
        <div className="h-48 bg-slate-100/60 rounded-lg animate-pulse" />
      </div>
    );
  }

  const atRiskMinor = metrics?.total_amount_at_risk_minor || 0;
  const recoveredMinor = metrics?.total_amount_recovered_minor || 0;
  const unrecoveredMinor = Math.max(0, atRiskMinor - recoveredMinor);
  const recoveryRate = metrics?.amount_recovery_rate || (atRiskMinor > 0 ? recoveredMinor / atRiskMinor : 0);

  const chartData = [
    {
      name: 'Total at Risk',
      amountMinor: atRiskMinor,
      displayVal: formatMinorUnitsToINR(atRiskMinor),
      color: '#64748b', // Slate 500
    },
    {
      name: 'Recovered',
      amountMinor: recoveredMinor,
      displayVal: formatMinorUnitsToINR(recoveredMinor),
      color: '#10b981', // Emerald 500
    },
    {
      name: 'Unrecovered',
      amountMinor: unrecoveredMinor,
      displayVal: formatMinorUnitsToINR(unrecoveredMinor),
      color: '#f59e0b', // Amber 500
    }
  ];

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-slate-900 text-slate-100 px-3 py-2 rounded-lg text-xs shadow-xl border border-slate-800">
          <p className="font-semibold">{data.name}</p>
          <p className="text-emerald-400 font-mono text-sm mt-0.5">
            {formatMinorUnitsToINR(data.amountMinor, { showDecimals: true })}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs flex flex-col justify-between">
      <div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-1">
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Recovery Performance
            </h3>
            <p className="text-xs text-slate-500">
              Total revenue at risk vs. verified recovered volume (Test Mode).
            </p>
          </div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-semibold self-start sm:self-auto">
            <TrendingUp size={13} />
            <span>Recovery Rate: {formatPercentage(recoveryRate)}</span>
          </div>
        </div>

        {/* Progress Ratio Bar */}
        <div className="mt-4 mb-5">
          <div className="flex justify-between text-xs text-slate-600 font-medium mb-1.5">
            <span className="flex items-center gap-1 text-emerald-700">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              Recovered: {formatMinorUnitsToINR(recoveredMinor)}
            </span>
            <span className="flex items-center gap-1 text-slate-500">
              <span className="w-2 h-2 rounded-full bg-slate-400" />
              At Risk: {formatMinorUnitsToINR(atRiskMinor)}
            </span>
          </div>
          <div className="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden flex">
            <div 
              className="bg-emerald-500 transition-all duration-500 ease-out" 
              style={{ width: `${Math.min(100, Math.max(0, recoveryRate * 100))}%` }} 
            />
            <div 
              className="bg-amber-400/70 transition-all duration-500 ease-out" 
              style={{ width: `${Math.min(100, Math.max(0, 100 - (recoveryRate * 100)))}%` }} 
            />
          </div>
        </div>
      </div>

      {/* Aggregate Bar Chart */}
      <div className="h-44 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart 
            data={chartData} 
            layout="vertical" 
            margin={{ top: 0, right: 30, left: 10, bottom: 0 }}
          >
            <XAxis 
              type="number" 
              tickFormatter={(v) => formatMinorUnitsToINR(v, { compact: true })}
              tick={{ fontSize: 11, fill: '#64748b' }}
              axisLine={{ stroke: '#e2e8f0' }}
              tickLine={false}
            />
            <YAxis 
              dataKey="name" 
              type="category" 
              tick={{ fontSize: 11, fill: '#475569', fontWeight: 500 }}
              axisLine={{ stroke: '#e2e8f0' }}
              tickLine={false}
              width={90}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(241, 245, 249, 0.6)' }} />
            <Bar dataKey="amountMinor" radius={[0, 4, 4, 0]} barSize={18}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-2 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
        <span>Authoritative backend metrics</span>
        <span>Bounded by deterministic safety gate</span>
      </div>
    </div>
  );
}
