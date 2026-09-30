import React from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  RotateCcw, 
  ShieldCheck, 
  Cpu, 
  ActivitySquare,
  Sparkles
} from 'lucide-react';
import { formatCount, formatPercentage } from '../../utils/currency.js';

export default function RecoveryHealth({ 
  metrics = null, 
  isLoading = false 
}) {
  if (isLoading) {
    return (
      <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs h-80 flex flex-col justify-between">
        <div className="animate-pulse space-y-2">
          <div className="h-4 w-32 bg-slate-200 rounded" />
          <div className="h-3 w-48 bg-slate-100 rounded" />
        </div>
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-8 bg-slate-100/70 rounded animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  const items = [
    {
      label: 'Cases processed',
      value: formatCount(metrics?.total_cases || 0),
      icon: ActivitySquare,
      color: 'text-slate-700',
      bg: 'bg-slate-100',
      description: 'Payment failure events captured',
    },
    {
      label: 'Successful actions',
      value: formatCount(metrics?.executed_actions || metrics?.recovered_cases || 0),
      icon: CheckCircle2,
      color: 'text-emerald-700',
      bg: 'bg-emerald-50',
      description: 'Policy-approved recovery links completed',
    },
    {
      label: 'Failed / blocked actions',
      value: formatCount(metrics?.failed_actions || 0),
      icon: XCircle,
      color: 'text-rose-700',
      bg: 'bg-rose-50',
      description: 'Stopped safely by safety ceiling or errors',
    },
    {
      label: 'Automated recovery attempts',
      value: `${formatCount(metrics?.total_attempts || 0)} attempts`,
      icon: RotateCcw,
      color: 'text-amber-700',
      bg: 'bg-amber-50',
      description: 'Enforces hard 2-attempt limit per case',
    },
    {
      label: 'Policy-eligible cases',
      value: formatCount(metrics?.policy_eligible_cases || 0),
      icon: ShieldCheck,
      color: 'text-teal-700',
      bg: 'bg-teal-50',
      description: 'Deterministic rules permitted recovery',
    },
    {
      label: 'ML / Policy agreement rate',
      value: formatPercentage(metrics?.ml_policy_agreement_rate || 0),
      icon: Sparkles,
      color: 'text-indigo-700',
      bg: 'bg-indigo-50',
      description: 'Advisory alignment with policy gate',
    },
  ];

  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-1">
          <h3 className="text-base font-bold text-slate-900">
            Recovery Health
          </h3>
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Operations
          </span>
        </div>
        <p className="text-xs text-slate-500 mb-4">
          Deterministic execution & safety boundary enforcement.
        </p>

        <div className="divide-y divide-slate-100">
          {items.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div key={idx} className="py-2.5 flex items-center justify-between gap-3 text-xs">
                <div className="flex items-center gap-2.5 min-w-0">
                  <div className={`w-6 h-6 rounded-md flex items-center justify-center shrink-0 ${item.bg} ${item.color}`}>
                    <Icon size={13} />
                  </div>
                  <div className="truncate">
                    <span className="font-semibold text-slate-800">{item.label}</span>
                    <span className="hidden sm:inline text-slate-400 text-[11px] ml-2 font-normal">
                      · {item.description}
                    </span>
                  </div>
                </div>
                <div className="font-mono font-semibold text-slate-900 text-xs shrink-0">
                  {item.value}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500 bg-slate-50/80 px-3 py-2 rounded-lg">
        <span className="font-medium text-slate-700">Safety Ceiling</span>
        <span className="font-mono text-indigo-700 font-semibold">Max 2 automated attempts</span>
      </div>
    </div>
  );
}
