import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

interface PendingRequest {
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}

let accessToken: string | null = null;
let refreshToken: string | null = null;
let tenantId: string | null = null;
let isRefreshing = false;
let pendingRequests: PendingRequest[] = [];
let onLogout: (() => void) | null = null;
let onTokenRotation: ((newRefreshToken: string) => void) | null = null;

export function setAccessToken(token: string | null) { accessToken = token; }
export function setRefreshToken(token: string | null) { refreshToken = token; }
export function getRefreshToken(): string | null { return refreshToken; }
export function setTenantId(id: string | null) { tenantId = id; }
export function setOnLogout(handler: () => void) { onLogout = handler; }
export function setOnTokenRotation(handler: (newRefreshToken: string) => void) {
  onTokenRotation = handler;
}

const api = axios.create({
  baseURL: '',
  timeout: 30000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    if (tenantId && config.headers) {
      config.headers['X-Tenant-ID'] = tenantId;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        pendingRequests.push({ resolve, reject });
      }).then((token) => {
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${token}`;
        }
        return api(originalRequest);
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const response = await axios.post<{ access_token: string; refresh_token?: string }>(
        '/api/auth/refresh',
        { refresh_token: refreshToken },
        { headers: { 'X-Tenant-ID': tenantId ?? '' } },
      );

      const newToken = response.data.access_token;
      setAccessToken(newToken);
      if (response.data.refresh_token) {
        setRefreshToken(response.data.refresh_token);
        onTokenRotation?.(response.data.refresh_token);
      }

      pendingRequests.forEach((p) => p.resolve(newToken));
      pendingRequests = [];

      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
      }
      return api(originalRequest);
    } catch (refreshError) {
      pendingRequests.forEach((p) => p.reject(refreshError));
      pendingRequests = [];
      setAccessToken(null);
      onLogout?.();
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  },
);

export async function get<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  const response = await api.get<T>(url, { params });
  return response.data;
}

export async function post<T>(url: string, data?: unknown): Promise<T> {
  const response = await api.post<T>(url, data);
  return response.data;
}

export async function put<T>(url: string, data?: unknown): Promise<T> {
  const response = await api.put<T>(url, data);
  return response.data;
}

export async function patch<T>(url: string, data?: unknown): Promise<T> {
  const response = await api.patch<T>(url, data);
  return response.data;
}

export async function del<T>(url: string): Promise<T> {
  const response = await api.delete<T>(url);
  return response.data;
}

/**
 * Downloads a file via authenticated GET (auth header attached by request interceptor).
 * Reads the Content-Disposition header for the filename; falls back to the provided filename arg.
 * This is required for endpoints that return CSV attachments behind JWT auth —
 * a plain <a href> would download a 401 JSON instead of the real file.
 */
export async function download(url: string, filename: string): Promise<void> {
  const response = await api.get<Blob>(url, { responseType: 'blob' });

  // Try to extract filename from Content-Disposition: attachment; filename="foo.csv"
  const disposition = response.headers['content-disposition'] as string | undefined;
  let resolvedFilename = filename;
  if (disposition) {
    const match = disposition.match(/filename[^;=\n]*=["']?([^"';\n]+)["']?/i);
    if (match?.[1]) resolvedFilename = match[1].trim();
  }

  const objectUrl = URL.createObjectURL(response.data);
  const anchor = document.createElement('a');
  anchor.href = objectUrl;
  anchor.download = resolvedFilename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(objectUrl);
}

/**
 * Uploads a FormData payload via multipart POST.
 * Lets axios set the Content-Type (including the multipart boundary) automatically.
 */
export async function upload<T>(url: string, formData: FormData): Promise<T> {
  const response = await api.post<T>(url, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export default api;
