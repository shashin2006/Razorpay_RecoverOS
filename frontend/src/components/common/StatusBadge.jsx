import React from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Clock, 
  ShieldCheck, 
  ShieldAlert, 
  Sparkles,
  HelpCircle,
  Activity
} from 'lucide-react';

export default function StatusBadge({ status, size = 'sm', customLabel = null }) {
  if (status === null || status === undefined || status === '') {
    return (
      <span className="inline-flex items-center text-slate-400 text-xs font-mono">
        Not recorded
      </span>
    );
  }

  const normalized = String(status).toLowerCase().trim().replace(/[\s_-]+/g, '_');

  let config = {
    bg: 'bg-slate-100',
    text: 'text-slate-700',
    border: 'border-slate-200',
    icon: HelpCircle,
    label: customLabel || status,
  };

  // OPEN STATUS
  if (normalized === 'open') {
    config = {
      bg: 'bg-blue-50',
      text: 'text-blue-700',
      border: 'border-blue-200',
      icon: Activity,
      label: customLabel || 'Open',
    };
  }
  // RECOVERED STATUS (Actual recovered revenue / closed recovery)
  else if (['recovered', 'paid'].includes(normalized)) {
    config = {
      bg: 'bg-emerald-50',
      text: 'text-emerald-700',
      border: 'border-emerald-200',
      icon: CheckCircle2,
      label: customLabel || (normalized === 'paid' ? 'Paid' : 'Recovered'),
    };
  }
  // EXECUTION OUTCOME STATUSES (Action triggered/link created - distinct from revenue recovery)
  else if (['executed', 'completed', 'created', 'action_executed', 'success'].includes(normalized)) {
    config = {
      bg: 'bg-emerald-50',
      text: 'text-emerald-700',
      border: 'border-emerald-200',
      icon: CheckCircle2,
      label: customLabel || (normalized === 'created' ? 'Created' : normalized === 'action_executed' ? 'Action Executed' : 'Executed'),
    };
  }
  // POLICY APPROVED
  else if (['policy_approved', 'approved'].includes(normalized)) {
    config = {
      bg: 'bg-teal-50',
      text: 'text-teal-700',
      border: 'border-teal-200',
      icon: ShieldCheck,
      label: customLabel || 'Policy Approved',
    };
  }
  // ELIGIBLE STATUS
  else if (['eligible', 'recovery_eligible'].includes(normalized)) {
    config = {
      bg: 'bg-teal-50',
      text: 'text-teal-700',
      border: 'border-teal-200',
      icon: ShieldCheck,
      label: customLabel || 'Eligible',
    };
  }
  // PENDING / AWAITING STATUSES
  else if (['awaiting_payment', 'issued', 'pending', 'attention', 'retry_available', 'cooldown'].includes(normalized)) {
    config = {
      bg: 'bg-amber-50',
      text: 'text-amber-800',
      border: 'border-amber-200',
      icon: Clock,
      label: customLabel || (normalized === 'awaiting_payment' ? 'Awaiting Payment' : 'Pending'),
    };
  }
  // ERROR / BLOCKED STATUSES
  else if (['failed', 'blocked', 'policy_blocked', 'escalated', 'max_attempts_reached', 'blocked_by_policy'].includes(normalized)) {
    config = {
      bg: 'bg-rose-50',
      text: 'text-rose-700',
      border: 'border-rose-200',
      icon: normalized.includes('policy') ? ShieldAlert : XCircle,
      label: customLabel || (normalized === 'policy_blocked' || normalized === 'blocked_by_policy' ? 'Policy Blocked' : normalized === 'escalated' ? 'Escalated' : 'Failed'),
    };
  }
  // ML / ADVISORY STATUSES
  else if (['ml_advisory', 'high_confidence', 'inferred', 'action_requested', 'action_executed'].includes(normalized)) {
    config = {
      bg: 'bg-indigo-50',
      text: 'text-indigo-700',
      border: 'border-indigo-200',
      icon: Sparkles,
      label: customLabel || 'ML Advisory',
    };
  }
  // WARNING EVENT
  else if (['warning'].includes(normalized)) {
    config = {
      bg: 'bg-amber-50',
      text: 'text-amber-800',
      border: 'border-amber-200',
      icon: AlertTriangle,
      label: customLabel || 'Warning',
    };
  }

  const IconComponent = config.icon;
  const sizeClasses = size === 'xs' 
    ? 'px-2 py-0.5 text-xs gap-1' 
    : size === 'md' 
    ? 'px-3 py-1 text-sm gap-1.5 font-medium' 
    : 'px-2.5 py-1 text-xs gap-1.5 font-medium';

  const iconSize = size === 'xs' ? 12 : size === 'md' ? 16 : 14;

  return (
    <span 
      className={`inline-flex items-center rounded-md border ${config.bg} ${config.text} ${config.border} ${sizeClasses} whitespace-nowrap select-none font-medium`}
    >
      <IconComponent size={iconSize} className="shrink-0" />
      <span>{config.label}</span>
    </span>
  );
}
