import React, { useState, useEffect } from 'react';
import RecoveryTimeline from '../components/recovery/RecoveryTimeline.jsx';
import EmptyState from '../components/common/EmptyState.jsx';
import { getRecoveryCaseAudit } from '../api/recovery.js';
import { History, ShieldCheck, RotateCcw, AlertCircle } from 'lucide-react';

export default function AuditTrailPage({ cases = [], isLoading = false }) {
  const [selectedCaseId, setSelectedCaseId] = useState(cases[0]?.id || '');
  const [auditEvents, setAuditEvents] = useState([]);
  const [isLoadingAudit, setIsLoadingAudit] = useState(false);
  const [auditError, setAuditError] = useState(null);

  // Default to first case if not set and cases arrive
  useEffect(() => {
    if (!selectedCaseId && cases.length > 0) {
      setSelectedCaseId(String(cases[0].id));
    }
  }, [cases, selectedCaseId]);

  // Fetch real audit events when selectedCaseId changes
  useEffect(() => {
    if (!selectedCaseId) {
      setAuditEvents([]);
      return;
    }

    let isMounted = true;
    const fetchAudit = async () => {
      setIsLoadingAudit(true);
      setAuditError(null);

      try {
        const res = await getRecoveryCaseAudit(selectedCaseId);
        if (isMounted) {
          if (res.ok && res.data) {
            const events = Array.isArray(res.data) 
              ? res.data 
              : (res.data.events || []);
            setAuditEvents(events);
          } else {
            // Check if selected case in props has timeline
            const foundCase = cases.find(c => String(c.id) === String(selectedCaseId));
            if (foundCase?.timeline?.length) {
              setAuditEvents(foundCase.timeline);
            } else {
              setAuditEvents([]);
              if (!res.ok && res.status !== 404) {
                setAuditError(res.error || 'Failed to fetch audit events for this case');
              }
            }
          }
        }
      } catch (err) {
        if (isMounted) {
          setAuditError(err.message || 'Error loading audit timeline');
          setAuditEvents([]);
        }
      } finally {
        if (isMounted) {
          setIsLoadingAudit(false);
        }
      }
    };

    fetchAudit();

    return () => {
      isMounted = false;
    };
  }, [selectedCaseId, cases]);

  const selectedCaseObj = cases.find(c => String(c.id) === String(selectedCaseId));

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">
              Operational Audit Trail
            </h1>
            <span className="px-2 py-0.5 text-xs font-semibold bg-slate-100 text-slate-700 rounded border border-slate-200">
              Immutable History
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            End-to-end chronological timeline of webhooks, policy safety gate evaluations, agent calls, and captured outcomes.
          </p>
        </div>

        {/* Case Filter Selector */}
        {cases.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 font-medium">Select Case:</span>
            <select
              value={selectedCaseId}
              onChange={(e) => setSelectedCaseId(e.target.value)}
              className="text-xs rounded-lg border border-slate-300 bg-white px-3 py-1.5 font-mono text-slate-800 focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 cursor-pointer"
            >
              {cases.map(c => (
                <option key={c.id} value={c.id}>
                  {c.case_code || `Case #${c.id}`} ({c.status})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Audit Pipeline Description Banner */}
      <div className="bg-slate-900 text-slate-300 p-4 rounded-xl border border-slate-800 text-xs flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-slate-200 font-medium">
          <ShieldCheck size={16} className="text-teal-400" />
          <span>Recovery Lifecycle Progression:</span>
        </div>
        <div className="flex flex-wrap items-center gap-2 font-mono text-[11px] text-slate-400">
          <span>Detection</span>
          <span>→</span>
          <span>Intelligence</span>
          <span>→</span>
          <span>Policy</span>
          <span>→</span>
          <span>Execution</span>
          <span>→</span>
          <span className="text-emerald-400 font-bold">Outcome</span>
        </div>
      </div>

      {/* Timeline Container */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-xs">
        {auditError && (
          <div className="mb-4 p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-800 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle size={14} className="text-rose-600" />
              <span>{auditError}</span>
            </div>
          </div>
        )}

        {isLoading || isLoadingAudit ? (
          <div className="space-y-4 animate-pulse">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-16 bg-slate-100 rounded-lg" />
            ))}
          </div>
        ) : cases.length === 0 ? (
          <EmptyState
            icon={History}
            title="No recovery cases available"
            description="Audit events will appear once recovery cases exist in the backend."
          />
        ) : auditEvents.length === 0 ? (
          <EmptyState
            icon={History}
            title="No audit events recorded"
            description={`No chronological audit events are currently recorded for ${selectedCaseObj ? (selectedCaseObj.case_code || `Case #${selectedCaseObj.id}`) : 'this case'}.`}
          />
        ) : (
          <div className="space-y-2">
            <div className="mb-4 pb-2 border-b border-slate-100 flex items-center justify-between">
              <div>
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Event Stream: {selectedCaseObj ? (selectedCaseObj.case_code || `Case #${selectedCaseObj.id}`) : `Case #${selectedCaseId}`}
                </h3>
                <p className="text-[11px] text-slate-400">
                  Authoritative chronological events recorded by FastAPI backend
                </p>
              </div>
              <span className="text-slate-500 font-mono text-xs">
                {auditEvents.length} events
              </span>
            </div>
            <RecoveryTimeline timeline={auditEvents} />
          </div>
        )}
      </div>
    </div>
  );
}
