import React from 'react';
import { formatPercentage, formatCount } from '../../utils/currency.js';
import { ShieldCheck, Sparkles, ShieldAlert, CheckCircle2, ArrowRight } from 'lucide-react';

export default function PolicyAgreementMatrix({ agreement = null, isLoading = false }) {
  if (isLoading) {
    return (
      <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs h-64 animate-pulse">
        <div className="h-4 w-44 bg-slate-200 rounded mb-3" />
        <div className="h-3 w-64 bg-slate-100 rounded mb-6" />
        <div className="grid grid-cols-2 gap-3">
          <div className="h-20 bg-slate-100 rounded" />
          <div className="h-20 bg-slate-100 rounded" />
        </div>
      </div>
    );
  }

  if (!agreement) {
    return (
      <div className="bg-white p-8 rounded-xl border border-slate-200/80 shadow-xs text-center text-xs text-slate-500">
        Decision agreement analytics are not available from the backend yet.
      </div>
    );
  }

  const breakdown = agreement.breakdown || {};
  const agreementRate = agreement.agreement_rate || 0;

  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">
            Policy / ML Decision Agreement
          </h3>
          <p className="text-xs text-slate-500">
            Alignment between statistical ML advisory and deterministic safety gates.
          </p>
        </div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-indigo-50 text-indigo-700 font-semibold text-xs rounded-md border border-indigo-200">
          <Sparkles size={13} />
          <span>Agreement: {formatPercentage(agreementRate)}</span>
        </div>
      </div>

      {/* 4-Quadrant Agreement Matrix */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
        {/* Quadrant 1: Both Allow */}
        <div className="p-3.5 rounded-lg bg-emerald-50/70 border border-emerald-200/80">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-bold text-emerald-950 flex items-center gap-1.5">
              <CheckCircle2 size={14} className="text-emerald-600" />
              <span>Concurrence: Both Allow</span>
            </span>
            <span className="font-mono font-bold text-emerald-800 text-sm">
              {formatCount(breakdown.both_allow || 0)}
            </span>
          </div>
          <p className="text-[11px] text-emerald-800/80 leading-relaxed">
            Policy permitted retry and ML scored positive recovery probability.
          </p>
        </div>

        {/* Quadrant 2: Both Block */}
        <div className="p-3.5 rounded-lg bg-slate-100 border border-slate-200">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
              <ShieldAlert size={14} className="text-slate-600" />
              <span>Concurrence: Both Block</span>
            </span>
            <span className="font-mono font-bold text-slate-800 text-sm">
              {formatCount(breakdown.both_block || 0)}
            </span>
          </div>
          <p className="text-[11px] text-slate-600 leading-relaxed">
            Both systems blocked retry (e.g. repeated invalid credentials, high friction).
          </p>
        </div>

        {/* Quadrant 3: Policy Block / ML Recommend (Safety Gate Overrides) */}
        <div className="p-3.5 rounded-lg bg-rose-50/70 border border-rose-200/80">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-bold text-rose-950 flex items-center gap-1.5">
              <ShieldAlert size={14} className="text-rose-600" />
              <span>Safety Interventions (Policy Blocked ML)</span>
            </span>
            <span className="font-mono font-bold text-rose-800 text-sm">
              {formatCount(breakdown.policy_block_ml_recommend || agreement.safety_interventions || 0)}
            </span>
          </div>
          <p className="text-[11px] text-rose-800/80 leading-relaxed">
            Deterministic ceiling (e.g. max 2 attempts) safely vetoed ML recommendation.
          </p>
        </div>

        {/* Quadrant 4: Policy Allow / ML Hesitant */}
        <div className="p-3.5 rounded-lg bg-amber-50/70 border border-amber-200/80">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-bold text-amber-950 flex items-center gap-1.5">
              <ShieldCheck size={14} className="text-amber-700" />
              <span>Cautious Policy Approval</span>
            </span>
            <span className="font-mono font-bold text-amber-800 text-sm">
              {formatCount(breakdown.policy_allow_ml_hesitant || 0)}
            </span>
          </div>
          <p className="text-[11px] text-amber-800/80 leading-relaxed">
            Permitted by rulebook while ML scored lower confidence; executed with cooldown.
          </p>
        </div>
      </div>

      <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-600 flex items-start gap-2">
        <ShieldCheck size={16} className="text-indigo-600 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-slate-900">Governance Principle: </span>
          The deterministic recovery policy is authoritative. When probabilistic ML signals disagree with hard compliance rules, the safety gate takes precedence.
        </div>
      </div>
    </div>
  );
}
