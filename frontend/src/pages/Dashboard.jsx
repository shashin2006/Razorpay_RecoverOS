import React from 'react';
import { 
  AlertTriangle, 
  CheckCircle2, 
  TrendingUp, 
  FolderKanban, 
  Sparkles,
  ShieldCheck,
  RotateCcw,
  ArrowRight
} from 'lucide-react';
import MetricCard from '../components/common/MetricCard.jsx';
import RecoveryPerformance from '../components/dashboard/RecoveryPerformance.jsx';
import RecoveryHealth from '../components/dashboard/RecoveryHealth.jsx';
import RecoveryCasesTable from '../components/dashboard/RecoveryCasesTable.jsx';
import ErrorState from '../components/common/ErrorState.jsx';
import { MetricCardSkeleton } from '../components/common/LoadingSkeleton.jsx';
import { formatMinorUnitsToINR, formatPercentage, formatCount } from '../utils/currency.js';

export default function Dashboard({
  metrics = null,
  cases = [],
  isLoading = false,
  error = null,
  onRetry = () => {},
  onSelectCase = () => {},
  onRunAgent = () => {},
  onNavigateTab = () => {},
  isMockMode = false,
}) {
  const atRiskMinor = metrics?.total_amount_at_risk_minor ?? 0;
  const recoveredMinor = metrics?.total_amount_recovered_minor ?? 0;
  const recoveryRate = metrics?.amount_recovery_rate ?? (atRiskMinor > 0 ? recoveredMinor / atRiskMinor : 0);
  const totalCases = metrics?.total_cases ?? cases.length;

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* Demo / Mock Warning Banner if explicit mock mode is active */}
      {isMockMode && (
        <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 flex items-start justify-between gap-3 text-xs shadow-2xs">
          <div className="flex items-start gap-2">
            <Sparkles size={16} className="text-amber-600 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold">Simulated Telemetry Mode: </span>
              Displaying demo datasets. Set <code className="font-mono bg-amber-100 px-1 py-0.5 rounded text-amber-950">VITE_USE_MOCK_DATA=false</code> to connect exclusively to the live FastAPI backend.
            </div>
          </div>
        </div>
      )}

      {/* Main Error Banner if API failed */}
      {error && !isMockMode && (
        <ErrorState
          title="Backend Telemetry Offline"
          message={`Unable to load recovery metrics from ${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'}. Ensure the FastAPI server is running.`}
          onRetry={onRetry}
        />
      )}

      {/* 4 PRIMARY KPI METRIC CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {isLoading ? (
          <>
            <MetricCardSkeleton />
            <MetricCardSkeleton />
            <MetricCardSkeleton />
            <MetricCardSkeleton />
          </>
        ) : (
          <>
            {/* 1. Revenue at Risk */}
            <MetricCard
              label="Revenue at Risk"
              value={formatMinorUnitsToINR(atRiskMinor)}
              subtext="Unsettled payment failure volume"
              icon={AlertTriangle}
              variant="default"
            />

            {/* 2. Revenue Recovered */}
            <MetricCard
              label="Revenue Recovered"
              value={formatMinorUnitsToINR(recoveredMinor)}
              subtext="Verified captured recovery volume"
              icon={CheckCircle2}
              variant="emerald"
            />

            {/* 3. Amount Recovery Rate */}
            <MetricCard
              label="Amount Recovery Rate"
              value={formatPercentage(recoveryRate)}
              subtext="Efficiency vs total at-risk volume"
              icon={TrendingUp}
              variant="indigo"
            />

            {/* 4. Recovery Cases */}
            <MetricCard
              label="Recovery Cases"
              value={formatCount(totalCases)}
              subtext="Total failure incidents captured"
              icon={FolderKanban}
              variant="default"
            />
          </>
        )}
      </div>

      {/* RECOVERY PERFORMANCE & HEALTH GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RecoveryPerformance metrics={metrics} isLoading={isLoading} />
        </div>
        <div className="lg:col-span-1">
          <RecoveryHealth metrics={metrics} isLoading={isLoading} />
        </div>
      </div>

      {/* RECOVERY CASES SECTION */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900">Recent Recovery Cases</h2>
            <p className="text-xs text-slate-500">Live payment failure classification & recovery status</p>
          </div>
          <button
            onClick={() => onNavigateTab('cases')}
            className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition-colors cursor-pointer"
          >
            <span>View All Cases</span>
            <ArrowRight size={13} />
          </button>
        </div>

        <RecoveryCasesTable
          cases={cases.slice(0, 5)}
          isLoading={isLoading}
          onSelectCase={onSelectCase}
          onRunAgent={onRunAgent}
          showSearch={false}
          title="Active Recovery Incidents"
          subtitle="Showing recent payment failures requiring bounded recovery action."
        />
      </div>

      {/* CORE FINTECH TRUST ARCHITECTURE CALLOUT */}
      <div className="bg-slate-900 text-slate-300 rounded-xl p-6 border border-slate-800 text-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm text-white">RecoveryOS Governance Model</span>
              <span className="bg-indigo-900/60 text-indigo-300 text-[10px] font-mono px-2 py-0.5 rounded border border-indigo-700/60">
                Deterministic
              </span>
            </div>
            <p className="text-slate-400 max-w-2xl leading-relaxed">
              AI recommends. Deterministic policy authorizes. Executor acts. Razorpay processes. Bounded by a strict 2-attempt ceiling.
            </p>
          </div>
          <button
            onClick={() => onNavigateTab('ai-policy')}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs border border-slate-700 transition-colors cursor-pointer shrink-0 self-start md:self-auto"
          >
            <ShieldCheck size={14} className="text-teal-400" />
            <span>Inspect Safety Policy</span>
          </button>
        </div>
      </div>
    </div>
  );
}
