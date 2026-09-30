import React, { useState } from 'react';
import { ShieldCheck, Info } from 'lucide-react';

export default function TestModeBadge() {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div className="relative inline-flex items-center">
      <div 
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-300/80 cursor-help select-none"
      >
        <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
        <span>Test Mode</span>
      </div>

      {showTooltip && (
        <div className="absolute top-full right-0 mt-2 z-50 w-64 p-3 bg-slate-900 text-slate-100 text-xs rounded-lg shadow-xl border border-slate-800 animate-in fade-in zoom-in-95 duration-150 pointer-events-none">
          <div className="flex items-start gap-2">
            <ShieldCheck size={16} className="text-amber-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-white mb-0.5">Razorpay Test Mode</p>
              <p className="text-slate-300 leading-relaxed">
                No real payments are processed. All payment links and recovery flows operate safely within the sandbox environment.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
