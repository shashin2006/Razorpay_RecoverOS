import React from 'react';
import RecoveryCasesTable from '../components/dashboard/RecoveryCasesTable.jsx';
import { formatCount } from '../utils/currency.js';
import { FolderKanban, ShieldCheck, Activity, CheckCircle2 } from 'lucide-react';

export default function RecoveryCasesPage({
  cases = [],
  metrics = null,
  isLoading = false,
  error = null,
  onRetry = () => {},
  onSelectCase = () => {},
  onRunAgent = () => {},
}) {
  const total = cases.length;
  const openCount = cases.filter(item => String(item.status).toLowerCase() === 'open').length;
  const recoveredCount = cases.filter(item => String(item.status).toLowerCase() === 'recovered').length;
  
  // Policy eligible: use metrics count if available, or compute from loaded cases
  const eligibleCount = metrics?.policy_eligible_cases ?? 
    cases.filter(item => (item.policy?.eligible === true || item.is_eligible === true || item.status === 'open') && item.status !== 'recovered').length;

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">
          Recovery Cases
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
          Comprehensive inventory of payment failures, policy evaluations, and recovery outcomes.
        </p>
      </div>

      {/* Summary Stat Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {/* Total Cases */}
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-slate-700">
            <FolderKanban size={16} />
          </div>
          <div>
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Total Cases</span>
            <span className="text-lg font-bold font-mono text-slate-900">{formatCount(total)}</span>
          </div>
        </div>

        {/* Policy Eligible */}
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-teal-50 flex items-center justify-center text-teal-700">
            <ShieldCheck size={16} />
          </div>
          <div>
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Policy Eligible</span>
            <span className="text-lg font-bold font-mono text-teal-900">{formatCount(eligibleCount)}</span>
          </div>
        </div>

        {/* Open */}
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center text-blue-700">
            <Activity size={16} />
          </div>
          <div>
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Open</span>
            <span className="text-lg font-bold font-mono text-blue-900">{formatCount(openCount)}</span>
          </div>
        </div>

        {/* Recovered */}
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-700">
            <CheckCircle2 size={16} />
          </div>
          <div>
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Recovered</span>
            <span className="text-lg font-bold font-mono text-emerald-900">{formatCount(recoveredCount)}</span>
          </div>
        </div>
      </div>

      {/* Main Table */}
      <RecoveryCasesTable
        cases={cases}
        isLoading={isLoading}
        error={error}
        onRetry={onRetry}
        onSelectCase={onSelectCase}
        onRunAgent={onRunAgent}
        showSearch={true}
        title="All Recovery Incidents"
        subtitle="Filter by status, failure category, payment ID, or case ID."
      />
    </div>
  );
}
