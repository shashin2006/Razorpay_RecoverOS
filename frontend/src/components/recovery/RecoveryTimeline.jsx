import React from 'react';
import {
  CheckCircle2,
  AlertCircle,
  Clock,
  ShieldCheck,
  ShieldAlert,
  Bot,
  CreditCard,
  Activity,
  FileSearch,
  Zap,
} from 'lucide-react';
import { formatTimestamp, formatRelativeTime } from '../../utils/formatting.js';
import StatusBadge from '../common/StatusBadge.jsx';

function normalizeEvent(item, idx) {
  const rawType = item?.event_type || item?.type || item?.event || item?.action_type || item?.name || '';
  const rawStatus = item?.status || item?.level || item?.result || '';
  const type = String(rawType).toLowerCase();
  const status = String(rawStatus).toLowerCase();

  const title = item?.title || item?.event_title || item?.label || item?.name || rawType || `Event #${idx + 1}`;
  const description = item?.description || item?.details || item?.message || item?.reason || '';
  const timestamp = item?.timestamp || item?.created_at || item?.received_at || item?.time || null;

  return { ...item, title, description, timestamp, status, type };
}

export default function RecoveryTimeline({ timeline = [] }) {
  if (!Array.isArray(timeline) || timeline.length === 0) {
    return (
      <div className="py-6 text-center text-xs text-slate-400 bg-slate-50 rounded-lg border border-slate-200/60">
        No audit events recorded for this case yet.
      </div>
    );
  }

  const getEventIcon = (eventType, title, status) => {
    const e = `${eventType} ${title}`.toLowerCase();

    if (e.includes('captured') || e.includes('paid') || e.includes('recovered') || ['success', 'recovered', 'completed', 'paid'].includes(status)) {
      return <CheckCircle2 size={13} className="text-emerald-600" />;
    }
    if (e.includes('blocked') || e.includes('fail') || ['error', 'failed', 'blocked', 'policy_blocked'].includes(status)) {
      return <ShieldAlert size={13} className="text-rose-600" />;
    }
    if (e.includes('policy') || e.includes('decision') || e.includes('audit')) {
      return <ShieldCheck size={13} className="text-teal-600" />;
    }
    if (e.includes('agent') || e.includes('nim') || e.includes('model') || e.includes('ml') || e.includes('prediction')) {
      return <Bot size={13} className="text-indigo-600" />;
    }
    if (e.includes('link') || e.includes('payment') || e.includes('razorpay')) {
      return <CreditCard size={13} className="text-teal-600" />;
    }
    if (e.includes('action') || e.includes('execution')) {
      return <Zap size={13} className="text-amber-600" />;
    }
    if (e.includes('webhook') || e.includes('event')) {
      return <Activity size={13} className="text-slate-600" />;
    }
    return <FileSearch size={13} className="text-slate-500" />;
  };

  const getEventBadgeClass = (eventType, status) => {
    const e = String(eventType || '').toLowerCase();
    if (e.includes('captured') || e.includes('paid') || e.includes('recovered') || ['success', 'recovered', 'completed', 'paid'].includes(status)) {
      return 'bg-emerald-50 border-emerald-300';
    }
    if (e.includes('blocked') || e.includes('fail') || ['error', 'failed', 'blocked', 'policy_blocked'].includes(status)) {
      return 'bg-rose-50 border-rose-300';
    }
    if (e.includes('policy') || e.includes('decision')) {
      return 'bg-teal-50 border-teal-300';
    }
    if (e.includes('ml') || e.includes('prediction') || e.includes('agent')) {
      return 'bg-indigo-50 border-indigo-300';
    }
    if (e.includes('action') || e.includes('execution')) {
      return 'bg-amber-50 border-amber-300';
    }
    return 'bg-white border-slate-300';
  };

  const normalized = timeline
    .map(normalizeEvent)
    .sort((a, b) => {
      const ta = a.timestamp ? new Date(a.timestamp).getTime() : 0;
      const tb = b.timestamp ? new Date(b.timestamp).getTime() : 0;
      return ta - tb;
    });

  return (
    <div className="relative pl-6 space-y-3.5 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
      {normalized.map((item, idx) => (
        <div key={item.id || `${item.type}-${item.timestamp || idx}`} className="relative group">
          <div className={`absolute -left-6 top-1 w-5 h-5 rounded-full border flex items-center justify-center bg-white shadow-2xs ${getEventBadgeClass(item.type, item.status)}`}>
            {getEventIcon(item.type, item.title, item.status)}
          </div>

          <div className="bg-slate-50/80 hover:bg-slate-100/70 transition-colors p-3 rounded-lg border border-slate-200/70 text-xs">
            <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
              <div className="flex items-center gap-2 min-w-0">
                <span className="font-bold text-slate-900 truncate">{item.title}</span>
                {item.status && <StatusBadge status={item.status} size="xs" />}
              </div>
              {item.timestamp && (
                <span className="text-[10px] font-mono text-slate-400 shrink-0">
                  {formatRelativeTime(item.timestamp)}
                </span>
              )}
            </div>

            {item.description && (
              <p className="text-slate-600 leading-relaxed text-[11px] mt-0.5">
                {item.description}
              </p>
            )}

            {item.timestamp && (
              <div className="mt-1 text-[10px] font-mono text-slate-400">
                {formatTimestamp(item.timestamp)}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
