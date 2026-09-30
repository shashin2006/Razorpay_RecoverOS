import { apiClient } from './client.js';

/**
 * Fetch recovery metrics from FastAPI backend
 * GET /api/ml/recovery-metrics
 */
export async function getRecoveryMetrics() {
  return await apiClient('/api/ml/recovery-metrics');
}

/**
 * Fetch ML evaluation & performance metrics
 * GET /api/ml/evaluation
 */
export async function getMLEvaluation() {
  return await apiClient('/api/ml/evaluation');
}

/**
 * Fetch ML probability bucket distribution
 * GET /api/ml/probability-buckets
 */
export async function getProbabilityBuckets() {
  return await apiClient('/api/ml/probability-buckets');
}

/**
 * Fetch ML recommendation vs deterministic policy agreement stats
 * GET /api/ml/decision-agreement
 */
export async function getDecisionAgreement() {
  return await apiClient('/api/ml/decision-agreement');
}

/**
 * Fetch combined ML dashboard
 * GET /api/ml/dashboard
 */
export async function getMLDashboard() {
  return await apiClient('/api/ml/dashboard');
}
