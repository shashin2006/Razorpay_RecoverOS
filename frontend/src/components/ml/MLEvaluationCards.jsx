import React from 'react';
import { formatPercentage, formatCount } from '../../utils/currency.js';
import { formatTimestamp } from '../../utils/formatting.js';
import { Sparkles, BrainCircuit, CheckCircle, BarChart3 } from 'lucide-react';

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

  const metrics = [
    { label: 'ROC-AUC', value: evaluation.roc_auc ? evaluation.roc_auc.toFixed(3) : 'N/A', sub: 'Discrimination score' },
    { label: 'Precision', value: formatPercentage(evaluation.precision), sub: 'Positive predictive' },
    { label: 'Recall', value: formatPercentage(evaluation.recall), sub: 'Sensitivity rate' },
    { label: 'F1 Score', value: evaluation.f1_score ? evaluation.f1_score.toFixed(3) : 'N/A', sub: 'Harmonic mean' },
    { label: 'Accuracy', value: formatPercentage(evaluation.accuracy), sub: 'Overall fidelity' },
    { label: 'Brier Score', value: evaluation.brier_score !== undefined ? evaluation.brier_score.toFixed(3) : 'N/A', sub: 'Calibration error' },
  ];

  return (
    <div className="space-y-4">
      {/* Model metadata banner */}
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
              {evaluation.samples_evaluated && evaluation.samples_evaluated > 0
                ? `${formatCount(evaluation.samples_evaluated)} verified outcomes evaluated`
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

      {/* 6 Core Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {metrics.map((m, idx) => (
          <div key={idx} className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">
              {m.label}
            </span>
            <span className="text-xl font-bold font-mono text-slate-900 block mb-0.5">
              {m.value}
            </span>
            <span className="text-[10px] text-slate-400 block truncate">
              {m.sub}
            </span>
          </div>
        ))}
      </div>

      {/* Contextual Note on Limited Sample Set */}
      <div className="text-[11px] text-slate-500 flex items-center gap-1.5 px-1 font-medium">
        <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 shrink-0" />
        <span>Metrics reflect available verified outcomes from closed payment feedback loops.</span>
      </div>

      {/* Feature Importance if provided */}
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
