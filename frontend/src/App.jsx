import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/layout/Sidebar.jsx';
import Header from './components/layout/Header.jsx';
import Dashboard from './pages/Dashboard.jsx';
import RecoveryCasesPage from './pages/RecoveryCasesPage.jsx';
import AIPolicyPage from './pages/AIPolicyPage.jsx';
import MLMonitoringPage from './pages/MLMonitoringPage.jsx';
import AuditTrailPage from './pages/AuditTrailPage.jsx';
import RecoveryCaseDrawer from './components/recovery/RecoveryCaseDrawer.jsx';
import AgentConfirmationModal from './components/recovery/AgentConfirmationModal.jsx';

import { 
  getRecoveryMetrics, 
  getMLEvaluation, 
  getProbabilityBuckets, 
  getDecisionAgreement 
} from './api/ml.js';
import { getRecoveryCases, getRecoveryCaseById } from './api/recovery.js';
import { triggerAgentRecovery } from './api/agent.js';
import { checkBackendHealth, API_BASE_URL } from './api/client.js';
import { CheckCircle2, AlertCircle, Menu, X, ShieldAlert } from 'lucide-react';
import { normalizeCase } from './utils/formatting.js';

export default function App() {
  const [currentTab, setCurrentTab] = useState('overview');
  const [metrics, setMetrics] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [buckets, setBuckets] = useState([]);
  const [agreement, setAgreement] = useState(null);
  const [cases, setCases] = useState([]);
  const [totalCasesCount, setTotalCasesCount] = useState(0);
  
  const [backendStatus, setBackendStatus] = useState('connecting');
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [casesError, setCasesError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Selected case for side drawer
  const [selectedCase, setSelectedCase] = useState(null);
  // Case pending agent execution confirmation
  const [confirmModalCase, setConfirmModalCase] = useState(null);
  const [isExecutingAgent, setIsExecutingAgent] = useState(false);
  const [agentExecutionError, setAgentExecutionError] = useState(null);
  const [agentExecutionResult, setAgentExecutionResult] = useState(null);

  // Notification Banner
  const [notification, setNotification] = useState(null);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  const showToast = (type, message) => {
    setNotification({ type, message });
    setTimeout(() => {
      setNotification(prev => (prev?.message === message ? null : prev));
    }, 6000);
  };

  const loadData = useCallback(async (isManualRefresh = false) => {
    if (isManualRefresh) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }

    let coreCasesOk = false;
    let coreMetricsOk = false;
    let optionalFailuresCount = 0;

    try {
      // 1. Fetch Recovery Cases (GET /api/recovery/cases) - Core Endpoint
      const casesRes = await getRecoveryCases();
      if (casesRes.ok && casesRes.data) {
        const loadedCases = Array.isArray(casesRes.data)
          ? casesRes.data
          : (casesRes.data.cases || []);
        const total = casesRes.data.total ?? loadedCases.length;
        setCases(loadedCases);
        setTotalCasesCount(total);
        setCasesError(null);
        coreCasesOk = true;
      } else {
        setCases([]);
        setTotalCasesCount(0);
        setCasesError(casesRes.error || 'Failed to load recovery cases');
      }

      // 2. Fetch ML Recovery Metrics (GET /api/ml/recovery-metrics) - Core Endpoint
      const metricsRes = await getRecoveryMetrics();
      if (metricsRes.ok && metricsRes.data) {
        setMetrics(metricsRes.data);
        setError(null);
        coreMetricsOk = true;
      } else {
        setMetrics(null);
        setError(metricsRes.error || 'Failed to connect to backend recovery metrics');
      }

      // 3. Fetch Evaluation (GET /api/ml/evaluation) - Advisory/Telemetry
      const evalRes = await getMLEvaluation();
      if (evalRes.ok && evalRes.data) {
        setEvaluation(evalRes.data);
      } else {
        setEvaluation(null);
        optionalFailuresCount++;
      }

      // 4. Fetch Probability Buckets (GET /api/ml/probability-buckets) - Advisory/Telemetry
      const bucketsRes = await getProbabilityBuckets();
      if (bucketsRes.ok && bucketsRes.data) {
        setBuckets(Array.isArray(bucketsRes.data) ? bucketsRes.data : (bucketsRes.data?.buckets || []));
      } else {
        setBuckets([]);
        optionalFailuresCount++;
      }

      // 5. Fetch Decision Agreement (GET /api/ml/decision-agreement) - Advisory/Telemetry
      const agreeRes = await getDecisionAgreement();
      if (agreeRes.ok && agreeRes.data) {
        setAgreement(agreeRes.data);
      } else {
        setAgreement(null);
        optionalFailuresCount++;
      }

      // 6. Authoritative Connection State Calculation
      if (coreCasesOk && coreMetricsOk) {
        setBackendStatus(optionalFailuresCount > 0 ? 'partially_unavailable' : 'connected');
      } else if (coreCasesOk || coreMetricsOk) {
        setBackendStatus('partially_unavailable');
      } else {
        setBackendStatus('unavailable');
      }

      setLastUpdated(new Date());
    } catch (err) {
      console.error('Data load error:', err);
      setBackendStatus('unavailable');
      setError('Unable to establish connection with FastAPI backend at ' + API_BASE_URL);
      setCasesError('Backend unreachable');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    loadData();

    // Polling interval every 30s
    const interval = setInterval(() => {
      loadData(true);
    }, 30000);

    return () => clearInterval(interval);
  }, [loadData]);

  // Handle running the recovery agent
  const handleOpenAgentConfirm = (caseItem) => {
    const normalized = normalizeCase(caseItem) || caseItem;
    setConfirmModalCase(normalized);
    setAgentExecutionError(null);
    setAgentExecutionResult(null);
  };

  const handleExecuteAgent = async () => {
    if (!confirmModalCase) return;
    setIsExecutingAgent(true);
    setAgentExecutionError(null);
    setAgentExecutionResult(null);

    // Guaranteed resolved case ID according to backend schema (detail.case.id)
    const caseId = confirmModalCase.case?.id ?? confirmModalCase.id;
    if (!caseId) {
      setAgentExecutionError("Recovery Case ID is required.");
      setIsExecutingAgent(false);
      return;
    }

    try {
      // 1. Send the agent request: POST /api/agent/recovery/{caseId}
      const res = await triggerAgentRecovery(caseId);

      if (res.ok) {
        const resultData = res.data || {};
        setAgentExecutionResult(resultData);
        showToast('success', `Recovery agent executed for Case #${caseId}.`);

        // 2. Authoritative Re-fetch: GET /api/recovery/cases/{caseId}
        try {
          const freshCaseRes = await getRecoveryCaseById(caseId);
          if (freshCaseRes.ok && freshCaseRes.data) {
            const freshNorm = normalizeCase(freshCaseRes.data) || freshCaseRes.data;
            // Update modal state and selected drawer case with fresh authoritative backend record
            setConfirmModalCase(freshNorm);
            setSelectedCase(prev => (prev && (prev.id === caseId || prev.case?.id === caseId) ? freshNorm : prev));
          }
        } catch {
          // Keep current state if single case fetch fails
        }

        // 3. Reload fresh dashboard metrics and cases list from backend
        loadData(true);
      } else {
        const errorMsg = res.error || "Recovery action could not be executed.";
        setAgentExecutionError(errorMsg);
        showToast('error', `Recovery action could not be executed: ${errorMsg}`);
      }
    } catch (err) {
      const errorMsg = err.message || "Execution failed due to an unexpected error.";
      setAgentExecutionError(errorMsg);
      showToast('error', errorMsg);
    } finally {
      setIsExecutingAgent(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900">
      {/* Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        casesCount={cases.length}
        mobileOpen={mobileSidebarOpen}
        onCloseMobile={() => setMobileSidebarOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile Header Toggle */}
        <div className="md:hidden flex items-center justify-between p-4 bg-slate-900 text-white border-b border-slate-800">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setMobileSidebarOpen(true)}
              className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white cursor-pointer"
            >
              <Menu size={20} />
            </button>
            <span className="font-bold text-sm tracking-tight">RecoveryOS</span>
          </div>
          <span className="text-[11px] font-mono text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-800">
            Razorpay Test Mode
          </span>
        </div>

        {/* Global Header */}
        <Header
          backendStatus={backendStatus}
          lastUpdated={lastUpdated}
          isRefreshing={isRefreshing}
          onRefresh={() => loadData(true)}
        />

        {/* Toast / Notification Banner */}
        {notification && (
          <div className="px-4 sm:px-6 lg:px-8 pt-4 max-w-7xl mx-auto w-full">
            <div 
              className={`p-3.5 rounded-xl border flex items-center justify-between gap-3 text-xs shadow-sm animate-in slide-in-from-top-2 duration-150 ${
                notification.type === 'success' 
                  ? 'bg-emerald-50 border-emerald-200 text-emerald-900' 
                  : 'bg-rose-50 border-rose-200 text-rose-900'
              }`}
            >
              <div className="flex items-center gap-2.5">
                {notification.type === 'success' ? (
                  <CheckCircle2 size={16} className="text-emerald-600 shrink-0" />
                ) : (
                  <ShieldAlert size={16} className="text-rose-600 shrink-0" />
                )}
                <span className="font-medium">{notification.message}</span>
              </div>
              <button 
                onClick={() => setNotification(null)}
                className="text-slate-400 hover:text-slate-600 p-1 cursor-pointer"
              >
                <X size={14} />
              </button>
            </div>
          </div>
        )}

        {/* Page Content Body */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto">
          {currentTab === 'overview' && (
            <Dashboard
              metrics={metrics}
              cases={cases}
              isLoading={isLoading}
              error={error}
              onRetry={() => loadData(true)}
              onSelectCase={setSelectedCase}
              onRunAgent={handleOpenAgentConfirm}
              onNavigateTab={setCurrentTab}
            />
          )}

          {currentTab === 'cases' && (
            <RecoveryCasesPage
              cases={cases}
              metrics={metrics}
              isLoading={isLoading}
              error={casesError}
              onRetry={() => loadData(true)}
              onSelectCase={setSelectedCase}
              onRunAgent={handleOpenAgentConfirm}
            />
          )}

          {currentTab === 'ai-policy' && (
            <AIPolicyPage
              agreement={agreement}
              isLoading={isLoading}
            />
          )}

          {currentTab === 'ml-monitoring' && (
            <MLMonitoringPage
              metrics={metrics}
              evaluation={evaluation}
              buckets={buckets}
              agreement={agreement}
              isLoading={isLoading}
            />
          )}

          {currentTab === 'audit-trail' && (
            <AuditTrailPage
              cases={cases}
              isLoading={isLoading}
            />
          )}
        </main>
      </div>

      {/* Case Details Drawer */}
      <RecoveryCaseDrawer
        recoveryCase={selectedCase}
        isOpen={Boolean(selectedCase)}
        onClose={() => setSelectedCase(null)}
        onRunAgent={(caseItem) => {
          setConfirmModalCase(caseItem);
        }}
        isExecuting={isExecutingAgent}
      />

      {/* Agent Execution Confirmation Modal */}
      <AgentConfirmationModal
        recoveryCase={confirmModalCase}
        isOpen={Boolean(confirmModalCase)}
        isExecuting={isExecutingAgent}
        executionError={agentExecutionError}
        executionResult={agentExecutionResult}
        onConfirm={handleExecuteAgent}
        onClose={() => {
          setConfirmModalCase(null);
          setAgentExecutionError(null);
          setAgentExecutionResult(null);
        }}
        onViewDetails={(caseItem) => {
          setSelectedCase(caseItem);
        }}
      />
    </div>
  );
}
