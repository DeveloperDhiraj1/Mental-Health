const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
const REQUEST_TIMEOUT_MS = 12000;
let accessToken = sessionStorage.getItem('mindscope_access_token') || '';

class ApiError extends Error {
  constructor(message, status = 0) { super(message); this.name = 'ApiError'; this.status = status; }
}

async function request(path, options = {}) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const headers = new Headers(options.headers || {});
    if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`);
    const response = await fetch(`${API_BASE}${path}`, { ...options, headers, signal: controller.signal });
    let payload = null;
    try { payload = await response.json(); } catch { /* handled as an invalid response */ }
    if (!response.ok) {
      const detail = typeof payload?.detail === 'string' ? payload.detail : '';
      throw new ApiError(detail || `Request failed (${response.status})`, response.status);
    }
    return payload;
  } catch (error) {
    if (error.name === 'AbortError') throw new ApiError('The request timed out. Check that the backend is running.');
    if (error instanceof ApiError) throw error;
    throw new ApiError('The backend could not be reached. Check the API URL and server status.');
  } finally { window.clearTimeout(timeout); }
}

function validateModelInfo(payload) {
  if (!payload || typeof payload.available !== 'boolean') throw new ApiError('The backend returned an invalid model-status response.');
  return payload;
}

function validateBatchResponse(payload) {
  if (!Array.isArray(payload)) throw new ApiError('The backend returned an invalid analysis response.');
  return payload.map((item) => ({
    available: Boolean(item?.available),
    experimental: Boolean(item?.experimental),
    message: typeof item?.message === 'string' ? item.message : '',
    labels: Array.isArray(item?.labels) ? item.labels.filter((label) => typeof label === 'string') : [],
  }));
}

export const api = {
  baseUrl: API_BASE,
  setToken(token) { accessToken = token || ''; if (accessToken) sessionStorage.setItem('mindscope_access_token', accessToken); else sessionStorage.removeItem('mindscope_access_token'); },
  hasToken() { return Boolean(accessToken); },
  async modelInfo() { return validateModelInfo(await request('/api/v1/model/info')); },
  async batchPredict(texts) {
    return validateBatchResponse(await request('/api/v1/predictions/batch', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ texts }),
    }));
  },
  async register(email, password) { const result = await request('/api/v1/auth/register', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) }); this.setToken(result.access_token); return result.user; },
  async login(email, password) { const result = await request('/api/v1/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) }); this.setToken(result.access_token); return result.user; },
  async me() { return request('/api/v1/auth/me'); },
  async logout() { try { await request('/api/v1/auth/logout', { method: 'POST' }); } finally { this.setToken(''); } },
  uploadImages(files, onProgress = () => {}) {
    return new Promise((resolve, reject) => {
      const request = new XMLHttpRequest();
      request.open('POST', `${API_BASE}/api/v1/image-analysis`);
      request.timeout = REQUEST_TIMEOUT_MS;
      request.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) onProgress(Math.round((event.loaded / event.total) * 100));
      });
      request.addEventListener('load', () => {
        let payload = null;
        try { payload = JSON.parse(request.responseText); } catch { /* handled below */ }
        if (request.status >= 200 && request.status < 300) return resolve(payload);
        const detail = typeof payload?.detail === 'string' ? payload.detail : `Request failed (${request.status})`;
        reject(new ApiError(detail, request.status));
      });
      request.addEventListener('error', () => reject(new ApiError('The backend could not be reached. Check the API URL and server status.')));
      request.addEventListener('timeout', () => reject(new ApiError('The upload timed out. Check that the backend is running.')));
      const form = new FormData();
      files.forEach((file) => form.append('files', file, file.name));
      request.send(form);
    });
  },
};

export { ApiError };
