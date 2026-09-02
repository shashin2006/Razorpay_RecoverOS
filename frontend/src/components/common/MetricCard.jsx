import React from 'react';

export default function MetricCard({
  label,
  value,
  subtext,
  icon: Icon,
  variant = 'default', // 'default', 'emerald', 'indigo', 'amber'
  badge = null,
}) {
  const variantStyles = {
    default: {
      iconBg: 'bg-slate-100 text-slate-700',
      valueColor: 'text-slate-900',
      border: 'border-slate-200/80',
    },
    emerald: {
      iconBg: 'bg-emerald-50 text-emerald-700',
      valueColor: 'text-emerald-950',
      border: 'border-emerald-200/60',
    },
    indigo: {
      iconBg: 'bg-indigo-50 text-indigo-700',
      valueColor: 'text-indigo-950',
      border: 'border-indigo-200/60',
    },
    amber: {
      iconBg: 'bg-amber-50 text-amber-700',
      valueColor: 'text-amber-950',
      border: 'border-amber-200/60',
    },
  };

  const style = variantStyles[variant] || variantStyles.default;

  return (
    <div className={`bg-white p-5 rounded-xl border ${style.border} shadow-xs hover:border-slate-300 transition-all duration-150 flex flex-col justify-between`}>
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          {label}
        </span>
        {Icon && (
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${style.iconBg}`}>
            <Icon size={16} strokeWidth={2} />
          </div>
        )}
      </div>

      <div>
        <div className="flex items-baseline gap-2 mb-1">
          <span className={`text-2xl sm:text-3xl font-bold tracking-tight ${style.valueColor}`}>
            {value}
          </span>
          {badge && <span>{badge}</span>}
        </div>
        {subtext && (
          <p className="text-xs text-slate-500 font-medium truncate">
            {subtext}
          </p>
        )}
      </div>
    </div>
  );
}
