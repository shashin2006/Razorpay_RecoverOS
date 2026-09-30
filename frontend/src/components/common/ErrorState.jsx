import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

export default function ErrorState({ 
  title = "Unable to load data", 
  message = "An error occurred while connecting to the backend API.", 
  onRetry = null,
  compact = false 
}) {
  return (
    <div 
      className={`rounded-xl border border-rose-200 bg-rose-50/60 p-6 text-center flex flex-col items-center justify-center ${
        compact ? 'py-4' : 'py-8'
      }`}
    >
      <div className="w-10 h-10 rounded-full bg-rose-100 flex items-center justify-center text-rose-600 mb-3">
        <AlertCircle size={20} />
      </div>
      <h4 className="text-sm font-semibold text-rose-950 mb-1">{title}</h4>
      <p className="text-xs text-rose-700 max-w-md mb-4">{message}</p>
      
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium rounded-lg bg-rose-600 text-white hover:bg-rose-700 transition-colors shadow-xs cursor-pointer"
        >
          <RefreshCw size={13} />
          <span>Retry Request</span>
        </button>
      )}
    </div>
  );
}
