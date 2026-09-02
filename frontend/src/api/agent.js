import { apiClient } from './client.js';

/**
 * Triggers the recovery agent for a specific recovery case.
 * POST /api/agent/recovery/{recovery_case_id}
 * 
 * Safety:
 * - Deterministic policy evaluates whether action is bounded & approved.
 * - Maximum 2 automated attempts strictly enforced.
 */
export async function triggerAgentRecovery(recoveryCaseId) {
  if (!recoveryCaseId) {
    return { ok: false, error: 'Recovery Case ID is required.', status: 400 };
  }

  const response = await apiClient(`/api/agent/recovery/${recoveryCaseId}`, {
    method: 'POST',
    timeout: 30000,
  });

  return response;
}
