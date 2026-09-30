import React from 'react';
import { formatPercentage, formatCount } from '../../utils/currency.js';
import { formatTimestamp } from '../../utils/formatting.js';
import { BrainCircuit, Info } from 'lucide-react';

function hasMetric(value) {
  return value !== null && value !== undefined && Number.isFinite(Number(value));
}

function formatDecimal(value, digits = 3) {
  return hasMetric(value) ? Number(value).toFixed(digits) : 'N/A';
}

function metricAvailability(value, unavailableReason) {
  return hasMetric(value) ? unavailableReason.available : unavailableReason.missing;
}

export default function MLEvaluationCards({ evaluation = null, isLoading = false }) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="bg-white p-4 rounded-xl border border-slate-200/80 h-24 animate-pulse">
            <div className="h-3 w-16 bg-slate-200 rounded mb-2" />
            <div className="h-6 w-12 bg-slate-100 rounded" />
          </div>
        ))}
      </div>
    );
  }

  if (!evaluation) {
    return (
      <div className="p-6 bg-white rounded-xl border border-slate-200/80 text-center text-xs text-slate-500">
        ML model evaluation metrics are not available from the backend yet.
      </div>
    );
  }

  // The backend currently exposes `f1`; older frontend code expected `f1_score`.
  // Prefer the canonical backend field while remaining compatible with both shapes.
  const f1 = evaluation.f1 ?? evaluation.f1_score;
  const rocAuc = evaluation.roc_auc;
  const brier = evaluation.brier_score;

  const metrics = [
    {
      label: 'ROC-AUC',
      value: formatDecimal(rocAuc),
      sub: hasMetric(rocAuc) ? 'Discrimination' : 'Requires both outcome classes',
      unavailable: !hasMetric(rocAuc),
    },
    {
      label: 'Precision',
      value: hasMetric(evaluation.precision) ? formatPercentage(evaluation.precision) : 'N/A',
      sub: hasMetric(evaluation.precision) ? 'Positive predictive value' : 'Not available',
      unavailable: !hasMetric(evaluation.precision),
    },
    {
      label: 'Recall',
      value: hasMetric(evaluation.recall) ? formatPercentage(evaluation.recall) : 'N/A',
      sub: hasMetric(evaluation.recall) ? 'Sensitivity' : 'Not available',
      unavailable: !hasMetric(evaluation.recall),
    },
    {
      label: 'F1 Score',
      value: formatDecimal(f1),
      sub: hasMetric(f1) ? 'Precision/recall balance' : 'Not available',
      unavailable: !hasMetric(f1),
    },
    {
      label: 'Accuracy',
      value: hasMetric(evaluation.accuracy) ? formatPercentage(evaluation.accuracy) : 'N/A',
      sub: hasMetric(evaluation.accuracy) ? 'Classification accuracy' : 'Not available',
      unavailable: !hasMetric(evaluation.accuracy),
    },
    {
      label: 'Brier Score',
      value: formatDecimal(brier),
      sub: hasMetric(brier) ? 'Probability calibration' : 'Not reported by evaluator',
      unavailable: !hasMetric(brier),
    },
  ];

  const verifiedOutcomes = Number(evaluation.samples_evaluated ?? evaluation.total_predictions ?? 0);
  const hasBothClasses = hasMetric(rocAuc);
  const unavailableCount = metrics.filter((metric) => metric.unavailable).length;

  return (
    <div className="space-y-4">
      <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-700 flex items-center justify-center">
            <BrainCircuit size={18} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-900">ML Prediction</span>
              <span className="text-[10px] font-semibold bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded border border-indigo-200">
                Advisory Monitoring
              </span>
            </div>
            <span className="text-[11px] text-slate-500">
              {verifiedOutcomes > 0
                ? `${formatCount(verifiedOutcomes)} verified outcomes evaluated`
                : 'Limited verified ground truth (telemetry collecting in real time)'}
            </span>
          </div>
        </div>
        {evaluation.last_evaluated && (
          <div className="text-[11px] text-slate-400 font-mono">
            Last evaluated: {formatTimestamp(evaluation.last_evaluated)}
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {metrics.map((m) => (
          <div key={m.label} className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs min-w-0">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">
              {m.label}
            </span>
            <span className={`text-xl font-bold font-mono block mb-0.5 ${m.unavailable ? 'text-slate-500' : 'text-slate-900'}`}>
              {m.value}
            </span>
            <span className="text-[10px] text-slate-400 block leading-tight min-h-[24px]">
              {m.sub}
            </span>
          </div>
        ))}
      </div>

      <div className="flex items-start gap-2 px-1 text-[11px] text-slate-500 font-medium">
        <Info size={14} className="text-slate-400 shrink-0 mt-0.5" />
        <span>
          Metrics reflect verified outcomes from closed payment feedback loops.
          {unavailableCount > 0 && (
            <> Some metrics remain unavailable until the evaluator has the required outcome data.</>
          )}
        </span>
      </div>

      {!hasBothClasses && verifiedOutcomes > 0 && (
        <div className="px-3 py-2.5 rounded-lg border border-amber-200 bg-amber-50/60 text-[11px] text-amber-800">
          <span className="font-semibold">Evaluation coverage note:</span> ROC-AUC requires both recovered and unrecovered outcomes. The current verified set does not yet provide both classes.
        </div>
      )}

      {evaluation.features_importance && evaluation.features_importance.length > 0 && (
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-2xs">
          <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3">
            Top Predictive Signals (Feature Weights)
          </h4>
          <div className="space-y-2.5">
            {evaluation.features_importance.map((f, i) => (
              <div key={i} className="text-xs">
                <div className="flex justify-between text-slate-700 font-medium mb-1">
                  <span className="font-mono text-[11px] text-slate-600">{f.feature}</span>
                  <span className="font-mono font-semibold">{formatPercentage(f.importance)}</span>
                </div>
                <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-indigo-500 rounded-full"
                    style={{ width: `${Math.min(100, f.importance * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
