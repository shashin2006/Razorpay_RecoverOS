import React from 'react';
import { 
  LayoutDashboard, 
  FolderKanban, 
  ShieldAlert, 
  LineChart, 
  History, 
  ExternalLink,
  Shield,
  Layers,
  Sparkles
} from 'lucide-react';
import { API_BASE_URL } from '../../api/client.js';

export default function Sidebar({ 
  currentTab = 'overview', 
  onSelectTab = () => {},
  casesCount = 0,
  mobileOpen = false,
  onCloseMobile = () => {}
}) {
  const navItems = [
    {
      id: 'overview',
      label: 'Overview',
      icon: LayoutDashboard,
      description: 'KPIs & recovery performance',
    },
    {
      id: 'cases',
      label: 'Recovery Cases',
      icon: FolderKanban,
      badge: casesCount > 0 ? casesCount : null,
      description: 'Incident logs & agent trigger',
    },
    {
      id: 'ai-policy',
      label: 'AI & Policy',
      icon: ShieldAlert,
      description: 'Deterministic safety rules',
    },
    {
      id: 'ml-monitoring',
      label: 'ML Monitoring',
      icon: LineChart,
      description: 'Model metrics & agreement',
    },
    {
      id: 'audit-trail',
      label: 'Audit Trail',
      icon: History,
      description: 'End-to-end execution logs',
    },
  ];

  const sidebarContent = (
    <div className="flex flex-col h-full bg-slate-900 text-slate-300 w-64 border-r border-slate-800 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold shadow-md shadow-indigo-600/30">
            <Layers size={18} />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-base text-white tracking-tight">RecoveryOS</span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-slate-800 text-indigo-400 border border-slate-700">
                Core
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">Revenue Recovery Engine</p>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">
          Control Center
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => {
                onSelectTab(item.id);
                onCloseMobile();
              }}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold transition-all duration-150 cursor-pointer ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Icon size={16} className={isActive ? 'text-white' : 'text-slate-400'} />
                <span>{item.label}</span>
              </div>
              {item.badge !== null && item.badge !== undefined && (
                <span className={`text-[11px] px-1.5 py-0.2 rounded-full font-mono ${
                  isActive ? 'bg-indigo-700 text-indigo-100' : 'bg-slate-800 text-slate-300'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}

        <div className="pt-5 px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">
          Intelligence & Policy
        </div>

        <div className="mx-2 p-3 rounded-lg bg-slate-800/60 border border-slate-700/60 text-[11px]">
          <div className="flex items-center gap-1.5 text-indigo-300 font-semibold mb-1">
            <Sparkles size={13} />
            <span>Advisory Model</span>
          </div>
          <p className="text-slate-400 leading-relaxed">
            ML Prediction + ML advisory layer. Deterministic policy enforces a strict 2-attempt ceiling.
          </p>
        </div>
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40 text-xs">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-[11px]">API Target</span>
          <a 
            href={`${API_BASE_URL.replace(/\/$/, '')}/docs`} 
            target="_blank" 
            rel="noreferrer"
            className="flex items-center gap-1 text-indigo-400 hover:text-indigo-300 text-[11px] font-mono hover:underline"
          >
            <span>FastAPI Docs</span>
            <ExternalLink size={11} />
          </a>
        </div>
        <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-800">
          <span>Razorpay Test Mode</span>
          <span className="font-mono">v0.1.0</span>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside className="hidden md:block shrink-0 sticky top-0 h-screen z-40">
        {sidebarContent}
      </aside>

      {/* Mobile Drawer Backdrop */}
      {mobileOpen && (
        <div 
          className="fixed inset-0 bg-slate-950/60 backdrop-blur-xs z-50 md:hidden animate-in fade-in"
          onClick={onCloseMobile}
        >
          <div 
            className="fixed inset-y-0 left-0 max-w-xs w-full shadow-2xl animate-in slide-in-from-left duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
}
