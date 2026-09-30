import React from 'react';
import MLEvaluationCards from '../components/ml/MLEvaluationCards.jsx';
import ProbabilityBucketChart from '../components/ml/ProbabilityBucketChart.jsx';
import PolicyAgreementMatrix from '../components/ml/PolicyAgreementMatrix.jsx';
import MetricCard from '../components/common/MetricCard.jsx';
import { formatCount, formatPercentage } from '../utils/currency.js';
import { Sparkles, BrainCircuit, CheckCircle2, ShieldCheck, Activity } from 'lucide-react';

export default function MLMonitoringPage({
  metrics = null,
  evaluation = null,
  buckets = [],
  agreement = null,
  isLoading = false,
}) {
  const predictionCount = metrics?.ml_predictions || metrics?.total_cases || 0;
  const outcomesCount = metrics?.ml_outcomes_recorded || metrics?.recovered_cases || 0;
  const agreementRate = metrics?.ml_policy_agreement_rate || agreement?.agreement_rate || 0;
  const outcomeCoverage = predictionCount > 0 ? outcomesCount / predictionCount : 0;

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">
            ML Intelligence & Model Evaluation
          </h1>
          <span className="px-2 py-0.5 text-xs font-semibold bg-indigo-50 text-indigo-700 rounded border border-indigo-200">
            Advisory Monitoring
          </span>
        </div>
        <p className="text-xs sm:text-sm text-slate-500 mt-0.5 max-w-2xl">
          Real-time telemetry measuring machine learning inference performance, probability calibration, and safety alignment.
        </p>
      </div>

      {/* 4 Summary Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="ML Predictions"
          value={formatCount(predictionCount)}
          subtext="Total recovery probability inferences"
          icon={Sparkles}
          variant="indigo"
        />

        <MetricCard
          label="Outcomes Recorded"
          value={formatCount(outcomesCount)}
          subtext="Ground-truth verified outcomes"
          icon={CheckCircle2}
          variant="emerald"
        />

        <MetricCard
          label="Policy/ML Agreement"
          value={formatPercentage(agreementRate)}
          subtext="Alignment with deterministic policy"
          icon={ShieldCheck}
          variant="default"
        />

        <MetricCard
          label="Outcome Coverage"
          value={formatPercentage(outcomeCoverage)}
          subtext="Inferences with closed feedback loops"
          icon={Activity}
          variant="amber"
        />
      </div>

      {/* Model Evaluation & Performance */}
      <MLEvaluationCards evaluation={evaluation} isLoading={isLoading} />

      {/* Probability Calibration Distribution Chart */}
      <ProbabilityBucketChart buckets={buckets} isLoading={isLoading} />

      {/* Policy Agreement Matrix */}
      <PolicyAgreementMatrix agreement={agreement} isLoading={isLoading} />
    </div>
  );
}
