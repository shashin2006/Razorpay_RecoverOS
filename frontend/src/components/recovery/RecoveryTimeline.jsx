import React from 'react';
import { 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  ShieldCheck, 
  ShieldAlert, 
  Bot, 
  CreditCard,
  Zap,
  Activity
} from 'lucide-react';
import { formatTimestamp, formatRelativeTime } from '../../utils/formatting.js';
import StatusBadge from '../common/StatusBadge.jsx';

export default function RecoveryTimeline({ timeline = [] }) {
  if (!timeline || timeline.length === 0) {
    return (
      <div className="py-6 text-center text-xs text-slate-400 bg-slate-50 rounded-lg border border-slate-200/60">
        No audit events recorded for this case yet.
      </div>
    );
  }

  const getEventIcon = (eventStr, statusStr) => {
    const s = String(statusStr || '').toLowerCase();
    const e = String(eventStr || '').toLowerCase();

    if (['success', 'recovered', 'completed', 'paid'].includes(s) || e.includes('recovered') || e.includes('paid')) {
      return <CheckCircle2 size={13} className="text-emerald-600" />;
    }
    if (['error', 'failed', 'blocked', 'policy_blocked'].includes(s) || e.includes('blocked') || e.includes('fail')) {
      return <ShieldAlert size={13} className="text-rose-600" />;
    }
    if (['warning', 'attention'].includes(s) || e.includes('warn')) {
      return <AlertCircle size={13} className="text-amber-600" />;
    }
    if (e.includes('agent') || e.includes('llm') || e.includes('model') || e.includes('ml') || e.includes('prediction')) {
      return <Bot size={13} className="text-indigo-600" />;
    }
    if (e.includes('link') || e.includes('payment') || e.includes('razorpay')) {
      return <CreditCard size={13} className="text-teal-600" />;
    }
    if (e.includes('policy')) {
      return <ShieldCheck size={13} className="text-teal-600" />;
    }
    return <Clock size={13} className="text-slate-500" />;
  };

  const getEventBadgeClass = (statusStr) => {
    const s = String(statusStr || '').toLowerCase();
    if (['success', 'recovered', 'completed', 'paid'].includes(s)) {
      return 'bg-emerald-50 border-emerald-300 text-emerald-700';
    }
    if (['error', 'failed', 'blocked', 'policy_blocked'].includes(s)) {
      return 'bg-rose-50 border-rose-300 text-rose-700';
    }
    if (['warning', 'attention'].includes(s)) {
      return 'bg-amber-50 border-amber-300 text-amber-800';
    }
    return 'bg-slate-50 border-slate-300 text-slate-700';
  };

  return (
    <div className="relative pl-6 space-y-3.5 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
      {timeline.map((item, idx) => {
        const title = item.title || item.event_title || item.event || item.name || `Event #${idx + 1}`;
        const description = item.description || item.details || item.message || '';
        const timestamp = item.timestamp || item.created_at || item.time || null;
        const status = item.status || item.level || null;

        return (
          <div key={idx} className="relative group">
            {/* Dot / Icon */}
            <div className={`absolute -left-6 top-1 w-5 h-5 rounded-full border flex items-center justify-center bg-white shadow-2xs ${getEventBadgeClass(status)}`}>
              {getEventIcon(title, status)}
            </div>

            <div className="bg-slate-50/80 hover:bg-slate-100/70 transition-colors p-3 rounded-lg border border-slate-200/70 text-xs">
              <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-900">{title}</span>
                  {status && (
                    <StatusBadge status={status} size="xs" />
                  )}
                </div>
                {timestamp && (
                  <span className="text-[10px] font-mono text-slate-400 shrink-0">
                    {formatRelativeTime(timestamp)}
                  </span>
                )}
              </div>

              {description && (
                <p className="text-slate-600 leading-relaxed text-[11px] mt-0.5">
                  {description}
                </p>
              )}

              {timestamp && (
                <div className="mt-1 text-[10px] font-mono text-slate-400">
                  {formatTimestamp(timestamp)}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
