import React, { useState, useMemo } from 'react';
import { 
  FolderKanban, 
  Search, 
  ChevronRight, 
  Bot, 
  ShieldCheck, 
  ShieldAlert,
  RotateCcw,
  AlertCircle
} from 'lucide-react';
import StatusBadge from '../common/StatusBadge.jsx';
import { TableRowSkeleton } from '../common/LoadingSkeleton.jsx';
import EmptyState from '../common/EmptyState.jsx';
import { formatMinorUnitsToINR } from '../../utils/currency.js';
import { getFailureCategoryLabel, getPolicyActionLabel, formatRelativeTime } from '../../utils/formatting.js';

export default function RecoveryCasesTable({
  cases = [],
  isLoading = false,
  error = null,
  onRetry = () => {},
  onSelectCase = () => {},
  onRunAgent = () => {},
  showSearch = true,
  title = "Recovery Cases",
  subtitle = "Live payment failure classification & recovery status"
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Discover all distinct statuses present in the data to populate the filter dynamically
  const availableStatuses = useMemo(() => {
    const set = new Set();
    cases.forEach(item => {
      if (item.status) set.add(String(item.status).toLowerCase());
    });
    // Ensure primary statuses 'open' and 'recovered' are always available options
    set.add('open');
    set.add('recovered');
    return Array.from(set);
  }, [cases]);

  const filteredCases = useMemo(() => {
    return (cases || []).filter(item => {
      const q = searchTerm.trim().toLowerCase();
      const idStr = String(item.id ?? '');
      const caseCodeStr = String(item.case_code ?? '');
      const paymentIdStr = String(item.payment_id || item.payment?.id || '');
      const failureStr = String(item.failure_category ?? '');

      const matchesSearch = !q ||
        idStr.toLowerCase().includes(q) ||
        `case #${idStr}`.toLowerCase().includes(q) ||
        `#${idStr}`.toLowerCase().includes(q) ||
        caseCodeStr.toLowerCase().includes(q) ||
        paymentIdStr.toLowerCase().includes(q) ||
        failureStr.toLowerCase().includes(q) ||
        getFailureCategoryLabel(failureStr).toLowerCase().includes(q);

      const itemStatus = String(item.status ?? '').toLowerCase();
      const matchesStatus = statusFilter === 'ALL' || itemStatus === statusFilter.toLowerCase();

      return matchesSearch && matchesStatus;
    });
  }, [cases, searchTerm, statusFilter]);

  return (
    <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
      {/* Table Header Controls */}
      <div className="p-5 border-b border-slate-200/80 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">{title}</h3>
          <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>
        </div>

        {showSearch && (
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5">
            <div className="relative">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search case ID, payment ID, or failure..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full sm:w-64 pl-9 pr-3 py-1.5 text-xs rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all font-sans"
              />
            </div>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="text-xs rounded-lg border border-slate-300 bg-slate-50/50 px-2.5 py-1.5 text-slate-700 font-medium focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 cursor-pointer"
            >
              <option value="ALL">All Statuses</option>
              {availableStatuses.map(st => (
                <option key={st} value={st}>
                  {st.charAt(0).toUpperCase() + st.slice(1)}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Backend Error State */}
      {error && (
        <div className="p-6 bg-rose-50/60 border-b border-rose-100 flex items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2 text-rose-800 font-medium">
            <AlertCircle size={16} className="text-rose-600 shrink-0" />
            <span>Backend communication issue: {error}</span>
          </div>
          <button
            onClick={onRetry}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-white text-rose-700 border border-rose-200 font-semibold hover:bg-rose-50 cursor-pointer shadow-2xs"
          >
            <RotateCcw size={12} />
            <span>Retry</span>
          </button>
        </div>
      )}

      {/* Table Loading State */}
      {isLoading ? (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200/80 text-slate-500 uppercase tracking-wider font-semibold">
              <tr>
                <th className="py-3 px-4">Case</th>
                <th className="py-3 px-4">Payment</th>
                <th className="py-3 px-4">Failure</th>
                <th className="py-3 px-4">Amount at Risk</th>
                <th className="py-3 px-4">Recovered</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Attempts</th>
                <th className="py-3 px-4">Policy Action</th>
                <th className="py-3 px-4">Updated</th>
                <th className="py-3 px-4 text-right">Details</th>
              </tr>
            </thead>
            <tbody>
              {Array.from({ length: 5 }).map((_, i) => (
                <TableRowSkeleton key={i} columns={10} />
              ))}
            </tbody>
          </table>
        </div>
      ) : cases.length === 0 ? (
        /* State 1: Genuinely no backend cases */
        <div className="p-8">
          <EmptyState
            icon={FolderKanban}
            title="No recovery cases available"
            description="Recovery case data will appear here when payment failure events are ingested from the FastAPI backend."
          />
        </div>
      ) : filteredCases.length === 0 ? (
        /* State 2: Cases exist, but search / filter matched nothing */
        <div className="p-8">
          <EmptyState
            icon={Search}
            title="No matching recovery cases"
            description={`No recovery cases match your search query "${searchTerm}" or the selected status filter.`}
          />
        </div>
      ) : (
        /* Render Real Cases Table */
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-slate-50/80 border-b border-slate-200/80 text-slate-500 uppercase tracking-wider font-semibold">
              <tr>
                <th className="py-3 px-4">Case</th>
                <th className="py-3 px-4">Payment</th>
                <th className="py-3 px-4">Failure</th>
                <th className="py-3 px-4">Amount at Risk</th>
                <th className="py-3 px-4">Recovered</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Attempts</th>
                <th className="py-3 px-4">Policy Action</th>
                <th className="py-3 px-4">Updated</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-normal">
              {filteredCases.map((item) => {
                const caseDisplay = item.case_code || `Case #${item.id}`;
                const paymentId = item.payment_id || item.payment?.id || '—';
                const atRisk = item.amount_at_risk_minor ?? item.amount_at_risk ?? 0;
                const recoveredAmt = item.amount_recovered ?? item.amount_recovered_minor ?? 0;
                const attemptsUsed = item.attempts ?? 0;
                const maxAttempts = 2;
                const policyAction = item.policy?.action || item.policy?.recommended_action || item.policy_action || item.action || 'payment_link';
                const isEligible = (item.policy?.eligible ?? (item.status === 'open')) && item.status !== 'recovered';

                return (
                  <tr
                    key={item.id}
                    onClick={() => onSelectCase(item)}
                    className="hover:bg-slate-50/80 transition-colors cursor-pointer group"
                  >
                    {/* 1. Case */}
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-900 whitespace-nowrap">
                      <span className="text-indigo-600 group-hover:underline">
                        {caseDisplay}
                      </span>
                    </td>

                    {/* 2. Payment */}
                    <td className="py-3.5 px-4 font-mono text-slate-600 max-w-[140px] truncate" title={paymentId}>
                      {paymentId}
                    </td>

                    {/* 3. Failure */}
                    <td className="py-3.5 px-4 text-slate-700 font-medium whitespace-nowrap">
                      {getFailureCategoryLabel(item.failure_category)}
                    </td>

                    {/* 4. Amount at Risk */}
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-900 whitespace-nowrap">
                      {formatMinorUnitsToINR(atRisk)}
                    </td>

                    {/* 5. Recovered */}
                    <td className="py-3.5 px-4 font-mono font-semibold text-emerald-700 whitespace-nowrap">
                      {recoveredAmt > 0 ? formatMinorUnitsToINR(recoveredAmt) : '—'}
                    </td>

                    {/* 6. Status */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <StatusBadge status={item.status} size="xs" />
                    </td>

                    {/* 7. Attempts */}
                    <td className="py-3.5 px-4 font-mono text-slate-700 whitespace-nowrap">
                      <span className={`px-1.5 py-0.5 rounded text-[11px] font-semibold ${
                        attemptsUsed >= maxAttempts 
                          ? 'bg-rose-50 text-rose-700 border border-rose-200' 
                          : 'bg-slate-100 text-slate-700'
                      }`}>
                        {attemptsUsed} / {maxAttempts}
                      </span>
                    </td>

                    {/* 8. Policy Action */}
                    <td className="py-3.5 px-4 text-slate-600 whitespace-nowrap">
                      {getPolicyActionLabel(policyAction)}
                    </td>

                    {/* 9. Updated */}
                    <td className="py-3.5 px-4 text-[11px] text-slate-400 font-mono whitespace-nowrap">
                      {formatRelativeTime(item.updated_at || item.created_at)}
                    </td>

                    {/* 10. Action / Inspect */}
                    <td className="py-3.5 px-4 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                        {isEligible && attemptsUsed < maxAttempts ? (
                          <button
                            onClick={() => onRunAgent(item)}
                            className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-indigo-600 text-white font-medium text-xs hover:bg-indigo-700 shadow-2xs transition-colors cursor-pointer"
                            title="Execute bounded recovery agent"
                          >
                            <Bot size={12} />
                            <span>Run Agent</span>
                          </button>
                        ) : (
                          <button
                            onClick={() => onSelectCase(item)}
                            className="inline-flex items-center gap-1 text-slate-400 hover:text-slate-700 text-xs font-medium cursor-pointer"
                          >
                            <span>Inspect</span>
                            <ChevronRight size={14} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
