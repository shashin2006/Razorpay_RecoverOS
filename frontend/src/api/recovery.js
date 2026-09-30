import { apiClient } from './client.js';

/**
 * Fetch list of recovery cases
 * GET /api/recovery/cases
 * Returns { cases: [...], total: number }
 */
export async function getRecoveryCases() {
  return await apiClient('/api/recovery/cases');
}

/**
 * Fetch a single recovery case by ID
 * GET /api/recovery/cases/{id}
 */
export async function getRecoveryCaseById(caseId) {
  if (!caseId) {
    return { ok: false, error: 'Case ID is required', data: null };
  }
  return await apiClient(`/api/recovery/cases/${caseId}`);
}

/**
 * Fetch audit trail events for a recovery case
 * GET /api/recovery/cases/{id}/audit
 */
export async function getRecoveryCaseAudit(caseId) {
  if (!caseId) {
    return { ok: false, error: 'Case ID is required', data: null };
  }
  return await apiClient(`/api/recovery/cases/${caseId}/audit`);
}
