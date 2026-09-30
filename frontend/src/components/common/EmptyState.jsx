import React from 'react';
import { Inbox, ShieldCheck } from 'lucide-react';

export default function EmptyState({ 
  icon: Icon = Inbox, 
  title = "No data available", 
  description = "Recovery case data will appear here when telemetry is processed.",
  action = null
}) {
  return (
    <div className="py-12 px-4 rounded-xl border border-dashed border-slate-300 bg-white text-center flex flex-col items-center justify-center">
      <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 mb-3">
        <Icon size={22} strokeWidth={1.75} />
      </div>
      <h4 className="text-sm font-semibold text-slate-900 mb-1">{title}</h4>
      <p className="text-xs text-slate-500 max-w-sm mb-4 leading-relaxed">{description}</p>
      {action && <div>{action}</div>}
    </div>
  );
}
