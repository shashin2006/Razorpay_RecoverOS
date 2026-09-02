/**
 * Centralized API client for RecoveryOS
 * Connects directly to the FastAPI backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export { API_BASE_URL };

export async function apiClient(endpoint, options = {}) {
  const url = `${API_BASE_URL.replace(/\/$/, '')}/${endpoint.replace(/^\//, '')}`;
  const timeoutMs = options.timeout || 8000;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    ...(options.headers || {}),
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    let data = null;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      data = await response.json().catch(() => null);
    } else {
      const text = await response.text().catch(() => '');
      data = text ? { message: text } : null;
    }

    if (!response.ok) {
      let errorMessage = `Request failed with status ${response.status}`;
      if (typeof data?.detail === 'string') {
        errorMessage = data.detail;
      } else if (data?.detail && typeof data.detail === 'object') {
        errorMessage = Array.isArray(data.detail)
          ? data.detail.map(d => (d.msg ? `${d.loc ? d.loc.join('.') + ': ' : ''}${d.msg}` : JSON.stringify(d))).join('; ')
          : (data.detail.error || data.detail.message || JSON.stringify(data.detail));
      } else if (typeof data?.error === 'string') {
        errorMessage = data.error;
      } else if (typeof data?.message === 'string') {
        errorMessage = data.message;
      } else if (typeof data?.description === 'string') {
        errorMessage = data.description;
      }

      return {
        ok: false,
        status: response.status,
        error: errorMessage,
        data: data || null,
      };
    }

    return {
      ok: true,
      status: response.status,
      data,
      error: null,
    };
  } catch (err) {
    clearTimeout(timeoutId);
    let errorMessage = 'Network error: Backend server is unreachable';
    if (err.name === 'AbortError') {
      const seconds = Math.round(timeoutMs / 1000);
      errorMessage = `Request timed out after ${seconds} seconds`;
    } else if (err.message) {
      errorMessage = err.message;
    }

    return {
      ok: false,
      status: 0,
      error: errorMessage,
      data: null,
      isNetworkError: true,
    };
  }
}

/**
 * Health check to test if FastAPI backend is reachable.
 * Uses core recovery cases endpoint with a 6-second budget.
 */
export async function checkBackendHealth() {
  try {
    const res = await apiClient('/api/recovery/cases', { timeout: 6000 });
    return res.ok || res.status === 200 || res.status === 404;
  } catch {
    return false;
  }
}
