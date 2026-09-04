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
import { getPolicyActionLabel, getFailureCategoryLabel } from '../../utils/formatting.js';

// Normalize NVIDIA's final assessment to clean operator-facing text.
// The model may return a string or a structured object; never render an
// object directly because React would display it incorrectly.
function cleanAgentAssessment(value) {
  let text = value;

  if (text && typeof text === 'object') {
    const preferred =
      text.agent_assessment ??
      text.assessment ??
      text.reasoning ??
      text.message ??
      text.content ??
      text.response ??
      text.text ??
      null;

    text = preferred ?? '';
  }

  if (text === null || text === undefined) return '';

  return String(text)
    // Remove fenced markdown/code wrappers.
    .replace(/```(?:text|markdown|md|json|javascript|js)?/gi, '')
    .replace(/```/g, '')
    // Remove markdown headings, bullets, numbered-list prefixes and blockquotes.
    .replace(/^\s{0,3}#{1,6}\s+/gm, '')
    .replace(/^\s*[-*+]\s+/gm, '')
    .replace(/^\s*\d+[.)]\s+/gm, '')
    .replace(/^\s*>\s?/gm, '')
    // Remove markdown emphasis without touching normal punctuation.
    .replace(/\*\*(.*?)\*\*/gs, '$1')
    .replace(/__(.*?)__/gs, '$1')
    .replace(/(?<!\w)\*([^*\n]+)\*(?!\w)/g, '$1')
    .replace(/(?<!\w)_([^_\n]+)_(?!\w)/g, '$1')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '$1')
    // Remove accidental code-comment markers that sometimes appear in model output.
    .replace(/^\s*\/\*+\s*$/gm, '')
    .replace(/^\s*\*+\/\s*$/gm, '')
    .replace(/^\s*\/\/\s?/gm, '')
    // Remove lines containing only decorative punctuation.
    .replace(/^\s*[*/_#`~|]+\s*$/gm, '')
    // Normalize whitespace after cleanup.
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

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

  // Backend detail responses wrap the authoritative case under `case`.
  // Normalize both list-style and detail-style payloads here so the modal
  // never displays stale/optimistic attempts or status.
  const backendCase = recoveryCase.case || recoveryCase;
  const latestAction = recoveryCase.latest_action || recoveryCase.recovery_action || null;
  const attempts = backendCase.attempts ?? recoveryCase.attempts ?? 0;
  const maxAttempts = recoveryCase.policy?.max_attempts ?? recoveryCase.max_attempts ?? recoveryCase.policy?.max_automated_attempts ?? 2;
  const atRisk = backendCase.amount_at_risk_minor ?? recoveryCase.amount_at_risk_minor ?? recoveryCase.amount_at_risk ?? 0;
  const failureLabel = getFailureCategoryLabel(
    backendCase.failure_category || 
    recoveryCase.failure_category || 
    recoveryCase.payment?.failure_reason || 
    'payment_failed'
  );

  const actionKey = recoveryCase.policy?.recommended_action || 
    recoveryCase.policy?.action || 
    recoveryCase.action || 
    'payment_link';
  const actionLabel = getPolicyActionLabel(actionKey);

  // 1. AGENT ASSESSMENT DETERMINATION (Strictly backend-backed or deterministic)
  const textualAgentReasoning = (
    executionResult?.agent_assessment ||
    executionResult?.original_message ||
    recoveryCase.agent?.agent_reasoning || 
    recoveryCase.agent_reasoning || 
    recoveryCase.agent?.reasoning || 
    recoveryCase.agent_assessment || 
    recoveryCase.assessment || 
    null
  );

  // Always sanitize the model-backed assessment before rendering it.
  // This handles both plain strings and structured model responses.
  const cleanedAgentReasoning = cleanAgentAssessment(textualAgentReasoning);

  const hasTextualAgentResponse = cleanedAgentReasoning.length > 0;

  // If no textual agent response exists in backend, use a concise deterministic summary.
  const deterministicAssessment = `${failureLabel} decline appears potentially recoverable through ${actionLabel.toLowerCase()}.`;
  const assessmentTitle = hasTextualAgentResponse ? 'Agent Assessment' : 'Recovery assessment';
  const assessmentContent = hasTextualAgentResponse ? cleanedAgentReasoning : deterministicAssessment;

  // 2. LLM PREDICTION DATA
  const mlObj = recoveryCase.ml || {};
  const mlProb = mlObj.recovery_probability ?? recoveryCase.recovery_probability ?? null;
  const mlRec = mlObj.recommendation || recoveryCase.ml_recommendation || (mlProb && mlProb >= 0.5 ? 'Recover' : 'Monitor');
  const mlMode = mlObj.mode || recoveryCase.mode || 'Shadow';

  // 3. POLICY DECISION DATA
  const policyObj = recoveryCase.policy || {};
  const isPolicyEligible = policyObj.eligible ?? recoveryCase.is_eligible ?? (attempts < maxAttempts);
  const policyDecisionText = policyObj.decision || (isPolicyEligible ? 'Policy Approved' : 'Policy Blocked');
  const cooldownPeriod = policyObj.cooldown_period_minutes ?? policyObj.cooldown ?? recoveryCase.cooldown ?? null;

  // 4. EXECUTION OUTCOME DATA EXTRACTION (when executed)
  // The agent endpoint returns execution details inside tool_calls. The
  // case-detail endpoint separately returns latest_action. Read both.
  const toolCalls = Array.isArray(executionResult?.tool_calls)
    ? executionResult.tool_calls
    : [];
  const executionToolResult = [...toolCalls]
    .reverse()
    .find((call) => call?.tool === 'execute_bounded_recovery')?.result || null;

  const resultStatus = executionResult?.status || 
    executionToolResult?.status ||
    latestAction?.status ||
    executionResult?.recovery_action?.status || 
    executionResult?.action_status ||
    'executed';
    
  const resultAction = executionResult?.action || 
    executionToolResult?.action ||
    latestAction?.action_type ||
    executionResult?.recovery_action?.action || 
    executionResult?.action_type ||
    actionKey;
    
  const resultExternalId = executionResult?.external_id || 
    executionToolResult?.external_id ||
    latestAction?.external_id ||
    executionResult?.recovery_action?.external_id || 
    executionResult?.payment_link_id || 
    null;
    
  const resultPaymentLink = executionResult?.payment_link_url || 
    executionToolResult?.payment_link_url ||
    latestAction?.payment_link_url ||
    executionResult?.payment_link || 
    executionResult?.recovery_action?.payment_link_url || 
    executionResult?.recovery_action?.payment_link || 
    null;

  const resultCaseStatus = executionResult?.case?.status || backendCase.status || recoveryCase.status;
  const resultAttempts = executionResult?.case?.attempts ??
    backendCase.attempts ??
    latestAction?.attempt_number ??
    executionResult?.attempts ??
    attempts;

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
                {recoveryCase.case_code || (recoveryCase.id ? `Case #${recoveryCase.id}` : 'Case Inspection')}
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
              <StatusBadge status={backendCase.status || recoveryCase.status} size="xs" />
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
              {hasTextualAgentResponse && (
                <div className="p-3.5 rounded-lg bg-indigo-50/70 border border-indigo-100 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-indigo-950 uppercase tracking-wider text-[10px] flex items-center gap-1.5">
                      <Bot size={13} className="text-indigo-600" />
                      <span>Agent Assessment</span>
                    </span>
                    <span className="text-[10px] text-indigo-600 font-mono">NVIDIA Recovery Agent</span>
                  </div>
                  <p className="text-indigo-900 text-xs leading-relaxed font-normal whitespace-pre-wrap">
                    {cleanedAgentReasoning}
                  </p>
                </div>
              )}
              <div className={`p-3.5 rounded-lg border flex items-start gap-2.5 ${
                resultCaseStatus === 'recovered'
                  ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                  : 'bg-indigo-50 border-indigo-200 text-indigo-900'
              }`}>
                {resultCaseStatus === 'recovered' ? (
                  <CheckCircle2 size={16} className="text-emerald-600 shrink-0 mt-0.5" />
                ) : (
                  <Zap size={16} className="text-indigo-600 shrink-0 mt-0.5" />
                )}
                <div>
                  <p className="font-bold">
                    {resultCaseStatus === 'recovered'
                      ? 'Revenue Recovered'
                      : 'Recovery Action Executed'}
                  </p>
                  <p className="text-[11px] mt-0.5 leading-relaxed">
                    {resultCaseStatus === 'recovered'
                      ? 'Razorpay confirmed the payment and RecoveryOS recorded the recovered amount.'
                      : 'Policy approved and recorded the action in Razorpay Test Mode. Payment recovery remains pending until Razorpay confirms payment.'}
                  </p>
                </div>
              </div>

              {/* Action Telemetry Card */}
              <div className="bg-slate-50 rounded-lg p-3.5 border border-slate-200/80 space-y-2 font-medium">
                <div className="flex items-center justify-between text-slate-600">
                  <span className="text-slate-500">Action Status</span>
                  <StatusBadge status={resultStatus} size="xs" />
                </div>

                <div className="flex items-center justify-between text-slate-600">
                  <span className="text-slate-500">Action Type</span>
                  <span className="text-slate-900 font-semibold">{getPolicyActionLabel(resultAction)}</span>
                </div>

                <div className="flex items-center justify-between text-slate-600">
                  <span className="text-slate-500">External ID</span>
                  <span className="font-mono text-slate-900 font-bold">
                    {resultExternalId || <span className="text-slate-400 font-normal">Not recorded</span>}
                  </span>
                </div>

                <div className="flex items-center justify-between text-slate-600">
                  <span className="text-slate-500">Automated Attempts</span>
                  <span className="font-mono text-indigo-700 font-semibold">
                    {resultAttempts} of {maxAttempts}
                  </span>
                </div>

                <div className="flex items-center justify-between text-slate-600">
                  <span className="text-slate-500">Recovery Outcome</span>
                  <span className={`font-semibold ${
                    resultCaseStatus === 'recovered'
                      ? 'text-emerald-700'
                      : 'text-amber-700'
                  }`}>
                    {resultCaseStatus === 'recovered'
                      ? 'Payment confirmed'
                      : 'Awaiting payment'}
                  </span>
                </div>

                {resultPaymentLink && (
                  <div className="pt-2 border-t border-slate-200/60 space-y-1">
                    <span className="text-slate-500 block text-[11px]">Razorpay Payment Link:</span>
                    <div className="flex items-center gap-1.5 bg-white p-2 rounded border border-slate-200 font-mono text-[11px]">
                      <span className="truncate flex-1 text-slate-800">{resultPaymentLink}</span>
                      <button
                        onClick={handleCopyLink}
                        className="p-1 rounded hover:bg-slate-100 text-slate-600 transition-colors cursor-pointer"
                        title="Copy payment link"
                      >
                        {copiedLink ? <Check size={13} className="text-emerald-600" /> : <Copy size={13} />}
                      </button>
                      <a
                        href={resultPaymentLink}
                        target="_blank"
                        rel="noreferrer"
                        className="p-1 rounded hover:bg-slate-100 text-indigo-600 transition-colors cursor-pointer"
                        title="Open payment link in new tab"
                      >
                        <ExternalLink size={13} />
                      </a>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* STATE 3: PRE-EXECUTION / DEFAULT PARAMETERS (1. AGENT ASSESSMENT, 2. LLM PREDICTION, 3. POLICY DECISION, 4. SAFETY BOUNDARY, 5. PIPELINE) */}
          {!executionResult && (
            <>
              {/* 1. AGENT ASSESSMENT */}
              <div className="p-3.5 rounded-lg bg-indigo-50/70 border border-indigo-100 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-indigo-950 uppercase tracking-wider text-[10px] flex items-center gap-1.5">
                    <Bot size={13} className="text-indigo-600" />
                    <span>{assessmentTitle}</span>
                  </span>
                  <span className="text-[10px] text-indigo-600 font-mono">
                    {hasTextualAgentResponse ? 'Advisory Signal' : 'Deterministic'}
                  </span>
                </div>
                <p className="text-indigo-900 text-xs leading-relaxed font-normal">
                  {assessmentContent}
                </p>
              </div>

              {/* 2. LLM PREDICTION */}
              <div className="bg-white rounded-lg p-3.5 border border-slate-200/80 shadow-2xs space-y-2">
                <div className="flex items-center justify-between pb-1.5 border-b border-slate-100">
                  <span className="font-bold text-slate-900 uppercase tracking-wider text-[10px] flex items-center gap-1.5">
                    <Sparkles size={13} className="text-indigo-600" />
                    <span>LLM Prediction</span>
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

              {/* 3. POLICY DECISION */}
              <div className="bg-white rounded-lg p-3.5 border border-slate-200/80 shadow-2xs space-y-2 font-medium">
                <div className="flex items-center justify-between pb-1.5 border-b border-slate-100">
                  <span className="font-bold text-slate-900 uppercase tracking-wider text-[10px] flex items-center gap-1.5">
                    <ShieldCheck size={13} className="text-teal-600" />
                    <span>Policy Decision</span>
                  </span>
                  <span className="text-[10px] font-semibold text-teal-800 bg-teal-50 px-1.5 py-0.5 rounded border border-teal-200">
                    Authoritative
                  </span>
                </div>

                <div className="space-y-1.5 pt-0.5 text-[11px]">
                  <div className="flex items-center justify-between text-slate-600">
                    <span className="text-slate-500">Policy status</span>
                    <span className={`font-semibold flex items-center gap-1 ${isPolicyEligible ? 'text-teal-700' : 'text-rose-600'}`}>
                      <ShieldCheck size={12} />
                      <span>{policyDecisionText}</span>
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-slate-600">
                    <span className="text-slate-500">Requested action</span>
                    <span className="text-slate-900 font-semibold">{actionLabel}</span>
                  </div>

                  <div className="flex items-center justify-between text-slate-600">
                    <span className="text-slate-500">Automated attempts</span>
                    <span className="font-mono text-slate-800">
                      {attempts} / {maxAttempts} attempts
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-slate-600">
                    <span className="text-slate-500">Cooldown</span>
                    <span className="font-mono text-slate-800">{cooldownPeriod !== null ? `${cooldownPeriod} minute cooldown` : 'Not recorded'}</span>
                  </div>
                </div>
              </div>

              {/* 4. SAFETY BOUNDARY */}
              <div className="p-3 rounded-lg bg-amber-50/80 border border-amber-200/80 text-amber-950 flex items-start gap-2.5">
                <Lock size={15} className="text-amber-700 shrink-0 mt-0.5" />
                <div className="leading-snug">
                  <p className="font-bold text-amber-950 text-xs">2-Attempt Hard Ceiling</p>
                  <p className="text-amber-800 text-[11px] mt-0.5 font-medium">
                    Automated recovery is limited to 2 attempts per case.
                  </p>
                </div>
              </div>

              {/* 5. EXECUTION PIPELINE */}
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Execution Pipeline</span>
                  <span className="text-[10px] text-indigo-700 font-semibold">ML recommends. Policy decides.</span>
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
                    // The drawer expects the case record itself (with `id`),
                    // not the wrapped GET /cases/{id} detail response.
                    onViewDetails(backendCase);
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
