import React from 'react';

export function SkeletonBox({ className = '' }) {
  return (
    <div className={`animate-pulse bg-slate-200/80 rounded ${className}`} />
  );
}

export function MetricCardSkeleton() {
  return (
    <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs flex flex-col justify-between h-32">
      <div className="flex items-center justify-between">
        <SkeletonBox className="h-4 w-28" />
        <SkeletonBox className="h-8 w-8 rounded-lg" />
      </div>
      <div>
        <SkeletonBox className="h-8 w-36 mb-2" />
        <SkeletonBox className="h-3 w-20" />
      </div>
    </div>
  );
}

export function TableRowSkeleton({ columns = 6 }) {
  return (
    <tr className="border-b border-slate-100">
      {Array.from({ length: columns }).map((_, i) => (
        <td key={i} className="py-3.5 px-4">
          <SkeletonBox className={`h-4 ${i === 0 ? 'w-20' : i === 1 ? 'w-28' : 'w-16'}`} />
        </td>
      ))}
    </tr>
  );
}
