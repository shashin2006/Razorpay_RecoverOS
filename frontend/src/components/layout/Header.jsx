import React from 'react';
import { RefreshCw, Radio, AlertCircle } from 'lucide-react';
import TestModeBadge from './TestModeBadge.jsx';
import { formatRelativeTime } from '../../utils/formatting.js';

export default function Header({ 
  backendStatus = 'connecting', // 'connected', 'connecting', 'unavailable'
  lastUpdated = null,
  isRefreshing = false,
  onRefresh = () => {},
  isMockMode = false,
  onToggleMock = null
}) {
  const getBackendBadge = () => {
    switch (backendStatus) {
      case 'connected':
        return (
          <div className="inline-flex items-center gap-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span>Backend Connected</span>
          </div>
        );
      case 'partially_unavailable':
        return (
          <div className="inline-flex items-center gap-1.5 text-xs font-medium text-amber-700 bg-amber-50 px-2.5 py-1 rounded-full border border-amber-200">
            <span className="w-2 h-2 rounded-full bg-amber-500" />
            <span>Partially Available</span>
          </div>
        );
      case 'connecting':
        return (
          <div className="inline-flex items-center gap-1.5 text-xs font-medium text-amber-700 bg-amber-50 px-2.5 py-1 rounded-full border border-amber-200">
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
            <span>Connecting...</span>
          </div>
        );
      case 'unavailable':
      default:
        return (
          <div className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-600 bg-slate-100 px-2.5 py-1 rounded-full border border-slate-200">
            <span className="w-2 h-2 rounded-full bg-rose-500" />
            <span>Backend Offline</span>
          </div>
        );
    }
  };

  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-xs border-b border-slate-200/80 px-4 sm:px-6 lg:px-8 py-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 max-w-7xl mx-auto">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">
              Recovery Command Center
            </h1>
            <span className="hidden md:inline-block px-2 py-0.5 text-[11px] font-semibold bg-indigo-50 text-indigo-700 rounded border border-indigo-200/60">
              RecoveryOS Core
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            AI-assisted revenue recovery with deterministic policy controls.
          </p>
        </div>

        <div className="flex items-center flex-wrap gap-2.5 sm:self-center">
          <TestModeBadge />
          {getBackendBadge()}

          <div className="h-4 w-px bg-slate-200 hidden sm:block" />

          {lastUpdated && (
            <span className="text-xs text-slate-400 hidden lg:inline-block font-mono">
              Updated {formatRelativeTime(lastUpdated)}
            </span>
          )}

          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white hover:bg-slate-50 active:bg-slate-100 rounded-lg border border-slate-300 shadow-2xs transition-colors cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
            title="Refresh recovery metrics"
          >
            <RefreshCw size={13} className={isRefreshing ? "animate-spin text-indigo-600" : "text-slate-500"} />
            <span className="hidden sm:inline">Refresh</span>
          </button>
        </div>
      </div>
    </header>
  );
}
