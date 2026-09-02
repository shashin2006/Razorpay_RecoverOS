import React, { useState } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert,
  Bot, 
  AlertTriangle, 
  X, 
  ArrowRight,
  RotateCcw,
  CheckCircle2,
  ExternalLink,
  Copy,
  Check,
  Zap,
  Lock,
  Sparkles,
  Activity,
  CreditCard,
  Layers
} from 'lucide-react';
import StatusBadge from '../common/StatusBadge.jsx';
import { formatMinorUnitsToINR, formatPercentage } from '../../utils/currency.js';
import { getPolicyActionLabel, getFailureCategoryLabel, normalizeCase } from '../../utils/formatting.js';

export default function AgentConfirmationModal({
  recoveryCase = null,
  isOpen = false,
  isExecuting = false,
  executionError = null,
  executionResult = null,
  onConfirm = () => {},
  onClose = () => {},
  onViewDetails = null
}) {
  const [copiedLink, setCopiedLink] = useState(false);

  if (!isOpen || !recoveryCase) return null;

  // Normalize case object to ensure safe access to all top-level and nested properties
  const c = normalizeCase(recoveryCase) || recoveryCase;

  const attempts = c.attempts ?? 0;
  const maxAttempts = c.max_attempts ?? c.policy?.max_automated_attempts ?? 2;
  const atRisk = c.amount_at_risk_minor ?? c.amount_at_risk ?? 0;
  const failureLabel = getFailureCategoryLabel(
    c.failure_category || 
    c.payment?.failure_reason || 
    'payment_failed'
  );

  const actionKey = c.policy?.recommended_action || 
    c.policy?.action || 
    c.action || 
    'payment_link';
  const actionLabel = getPolicyActionLabel(actionKey);

  // 1. RECOVERY ASSESSMENT (Backend-backed textual reasoning or deterministic fallback)
  const textualAgentReasoning = (
    c.agent_assessment || 
    c.agent?.agent_reasoning || 
    c.agent_reasoning || 
    c.agent?.reasoning || 
    c.assessment || 
    null
  );

  const hasTextualAgentResponse = Boolean(
    textualAgentReasoning && 
    typeof textualAgentReasoning === 'string' && 
    textualAgentReasoning.trim().length > 0
  );

  const assessmentTitle = hasTextualAgentResponse ? 'AGENT ASSESSMENT' : 'RECOVERY ASSESSMENT';
  const assessmentSourceLabel = hasTextualAgentResponse ? 'Source: Recovery Agent' : 'Source: Prediction + Policy';
  const assessmentContent = hasTextualAgentResponse 
    ? textualAgentReasoning 
    : 'Assessment summary is based on the recorded recovery prediction and deterministic policy.';

  // 2. ML ADVISORY DATA (Advisory prediction values only)
  const mlObj = c.ml || c.latest_ml_prediction || {};
  const mlProb = mlObj.recovery_probability ?? c.recovery_probability ?? null;
  const mlRec = mlObj.recommendation || c.ml_recommendation || null;
  const mlMode = mlObj.mode || c.mode || null;

  // 3. DETERMINISTIC POLICY DATA
  const policyObj = c.policy || {};
  const isPolicyEligible = policyObj.eligible ?? c.is_eligible ?? (attempts < maxAttempts);
  const policyDecisionText = policyObj.decision || (isPolicyEligible ? 'Policy Approved' : 'Policy Blocked');
  const policyReason = policyObj.reason || c.policy_reason || (isPolicyEligible ? `Safety checks passed: ${attempts}/${maxAttempts} attempts utilized.` : 'Maximum automated recovery attempts reached or risk threshold exceeded.');
  const cooldownPeriod = policyObj.cooldown_period_minutes ?? policyObj.cooldown ?? c.cooldown ?? 30;

  // 4. EXECUTION OUTCOME DATA EXTRACTION (when executed)
  const resultStatus = executionResult?.status || 
    executionResult?.recovery_action?.status || 
    'executed';
    
  const resultAction = executionResult?.action || 
    executionResult?.recovery_action?.action || 
    c.latest_action?.action ||
    c.policy?.recommended_action ||
    c.policy?.action ||
    actionLabel;
    
  const resultExternalId = executionResult?.external_id || 
    executionResult?.recovery_action?.external_id || 
    executionResult?.payment_link_id || 
    c.latest_action?.external_id ||
    c.latest_action?.payment_link_id ||
    c.payment_link_id ||
    null;
    
  const resultPaymentLink = executionResult?.payment_link_url || 
    executionResult?.payment_link || 
    executionResult?.recovery_action?.payment_link_url || 
    executionResult?.recovery_action?.payment_link || 
    c.latest_action?.payment_link_url ||
    c.latest_action?.payment_link ||
    c.recovery_action?.payment_link_url ||
    c.recovery_action?.payment_link ||
    c.payment_link_url ||
    c.payment?.payment_link ||
    null;

  const resultAttempts = executionResult?.attempts ?? 
    executionResult?.case?.attempts ?? 
    c.attempts ?? 
    attempts;

  const isSafetyFallbackUsed = executionResult?.content_safety?.fallback_used === true;

  const executionAgentAssessment = (
    executionResult?.agent_assessment ||
    executionResult?.case?.agent_assessment ||
    c.agent_assessment ||
    null
  );

  const hasExecutionAgentAssessment = Boolean(
    executionAgentAssessment &&
    typeof executionAgentAssessment === 'string' &&
    executionAgentAssessment.trim().length > 0
  );

  const handleCopyLink = () => {
    if (!resultPaymentLink) return;
    navigator.clipboard.writeText(resultPaymentLink);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs animate-in fade-in duration-150">
      <div 
        className="bg-white rounded-xl shadow-2xl border border-slate-200 max-w-lg w-full flex flex-col max-h-[92vh] overflow-hidden animate-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="px-5 py-3.5 border-b border-slate-200/80 flex items-center justify-between bg-slate-50/70">
          <div className="flex items-center gap-2.5">
            <div className={`w-7 h-7 rounded-lg flex items-center justify-center text-white ${
              executionResult ? 'bg-emerald-600' : executionError ? 'bg-rose-600' : 'bg-indigo-600'
            }`}>
              {executionResult ? (
                <CheckCircle2 size={16} />
              ) : executionError ? (
                <ShieldAlert size={16} />
              ) : (
                <Bot size={16} />
              )}
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 leading-none">
                {executionResult ? 'Recovery Action Result' : 'Run Recovery Agent'}
              </h3>
              <p className="text-[11px] text-slate-500 font-mono mt-1">
                {c.case_code || (c.id ? `Case #${c.id}` : 'Case Inspection')}
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            disabled={isExecuting}
            className="text-slate-400 hover:text-slate-600 p-1 rounded-md cursor-pointer disabled:opacity-50 transition-colors"
            aria-label="Close dialog"
          >
            <X size={16} />
          </button>
        </div>

        {/* Modal Scrollable Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-3.5 text-xs">
          {/* Target Case Overview Strip */}
          <div className="bg-slate-50/80 rounded-lg p-3 border border-slate-200/70 flex items-center justify-between gap-2">
            <div>
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Amount at Risk</span>
              <span className="text-sm font-mono font-bold text-slate-900">
                {formatMinorUnitsToINR(atRisk, { showDecimals: true })}
              </span>
            </div>
            <div>
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Failure Trigger</span>
              <span className="text-xs text-slate-800 font-medium">{failureLabel}</span>
            </div>
            <div className="text-right">
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Current State</span>
              <StatusBadge status={c.status} size="xs" />
            </div>
          </div>

          {/* STATE 1: OPERATIONAL ERROR OCCURRED */}
          {executionError && (
            <div className="p-3.5 rounded-lg bg-rose-50 border border-rose-200 text-rose-900 space-y-1.5 animate-in fade-in duration-150">
              <div className="flex items-start gap-2">
                <AlertTriangle size={15} className="text-rose-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-rose-950 text-xs">
                    Recovery action could not be executed
                  </p>
                  <p className="text-rose-800 text-[11px] mt-0.5 leading-relaxed break-words font-medium">
                    {executionError}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* STATE 2: SUCCESS OUTCOME TELEMETRY */}
          {executionResult && (
            <div className="space-y-3 animate-in fade-in duration-150">
              <div className="p-3.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-900 flex items-start gap-2.5">
                <CheckCircle2 size={16} className="text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-emerald-950">Recovery Action Executed</p>
                  <p className="text-emerald-800 text-[11px] mt-0.5">
                    Backend policy approved and recorded the recovery action in Razorpay Test Mode.
                  </p>
                </div>
              </div>

              {/* 1. AGENT ASSESSMENT */}
              <div className="p-3.5 rounded-lg bg-indigo-50/70 border border-indigo-100 space-y-1.5 animate-in fade-in">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-indigo-950 uppercase tracking-wider text-[10px] flex items-center gap-1.5">
                    <Bot size={13} className="text-indigo-600" />
                    <span>AGENT ASSESSMENT</span>
                  </span>
                  <div className="flex items-center gap-1.5">
                    {isSafetyFallbackUsed && (
                      <span className="text-[10px] text-amber-700 bg-amber-100/70 border border-amber-200 px-1.5 py-0.2 rounded font-medium">
                        Safety fallback applied
                      </span>
                    )}
                    <span className="text-[10px] text-indigo-600 font-mono">
                      Source: Recovery Agent
                    </span>
                  </div>
                </div>
                <p className="text-indigo-900 text-xs leading-relaxed font-normal">
                  {hasExecutionAgentAssessment 
                    ? executionAgentAssessment 
                    : 'Assessment summary unavailable.'}
                </p>
              </div>

              {/* 2-6. POLICY DECISION, ACTION, EXECUTION, ATTEMPTS & PAYMENT LINK */}
              <div className="bg-slate-50 rounded-lg p-3.5 border border-slate-200/80 space-y-2.5 font-medium">
                {/* 2. Policy Decision */}
                <div className="flex items-center justify-between text-slate-600">
                  <span className="text-slate-500">Policy Decision</span>
                  <span className="font-semibold text-teal-700 bg-teal-50 px-2 py-0.5 rounded border border-teal-200 text-xs flex items-center gap-1">
                    <ShieldCheck size={12} />
                    <span>{isPolicyEligible ? 'ELIGIBLE' : 'BLOCKED'}</span>
                  </span>
                </div>

                {/* 3. Approved Action */}
                <div className="flex items-center justify-between text-slate-600">
                  <span className="text-slate-500">Approved Action</span>
                  <span className="text-slate-900 font-semibold">{getPolicyActionLabel(resultAction)}</span>
                </div>

                {/* 4. Execution Status */}
                <div className="flex items-center justify-between text-slate-600">
                  <span className="text-slate-500">Execution Status</span>
                  <StatusBadge status={resultStatus} size="xs" />
                </div>

                {/* 5. Attempt */}
                <div className="flex items-center justify-between text-slate-600">
                  <span className="text-slate-500">Attempt</span>
                  <span className="font-mono text-indigo-700 font-semibold">
                    {resultAttempts} / {maxAttempts}
                  </span>
                </div>

                {/* External ID if available */}
                {resultExternalId && (
                  <div className="flex items-center justify-between text-slate-600">
                    <span className="text-slate-500">External ID</span>
                    <span className="font-mono text-slate-900 font-semibold text-[11px]">
                      {resultExternalId}
                    </span>
                  </div>
                )}

                {/* 6. Payment Link */}
                <div className="pt-2 border-t border-slate-200/60 space-y-1.5">
                  <span className="text-slate-500 block text-[11px]">Payment Link:</span>
                  {resultPaymentLink ? (
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-1.5 bg-white p-2 rounded border border-slate-200 font-mono text-[11px]">
                        <span className="truncate flex-1 text-slate-800">{resultPaymentLink}</span>
                        <button
                          onClick={handleCopyLink}
                          className="p-1 rounded hover:bg-slate-100 text-slate-600 transition-colors cursor-pointer"
                          title="Copy payment link"
                        >
                          {copiedLink ? <Check size={13} className="text-emerald-600" /> : <Copy size={13} />}
                        </button>
                      </div>
                      <a
                        href={resultPaymentLink}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center justify-center gap-1.5 w-full px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded font-semibold text-xs transition-colors cursor-pointer"
                      >
                        <span>Open Payment Link</span>
                        <ExternalLink size={13} />
                      </a>
                    </div>
                  ) : (
                    <span className="text-slate-400 font-mono text-xs">Not generated</span>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* STATE 3: PRE-EXECUTION / DEFAULT PARAMETERS (1. ASSESSMENT, 2. ML ADVISORY, 3. POLICY DECISION, 4. SAFETY BOUNDARY, 5. PIPELINE) */}
          {!executionResult && (
            <>
              {/* 1. RECOVERY ASSESSMENT */}
              <div className="p-3.5 rounded-lg bg-indigo-50/70 border border-indigo-100 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-indigo-950 uppercase tracking-wider text-[10px] flex items-center gap-1.5">
                    <Bot size={13} className="text-indigo-600" />
                    <span>{assessmentTitle}</span>
                  </span>
                  <span className="text-[10px] text-indigo-600 font-mono">
                    {assessmentSourceLabel}
                  </span>
                </div>
                <p className="text-indigo-900 text-xs leading-relaxed font-normal">
                  {assessmentContent}
                </p>
              </div>

              {/* 2. ML ADVISORY */}
              <div className="bg-white rounded-lg p-3.5 border border-slate-200/80 shadow-2xs space-y-2">
                <div className="flex items-center justify-between pb-1.5 border-b border-slate-100">
                  <span className="font-bold text-slate-900 uppercase tracking-wider text-[10px] flex items-center gap-1.5">
                    <Sparkles size={13} className="text-indigo-600" />
                    <span>ML Advisory</span>
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">Non-Authoritative</span>
                </div>

                <div className="grid grid-cols-3 gap-2 pt-0.5">
                  <div className="bg-slate-50/80 p-2 rounded border border-slate-100">
                    <span className="text-[10px] text-slate-500 block">Recovery Probability</span>
                    <span className="text-xs font-mono font-bold text-indigo-700">
                      {mlProb !== null ? formatPercentage(mlProb) : 'Not recorded'}
                    </span>
                  </div>

                  <div className="bg-slate-50/80 p-2 rounded border border-slate-100">
                    <span className="text-[10px] text-slate-500 block">Recommendation</span>
                    <span className="text-xs font-semibold text-slate-800 truncate block">
                      {typeof mlRec === 'string' ? (mlRec.length > 22 ? mlRec.slice(0, 20) + '...' : mlRec) : 'Not recorded'}
                    </span>
                  </div>

                  <div className="bg-slate-50/80 p-2 rounded border border-slate-100">
                    <span className="text-[10px] text-slate-500 block">Mode</span>
                    <span className="text-xs font-mono font-semibold text-slate-700 capitalize">
                      {mlMode || 'Shadow'}
                    </span>
                  </div>
                </div>
              </div>

              {/* 3. DETERMINISTIC POLICY */}
              <div className="bg-white rounded-lg p-3.5 border border-slate-200/80 shadow-2xs space-y-2 font-medium">
                <div className="flex items-center justify-between pb-1.5 border-b border-slate-100">
                  <span className="font-bold text-slate-900 uppercase tracking-wider text-[10px] flex items-center gap-1.5">
                    <ShieldCheck size={13} className="text-teal-600" />
                    <span>Deterministic Policy</span>
                  </span>
                  <span className="text-[10px] font-semibold text-teal-800 bg-teal-50 px-1.5 py-0.5 rounded border border-teal-200">
                    Authoritative
                  </span>
                </div>

                <div className="space-y-1.5 pt-0.5 text-[11px]">
                  <div className="flex items-center justify-between text-slate-600">
                    <span className="text-slate-500">Policy Status</span>
                    <span className={`font-semibold flex items-center gap-1 ${isPolicyEligible ? 'text-teal-700' : 'text-rose-600'}`}>
                      <ShieldCheck size={12} />
                      <span>{policyDecisionText}</span>
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-slate-600">
                    <span className="text-slate-500">Action</span>
                    <span className="text-slate-900 font-semibold">{actionLabel}</span>
                  </div>

                  <div className="flex items-center justify-between text-slate-600">
                    <span className="text-slate-500">Maximum Attempts</span>
                    <span className="font-mono text-slate-800">
                      {maxAttempts}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-slate-600">
                    <span className="text-slate-500">Cooldown</span>
                    <span className="font-mono text-slate-800">{cooldownPeriod} mins</span>
                  </div>

                  <div className="pt-1 border-t border-slate-100">
                    <span className="text-slate-500 block text-[10px] mb-0.5">Reason:</span>
                    <p className="text-slate-700 bg-slate-50 p-2 rounded border border-slate-100 text-[11px] leading-relaxed">
                      {policyReason}
                    </p>
                  </div>
                </div>
              </div>

              {/* 4. SAFETY BOUNDARY */}
              <div className="p-3 rounded-lg bg-amber-50/80 border border-amber-200/80 text-amber-950 flex items-start gap-2.5">
                <Lock size={15} className="text-amber-700 shrink-0 mt-0.5" />
                <div className="leading-snug">
                  <div className="flex items-center justify-between gap-2">
                    <p className="font-bold text-amber-950 text-xs">2-Attempt Hard Ceiling</p>
                    <span className="font-mono text-[11px] font-bold text-amber-900 bg-amber-100/70 px-1.5 py-0.5 rounded">
                      {attempts} / 2
                    </span>
                  </div>
                  <p className="text-amber-800 text-[11px] mt-1 font-medium">
                    Automated recovery is limited to two attempts per case.
                  </p>
                </div>
              </div>

              {/* 5. EXECUTION PIPELINE */}
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Execution Pipeline</span>
                  <span className="text-[10px] text-indigo-700 font-semibold italic">ML recommends. Policy decides.</span>
                </div>

                <div className="flex items-center justify-between text-[11px] font-mono text-slate-700 py-1 px-1">
                  <div className="flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                    <span>Agent</span>
                  </div>
                  <ArrowRight size={11} className="text-slate-400" />
                  <div className="flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-teal-500"></span>
                    <span>Policy Gate</span>
                  </div>
                  <ArrowRight size={11} className="text-slate-400" />
                  <div className="flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span>
                    <span>Bounded Executor</span>
                  </div>
                  <ArrowRight size={11} className="text-slate-400" />
                  <div className="flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                    <span>Razorpay</span>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Modal Footer Actions */}
        <div className="px-5 py-3 bg-slate-50 border-t border-slate-200/80 flex items-center justify-end gap-2.5">
          {executionResult ? (
            <>
              <button
                onClick={onClose}
                className="px-3.5 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-200/60 rounded-lg transition-colors cursor-pointer"
              >
                Close
              </button>
              {onViewDetails && (
                <button
                  onClick={() => {
                    onClose();
                    onViewDetails(c);
                  }}
                  className="inline-flex items-center gap-1.5 px-4 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm transition-all cursor-pointer"
                >
                  <Zap size={13} />
                  <span>Inspect in Drawer</span>
                </button>
              )}
            </>
          ) : (
            <>
              <button
                onClick={onClose}
                disabled={isExecuting}
                className="px-3.5 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-200/60 rounded-lg transition-colors cursor-pointer disabled:opacity-50"
              >
                {executionError ? 'Dismiss' : 'Cancel'}
              </button>
              <button
                onClick={onConfirm}
                disabled={isExecuting || attempts >= maxAttempts}
                className="inline-flex items-center gap-1.5 px-4 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isExecuting ? (
                  <>
                    <RotateCcw size={13} className="animate-spin" />
                    <span>Agent Executing...</span>
                  </>
                ) : executionError ? (
                  <>
                    <RotateCcw size={13} />
                    <span>Retry Bounded Action</span>
                  </>
                ) : (
                  <>
                    <Bot size={14} />
                    <span>Execute Bounded Action</span>
                  </>
                )}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
