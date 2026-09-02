import React, { useState, useEffect } from 'react';
import { 
  X, 
  Bot, 
  ShieldCheck, 
  ShieldAlert, 
  CreditCard, 
  Sparkles, 
  Clock, 
  ExternalLink, 
  Copy, 
  Check, 
  ChevronDown, 
  ChevronUp,
  FileCode2,
  AlertTriangle,
  RotateCcw,
  CheckCircle2,
  FileSearch,
  Zap,
  Activity
} from 'lucide-react';
import StatusBadge from '../common/StatusBadge.jsx';
import RecoveryTimeline from './RecoveryTimeline.jsx';
import { getRecoveryCaseById, getRecoveryCaseAudit } from '../../api/recovery.js';
import { formatMinorUnitsToINR, formatPercentage } from '../../utils/currency.js';
import { 
  getFailureCategoryLabel, 
  getPolicyActionLabel, 
  formatTimestamp,
  normalizeCase
} from '../../utils/formatting.js';

export default function RecoveryCaseDrawer({
  recoveryCase = null,
  isOpen = false,
  onClose = () => {},
  onRunAgent = () => {},
  isExecuting = false
}) {
  const [caseDetail, setCaseDetail] = useState(null);
  const [auditEvents, setAuditEvents] = useState([]);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [errorDetail, setErrorDetail] = useState(null);
  const [copiedLink, setCopiedLink] = useState(false);
  const [showRawJson, setShowRawJson] = useState(false);

  // Fetch full case detail and audit events on open or ID change
  useEffect(() => {
    if (!isOpen || !recoveryCase?.id) {
      setCaseDetail(null);
      setAuditEvents([]);
      return;
    }

    let isMounted = true;
    const fetchFullData = async () => {
      setIsLoadingDetail(true);
      setErrorDetail(null);

      try {
        // Fetch case detail: GET /api/recovery/cases/{id}
        const detailRes = await getRecoveryCaseById(recoveryCase.id);
        if (isMounted) {
          if (detailRes.ok && detailRes.data) {
            setCaseDetail(detailRes.data);
          } else {
            // Fallback to initial row data if detail endpoint fails
            setCaseDetail(recoveryCase);
            setErrorDetail(detailRes.error || 'Failed to fetch fresh case details from backend');
          }
        }

        // Fetch audit events: GET /api/recovery/cases/{id}/audit
        const auditRes = await getRecoveryCaseAudit(recoveryCase.id);
        if (isMounted) {
          if (auditRes.ok && auditRes.data) {
            const events = Array.isArray(auditRes.data) 
              ? auditRes.data 
              : (auditRes.data.events || []);
            setAuditEvents(events);
          } else {
            setAuditEvents(recoveryCase.timeline || []);
          }
        }
      } catch (err) {
        if (isMounted) {
          setErrorDetail(err.message || 'Error fetching case data');
          setCaseDetail(recoveryCase);
        }
      } finally {
        if (isMounted) {
          setIsLoadingDetail(false);
        }
      }
    };

    fetchFullData();

    return () => {
      isMounted = false;
    };
  }, [isOpen, recoveryCase?.id]);

  if (!isOpen || !recoveryCase) return null;

  // Normalize caseDetail or fallback recoveryCase to guarantee consistent properties and .id
  const normCase = normalizeCase(caseDetail || recoveryCase) || recoveryCase;
  const d = normCase;

  // Helper for displaying values with "Not recorded" fallback
  const renderVal = (val, formatter = null) => {
    if (val === null || val === undefined || val === '') {
      return <span className="text-slate-400 font-mono text-[11px]">Not recorded</span>;
    }
    return formatter ? formatter(val) : String(val);
  };

  // Field derivations based on real backend response schema
  const statusVal = d.status ?? null;
  const atRiskMinor = d.amount_at_risk_minor ?? d.amount_at_risk ?? null;
  const recoveredMinor = d.amount_recovered_minor ?? d.amount_recovered ?? 0;
  const attempts = d.attempts ?? 0;
  const maxAttempts = d.policy?.max_attempts ?? d.policy?.max_automated_attempts ?? d.max_attempts ?? 2;

  // PAYMENT SECTION
  const paymentObj = d.payment;
  const paymentId = paymentObj?.payment_id || paymentObj?.id || d.payment_id || null;
  const paymentStatus = paymentObj?.status || d.payment_status || null;
  const paymentMethod = paymentObj?.method || d.payment_method || null;
  const failureReason = paymentObj?.failure_reason || d.failure_reason || d.failure_category || null;
  const failureSource = paymentObj?.failure_source || d.failure_source || null;
  const errorStep = paymentObj?.error_step || d.error_step || null;

  // POLICY DECISION SECTION
  const policyObj = d.policy;
  const policyEligible = policyObj?.eligible ?? d.is_eligible ?? d.eligible ?? null;
  const policyAction = policyObj?.action || policyObj?.recommended_action || d.policy_action || null;
  const policyMaxAttempts = policyObj?.max_attempts ?? policyObj?.max_automated_attempts ?? d.max_attempts ?? 2;
  const policyCooldown = policyObj?.cooldown_period_minutes ?? policyObj?.cooldown ?? d.cooldown ?? null;
  const policyReason = policyObj?.reason || d.policy_reason || null;

  // ML ADVISORY SECTION
  const mlObj = d.ml;
  const mlProb = mlObj?.recovery_probability ?? d.recovery_probability ?? null;
  const mlThreshold = mlObj?.threshold ?? d.threshold ?? null;
  const mlRecommendation = mlObj?.recommendation || d.ml_recommendation || null;
  const mlModelVersion = mlObj?.model_version || d.model_version || null;
  const mlMode = mlObj?.mode || d.mode || null;

  // DECISION AUDIT SECTION
  const auditObj = d.decision_audit;
  const auditMlProb = auditObj?.ml_probability ?? mlProb;
  const auditMlThreshold = auditObj?.ml_threshold ?? mlThreshold;
  const auditMlRecommendation = auditObj?.ml_recommendation || mlRecommendation;
  const auditPolicyAction = auditObj?.policy_action || policyAction;
  const auditAgreement = auditObj?.agreement ?? d.agreement ?? null;

  // RECOVERY ACTION SECTION
  const actionObj = d.recovery_action || d.execution;
  const recoveryActionName = actionObj?.action || d.action || null;
  const recoveryAttempt = actionObj?.attempt ?? attempts;
  const recoveryActionStatus = actionObj?.status || d.action_status || null;
  const recoveryExternalId = actionObj?.external_id || actionObj?.payment_link_id || d.payment_link_id || null;
  const recoveryPaymentLink = actionObj?.payment_link || actionObj?.payment_link_url || d.payment_link_url || null;

  const isEligibleForAction = (policyEligible === true || statusVal === 'open') && statusVal !== 'recovered' && attempts < maxAttempts;

  const handleCopyLink = () => {
    if (!recoveryPaymentLink) return;
    navigator.clipboard.writeText(recoveryPaymentLink);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-950/40 backdrop-blur-xs animate-in fade-in duration-150">
      <div 
        className="absolute inset-y-0 right-0 max-w-xl w-full bg-white shadow-2xl border-l border-slate-200 flex flex-col animate-in slide-in-from-right duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Drawer Header */}
        <div className="p-5 border-b border-slate-200/80 bg-slate-50/70 flex items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="font-mono text-sm font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200/60">
                {d.case_code || `Case #${d.id}`}
              </span>
              <StatusBadge status={statusVal} size="sm" />
            </div>
            <h2 className="text-lg font-bold text-slate-900 tracking-tight">
              Case Inspection & Decision Audit
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Created {formatTimestamp(d.created_at)}
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-200/60 transition-colors cursor-pointer"
            aria-label="Close drawer"
          >
            <X size={18} />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-5 space-y-6 text-xs">
          {isLoadingDetail && (
            <div className="p-3 bg-indigo-50 border border-indigo-100 rounded-lg flex items-center gap-2 text-indigo-700 text-xs animate-pulse">
              <RotateCcw size={13} className="animate-spin" />
              <span>Fetching authoritative case detail & audit events from backend...</span>
            </div>
          )}

          {errorDetail && (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-800 text-xs flex items-start gap-2">
              <AlertTriangle size={14} className="text-rose-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold">Backend Notice: </span>
                <span>{errorDetail}</span>
              </div>
            </div>
          )}

          {/* 1. STATUS & CORE RECOVERY OVERVIEW */}
          <div className="bg-slate-50/80 rounded-xl p-4 border border-slate-200/80 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-200/60">
              <span className="font-bold text-slate-900 text-xs uppercase tracking-wider">
                Status & Recovery Volume
              </span>
              <span className="font-mono text-slate-500 text-[11px]">
                {d.currency || 'INR'}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <span className="text-slate-500 block text-[11px]">Amount at Risk</span>
                <span className="text-lg font-mono font-bold text-slate-900">
                  {atRiskMinor !== null ? formatMinorUnitsToINR(atRiskMinor, { showDecimals: true }) : renderVal(null)}
                </span>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px]">Amount Recovered</span>
                <span className="text-lg font-mono font-bold text-emerald-700">
                  {formatMinorUnitsToINR(recoveredMinor, { showDecimals: true })}
                </span>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-200/60 flex items-center justify-between">
              <div>
                <span className="text-slate-500 block text-[11px]">Attempts</span>
                <span className={`font-mono font-bold text-sm ${attempts >= maxAttempts ? 'text-rose-600' : 'text-slate-800'}`}>
                  {attempts} / 2 (Max Limit: 2)
                </span>
              </div>
              <div>
                <span className="text-slate-500 block text-[11px] text-right">Case Status</span>
                <StatusBadge status={statusVal} size="xs" />
              </div>
            </div>
          </div>

          {/* 2. PAYMENT */}
          <div className="bg-white rounded-xl p-4 border border-slate-200/80 shadow-2xs space-y-2.5">
            <div className="flex items-center justify-between pb-1 border-b border-slate-100">
              <div className="flex items-center gap-1.5 text-slate-900 font-bold text-xs uppercase tracking-wider">
                <CreditCard size={14} className="text-slate-600" />
                <span>Payment Details</span>
              </div>
              {!paymentObj && !paymentId && (
                <span className="text-[10px] text-amber-700 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded font-medium">
                  Not Linked
                </span>
              )}
            </div>

            {!paymentObj && !paymentId ? (
              <div className="p-3 bg-slate-50/80 rounded-lg border border-slate-200/60 text-slate-500 text-xs text-center font-medium">
                Payment record not linked
              </div>
            ) : (
              <div className="space-y-2">
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Razorpay Payment ID</span>
                  <span className="font-mono font-semibold text-slate-800">{renderVal(paymentId)}</span>
                </div>

                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Payment Status</span>
                  <span className="font-medium text-slate-800 capitalize">{renderVal(paymentStatus)}</span>
                </div>

                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Payment Method</span>
                  <span className="font-medium text-slate-800 capitalize">{renderVal(paymentMethod)}</span>
                </div>

                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Failure Reason</span>
                  <span className="font-medium text-slate-800">{renderVal(failureReason, getFailureCategoryLabel)}</span>
                </div>

                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Failure Source</span>
                  <span className="font-mono text-slate-800">{renderVal(failureSource)}</span>
                </div>

                <div className="flex justify-between py-1">
                  <span className="text-slate-500">Error Step</span>
                  <span className="font-mono text-slate-800">{renderVal(errorStep)}</span>
                </div>
              </div>
            )}
          </div>

          {/* 3. CURRENT POLICY DECISION */}
          <div className="bg-white rounded-xl p-4 border border-slate-200/80 shadow-2xs space-y-2.5">
            <div className="flex items-center justify-between pb-1 border-b border-slate-100">
              <div className="flex items-center gap-1.5 text-slate-900 font-bold text-xs uppercase tracking-wider">
                <ShieldCheck size={14} className="text-teal-600" />
                <span>Current Deterministic Policy</span>
              </div>
              <span className="text-[10px] font-semibold text-teal-800 bg-teal-50 px-2 py-0.5 rounded border border-teal-200">
                Authoritative
              </span>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Policy Status</span>
                <span className="font-semibold">
                  {statusVal === 'recovered' ? (
                    <span className="text-slate-700">No further action (Case Recovered)</span>
                  ) : policyEligible !== null ? (
                    policyEligible ? (
                      <span className="text-teal-700">Eligible (Approved)</span>
                    ) : (
                      <span className="text-rose-700">Blocked (Ceiling / Risk)</span>
                    )
                  ) : renderVal(null)}
                </span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Action</span>
                <span className="font-semibold text-slate-800">
                  {statusVal === 'recovered' ? 'No further action' : renderVal(policyAction, getPolicyActionLabel)}
                </span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Maximum Attempts</span>
                <span className="font-mono font-semibold text-slate-800">
                  {policyMaxAttempts !== null ? `${policyMaxAttempts} (Hard Ceiling)` : renderVal(null)}
                </span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Cooldown</span>
                <span className="font-mono text-slate-800">
                  {policyCooldown !== null ? `${policyCooldown} mins` : renderVal(null)}
                </span>
              </div>

              <div className="pt-1">
                <span className="text-slate-500 block mb-0.5">Reason:</span>
                <p className="bg-slate-50 p-2 rounded border border-slate-200/60 leading-relaxed text-slate-700">
                  {statusVal === 'recovered' 
                    ? (policyReason || 'Recovery case is not open. Payment already verified.') 
                    : (policyReason || 'Not recorded')}
                </p>
              </div>
            </div>
          </div>

          {/* 4. ML ADVISORY */}
          <div className="bg-white rounded-xl p-4 border border-slate-200/80 shadow-2xs space-y-2.5">
            <div className="flex items-center justify-between pb-1 border-b border-slate-100">
              <div className="flex items-center gap-1.5 text-slate-900 font-bold text-xs uppercase tracking-wider">
                <Sparkles size={14} className="text-indigo-600" />
                <span>ML Advisory</span>
              </div>
              <span className="text-[10px] text-slate-400 font-mono">
                Non-Authoritative
              </span>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Recovery Probability</span>
                <span className="font-mono font-bold text-indigo-900">
                  {mlProb !== null ? formatPercentage(mlProb) : renderVal(null)}
                </span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Threshold</span>
                <span className="font-mono text-slate-800">
                  {mlThreshold !== null ? (typeof mlThreshold === 'number' ? mlThreshold.toFixed(2) : String(mlThreshold)) : renderVal(null)}
                </span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Recommendation</span>
                <span className="font-medium text-slate-800">{renderVal(mlRecommendation, getPolicyActionLabel)}</span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Prediction Version</span>
                <span className="font-mono text-slate-800">{renderVal(mlModelVersion)}</span>
              </div>

              <div className="flex justify-between py-1">
                <span className="text-slate-500">Mode</span>
                <span className="font-mono text-slate-800 capitalize">{renderVal(mlMode)}</span>
              </div>
            </div>
          </div>

          {/* 5. DECISION AUDIT */}
          <div className="bg-white rounded-xl p-4 border border-slate-200/80 shadow-2xs space-y-2.5">
            <div className="flex items-center gap-1.5 text-slate-900 font-bold text-xs uppercase tracking-wider pb-1 border-b border-slate-100">
              <FileSearch size={14} className="text-slate-700" />
              <span>Decision Audit & Agreement</span>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">ML Probability</span>
                <span className="font-mono text-slate-800">{auditMlProb !== null ? formatPercentage(auditMlProb) : renderVal(null)}</span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">ML Threshold</span>
                <span className="font-mono text-slate-800">{auditMlThreshold !== null ? String(auditMlThreshold) : renderVal(null)}</span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">ML Recommendation</span>
                <span className="font-medium text-slate-800">{renderVal(auditMlRecommendation, getPolicyActionLabel)}</span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Policy Action</span>
                <span className="font-medium text-slate-800">{renderVal(auditPolicyAction, getPolicyActionLabel)}</span>
              </div>

              <div className="flex justify-between py-1">
                <span className="text-slate-500">Agreement</span>
                <span className="font-semibold">
                  {auditAgreement !== null ? (
                    auditAgreement ? (
                      <span className="text-emerald-700">Agreement (Aligned)</span>
                    ) : (
                      <span className="text-amber-700">Divergence (Safety Override)</span>
                    )
                  ) : renderVal(null)}
                </span>
              </div>
            </div>
          </div>

          {/* 6. HISTORICAL / CURRENT RECOVERY ACTION */}
          <div className="bg-white rounded-xl p-4 border border-slate-200/80 shadow-2xs space-y-2.5">
            <div className="flex items-center justify-between pb-1 border-b border-slate-100">
              <div className="flex items-center gap-1.5 text-slate-900 font-bold text-xs uppercase tracking-wider">
                <Zap size={14} className="text-amber-600" />
                <span>{statusVal === 'recovered' || recoveryActionStatus === 'executed' ? 'Historical Recovery Action' : 'Recovery Action Execution'}</span>
              </div>
              <span className="text-[10px] text-slate-500 font-mono">
                {statusVal === 'recovered' ? 'Executed Previously' : 'Razorpay Test Mode'}
              </span>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Action</span>
                <span className="font-semibold text-slate-800">{renderVal(recoveryActionName, getPolicyActionLabel)}</span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Attempt</span>
                <span className="font-mono text-slate-800">{recoveryAttempt !== null ? `${recoveryAttempt} of 2` : renderVal(null)}</span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">Status</span>
                <span className="font-medium text-slate-800 capitalize">{renderVal(recoveryActionStatus)}</span>
              </div>

              <div className="flex justify-between py-1 border-b border-slate-100">
                <span className="text-slate-500">External ID</span>
                <span className="font-mono text-slate-800">{renderVal(recoveryExternalId)}</span>
              </div>

              <div>
                <span className="text-slate-500 block mb-1">Payment Link:</span>
                {recoveryPaymentLink ? (
                  <div className="flex items-center gap-2 bg-slate-50 p-2 rounded-lg border border-slate-200 font-mono text-[11px]">
                    <span className="truncate flex-1 text-slate-800">{recoveryPaymentLink}</span>
                    <button
                      onClick={handleCopyLink}
                      className="p-1 rounded hover:bg-slate-200 text-slate-600 transition-colors cursor-pointer"
                      title="Copy link"
                    >
                      {copiedLink ? <Check size={14} className="text-emerald-600" /> : <Copy size={14} />}
                    </button>
                    <a
                      href={recoveryPaymentLink}
                      target="_blank"
                      rel="noreferrer"
                      className="p-1 rounded hover:bg-slate-200 text-indigo-600 transition-colors cursor-pointer"
                      title="Open test payment link"
                    >
                      <ExternalLink size={14} />
                    </a>
                  </div>
                ) : (
                  <span className="text-slate-400 font-mono">Not recorded</span>
                )}
              </div>
            </div>
          </div>

          {/* 7. AUDIT TRAIL */}
          <div className="bg-white rounded-xl p-4 border border-slate-200/80 shadow-2xs space-y-3">
            <div>
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider flex items-center gap-1.5">
                  <Clock size={14} className="text-slate-500" />
                  <span>Audit Trail</span>
                </h4>
                <span className="text-[10px] text-slate-400 font-mono">
                  {auditEvents.length} events
                </span>
              </div>
              <div className="mt-1 text-[10px] text-slate-500 flex flex-wrap items-center gap-1 font-mono">
                <span>Detection</span>
                <span>→</span>
                <span>Intelligence</span>
                <span>→</span>
                <span>Policy</span>
                <span>→</span>
                <span>Execution</span>
                <span>→</span>
                <span className="text-emerald-600 font-bold">Outcome</span>
              </div>
            </div>

            <RecoveryTimeline timeline={auditEvents} />
          </div>

          {/* 8. Raw JSON Developer Diagnostic */}
          <div className="border-t border-slate-200 pt-3">
            <button
              onClick={() => setShowRawJson(!showRawJson)}
              className="flex items-center justify-between w-full text-slate-500 hover:text-slate-800 text-[11px] font-semibold py-1 cursor-pointer"
            >
              <span className="flex items-center gap-1.5">
                <FileCode2 size={13} />
                <span>Developer Diagnostic Details (Raw Case JSON)</span>
              </span>
              {showRawJson ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>

            {showRawJson && (
              <pre className="mt-2 p-3 bg-slate-900 text-slate-200 rounded-lg text-[10px] font-mono overflow-x-auto max-h-60 border border-slate-800">
                {JSON.stringify(d, null, 2)}
              </pre>
            )}
          </div>
        </div>

        {/* Drawer Footer Actions */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between gap-3">
          <div className="text-[11px] text-slate-500">
            {isEligibleForAction ? (
              <span className="text-teal-700 font-medium">Eligible for recovery action ({attempts}/2 attempts)</span>
            ) : (
              <span className="text-slate-500 font-medium">
                {statusVal === 'recovered' ? 'Recovered successfully' : 'Disallowed or max attempts reached'}
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-200/60 rounded-lg transition-colors cursor-pointer"
            >
              Close
            </button>

            {isEligibleForAction && (
              <button
                onClick={() => onRunAgent(normCase)}
                disabled={isExecuting}
                className="inline-flex items-center gap-1.5 px-4 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm transition-all cursor-pointer disabled:opacity-60"
              >
                <Bot size={14} />
                <span>Run Recovery Agent</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
