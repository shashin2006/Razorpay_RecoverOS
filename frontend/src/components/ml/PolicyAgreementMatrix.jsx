import React, { useMemo } from 'react';
import { formatPercentage, formatCount } from '../../utils/currency.js';
import { ShieldCheck, Sparkles, ShieldAlert, CheckCircle2 } from 'lucide-react';

function numberFrom(object, keys, fallback = 0) {
  for (const key of keys) {
    const value = object?.[key];
    if (value !== null && value !== undefined && value !== '') {
      const n = Number(value);
      if (Number.isFinite(n)) return n;
    }
  }
  return fallback;
}

function normalizeAgreement(input) {
  const root = input?.agreement || input?.decision_agreement || input || {};
  const raw = root.breakdown || root.counts || root.categories || root.matrix || {};

  const breakdown = {
    both_allow: numberFrom(raw, ['both_allow', 'concurrence_both_allow', 'both_approve', 'allow_allow']),
    both_block: numberFrom(raw, ['both_block', 'concurrence_both_block', 'both_deny', 'block_block']),
    policy_block_ml_recommend: numberFrom(raw, [
      'policy_block_ml_recommend',
      'policy_blocked_ml_recommend',
      'safety_interventions',
      'policy_override_ml',
      'policy_block_ml_allow',
    ]),
    policy_allow_ml_hesitant: numberFrom(raw, [
      'policy_allow_ml_hesitant',
      'cautious_policy_approval',
      'policy_allow_ml_not_recommend',
      'policy_allow_ml_hesitant_count',
    ]),
  };

  const classifiedCount = Object.values(breakdown).reduce((sum, value) => sum + value, 0);
  const suppliedRate = numberFrom(root, ['agreement_rate', 'policy_ml_agreement_rate', 'agreement'], NaN);
  const agreementRate = Number.isFinite(suppliedRate)
    ? suppliedRate
    : classifiedCount > 0
      ? (breakdown.both_allow + breakdown.both_block) / classifiedCount
      : null;

  return { breakdown, classifiedCount, agreementRate };
}

export default function PolicyAgreementMatrix({ agreement = null, isLoading = false }) {
  const normalized = useMemo(() => normalizeAgreement(agreement), [agreement]);

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

  const { breakdown, classifiedCount, agreementRate } = normalized;
  const hasBreakdown = classifiedCount > 0;

  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">Policy / ML Decision Agreement</h3>
          <p className="text-xs text-slate-500">Alignment between statistical ML advisory and deterministic safety gates.</p>
        </div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-indigo-50 text-indigo-700 font-semibold text-xs rounded-md border border-indigo-200">
          <Sparkles size={13} />
          <span>{agreementRate === null ? 'Agreement: Not available' : `Agreement: ${formatPercentage(agreementRate)}`}</span>
        </div>
      </div>

      {!hasBreakdown ? (
        <div className="mb-4 p-4 rounded-lg border border-dashed border-slate-200 bg-slate-50 text-sm text-slate-600">
          <div className="flex items-start gap-2">
            <ShieldAlert size={16} className="text-slate-500 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-slate-900">No classified policy/ML decisions in the returned breakdown.</p>
              <p className="mt-1 text-xs leading-relaxed">
                The aggregate agreement rate may be available, but this panel will not invent category counts. Once decision-audit records are classified, the four quadrants will populate automatically.
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
          <div className="p-3.5 rounded-lg bg-emerald-50/70 border border-emerald-200/80">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-bold text-emerald-950 flex items-center gap-1.5"><CheckCircle2 size={14} className="text-emerald-600" /><span>Concurrence: Both Allow</span></span>
              <span className="font-mono font-bold text-emerald-800 text-sm">{formatCount(breakdown.both_allow)}</span>
            </div>
            <p className="text-[11px] text-emerald-800/80 leading-relaxed">Policy permitted recovery and ML scored a positive recovery recommendation.</p>
          </div>

          <div className="p-3.5 rounded-lg bg-slate-100 border border-slate-200">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5"><ShieldAlert size={14} className="text-slate-600" /><span>Concurrence: Both Block</span></span>
              <span className="font-mono font-bold text-slate-800 text-sm">{formatCount(breakdown.both_block)}</span>
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed">Both systems blocked the recovery recommendation.</p>
          </div>

          <div className="p-3.5 rounded-lg bg-rose-50/70 border border-rose-200/80">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-bold text-rose-950 flex items-center gap-1.5"><ShieldAlert size={14} className="text-rose-600" /><span>Safety Interventions</span></span>
              <span className="font-mono font-bold text-rose-800 text-sm">{formatCount(breakdown.policy_block_ml_recommend)}</span>
            </div>
            <p className="text-[11px] text-rose-800/80 leading-relaxed">Deterministic policy blocked an ML recovery recommendation.</p>
          </div>

          <div className="p-3.5 rounded-lg bg-amber-50/70 border border-amber-200/80">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-bold text-amber-950 flex items-center gap-1.5"><ShieldCheck size={14} className="text-amber-700" /><span>Cautious Policy Approval</span></span>
              <span className="font-mono font-bold text-amber-800 text-sm">{formatCount(breakdown.policy_allow_ml_hesitant)}</span>
            </div>
            <p className="text-[11px] text-amber-800/80 leading-relaxed">Policy permitted recovery while ML did not recommend it.</p>
          </div>
        </div>
      )}

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
