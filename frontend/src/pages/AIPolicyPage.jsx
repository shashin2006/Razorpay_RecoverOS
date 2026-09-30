import React from 'react';
import { 
  ShieldCheck, 
  Sparkles, 
  Cpu, 
  RotateCcw, 
  ShieldAlert, 
  CheckCircle2, 
  ArrowDown, 
  Lock, 
  CreditCard,
  Layers,
  FileCheck2,
  AlertTriangle
} from 'lucide-react';
import PolicyAgreementMatrix from '../components/ml/PolicyAgreementMatrix.jsx';

export default function AIPolicyPage({ agreement = null, isLoading = false }) {
  const steps = [
    {
      step: 1,
      title: "ML / AI Advisory Layer",
      badge: "Statistical & Non-Authoritative",
      badgeColor: "bg-indigo-50 text-indigo-700 border-indigo-200",
      icon: Sparkles,
      iconBg: "bg-indigo-100 text-indigo-700",
      description: "Machine learning models evaluate failure category, customer history, and transient signals to produce a recovery probability score and action recommendation.",
      highlight: "AI only suggests; it possesses ZERO direct execution authority."
    },
    {
      step: 2,
      title: "Deterministic Recovery Policy",
      badge: "Authoritative Rule Engine",
      badgeColor: "bg-teal-50 text-teal-700 border-teal-200",
      icon: ShieldCheck,
      iconBg: "bg-teal-100 text-teal-700",
      description: "The core business policy rules verify case eligibility, past transaction history, failure code permanence, and merchant risk parameters.",
      highlight: "Enforces non-negotiable compliance rules and failure categorization."
    },
    {
      step: 3,
      title: "Policy Safety Gate (Ceiling Enforcer)",
      badge: "Hard 2-Attempt Boundary",
      badgeColor: "bg-amber-50 text-amber-800 border-amber-200",
      icon: Lock,
      iconBg: "bg-amber-100 text-amber-800",
      description: "Strict limit of 2 automated recovery attempts per case. Even if the ML model recommends continued retries, the safety gate forcibly blocks execution when attempts = 2.",
      highlight: "Guarantees zero infinite loops and protects customer trust."
    },
    {
      step: 4,
      title: "Bounded Action Executor",
      badge: "Sandboxed Tool Dispatch",
      badgeColor: "bg-slate-100 text-slate-800 border-slate-200",
      icon: Cpu,
      iconBg: "bg-slate-200 text-slate-800",
      description: "Dispatches only predefined, bounded actions (e.g. create Razorpay Test Mode alternate payment link, trigger WhatsApp notification, or escalate to manual support).",
      highlight: "Never performs unverified debiting or arbitrary account changes."
    },
    {
      step: 5,
      title: "Outcome Recording & Audit Trail",
      badge: "Immutable Verification",
      badgeColor: "bg-emerald-50 text-emerald-800 border-emerald-200",
      icon: CheckCircle2,
      iconBg: "bg-emerald-100 text-emerald-800",
      description: "Listens for Razorpay webhook confirmations. Cases are only marked 'Recovered' when captured funds are mathematically verified.",
      highlight: "Telemetry is fed back into ML calibration to refine future precision."
    }
  ];

  return (
    <div className="space-y-6 pb-12 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">
            AI & Deterministic Policy Safety
          </h1>
          <span className="px-2 py-0.5 text-xs font-semibold bg-indigo-50 text-indigo-700 rounded border border-indigo-200">
            Governance Framework
          </span>
        </div>
        <p className="text-xs sm:text-sm text-slate-500 mt-0.5 max-w-3xl leading-relaxed">
          How RecoveryOS balances probabilistic machine intelligence with strict, non-negotiable financial policy boundaries.
        </p>
      </div>

      {/* CORE ARCHITECTURAL PIPELINE DIAGRAM */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-xs space-y-6">
        <div className="border-b border-slate-200/80 pb-3 flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
            Safety Execution Hierarchy
          </h2>
          <span className="text-xs text-slate-500 font-mono">
            FastAPI Authoritative Backend
          </span>
        </div>

        <div className="relative space-y-4">
          {steps.map((s, idx) => {
            const Icon = s.icon;
            const isLast = idx === steps.length - 1;

            return (
              <div key={s.step} className="flex flex-col items-center">
                <div className="w-full bg-slate-50/80 hover:bg-slate-100/60 transition-all rounded-xl p-5 border border-slate-200/80 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-start gap-4">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-2xs ${s.iconBg}`}>
                      <Icon size={20} />
                    </div>
                    <div className="space-y-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-bold text-sm text-slate-900">
                          {s.step}. {s.title}
                        </span>
                        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${s.badgeColor}`}>
                          {s.badge}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed max-w-2xl">
                        {s.description}
                      </p>
                    </div>
                  </div>

                  <div className="md:text-right shrink-0">
                    <span className="inline-block text-[11px] font-medium text-slate-700 bg-white px-3 py-1.5 rounded-lg border border-slate-200 shadow-2xs">
                      {s.highlight}
                    </span>
                  </div>
                </div>

                {!isLast && (
                  <div className="py-2 flex items-center justify-center text-slate-300">
                    <ArrowDown size={18} className="text-slate-400" />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* POLICY vs ML AGREEMENT MATRIX */}
      <PolicyAgreementMatrix agreement={agreement} isLoading={isLoading} />

      {/* SAFETY RULES SUMMARY TABLE */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-2xs space-y-2">
          <div className="flex items-center gap-2 text-slate-900 font-bold">
            <RotateCcw size={16} className="text-amber-600" />
            <span>2-Attempt Hard Ceiling</span>
          </div>
          <p className="text-slate-600 leading-relaxed">
            RecoveryOS strictly caps automated attempts to 2 per incident. Upon reaching attempt 2 without resolution, cases are automatically locked and escalated to human support.
          </p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-2xs space-y-2">
          <div className="flex items-center gap-2 text-slate-900 font-bold">
            <Lock size={16} className="text-teal-600" />
            <span>Zero Unbounded Tools</span>
          </div>
          <p className="text-slate-600 leading-relaxed">
            The AI recovery agent can only invoke declarative tools exposed by the backend schema (such as creating customer payment links). Arbitrary database writes or debit actions are impossible.
          </p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-2xs space-y-2">
          <div className="flex items-center gap-2 text-slate-900 font-bold">
            <FileCheck2 size={16} className="text-emerald-600" />
            <span>Audited & Verified</span>
          </div>
          <p className="text-slate-600 leading-relaxed">
            A case is never flagged as "Recovered" when a link is generated. Only upon the arrival and signature validation of a Razorpay capture webhook is revenue mathematically recognized.
          </p>
        </div>
      </div>
    </div>
  );
}
