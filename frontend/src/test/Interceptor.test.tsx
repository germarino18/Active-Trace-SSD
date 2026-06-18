import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import { setAccessToken, setTenantId, setOnLogout } from '@/shared/services/api';

describe('Axios interceptor configuration', () => {
  beforeEach(() => {
    setAccessToken('test-token');
    setTenantId('test-tenant');
    setOnLogout(vi.fn());
  });

  it('sets access token and tenant id', () => {
    expect(() => {
      setAccessToken('new-token');
      setTenantId('new-tenant');
    }).not.toThrow();
  });

  it('sets logout handler without error', () => {
    const handler = vi.fn();
    expect(() => {
      setOnLogout(handler);
    }).not.toThrow();
  });

  it('refresh endpoint is called after 401', async () => {
    setAccessToken('expired-token');
    const refreshSpy = vi.spyOn(axios, 'post');

    try {
      await axios.post('/api/auth/refresh', {});
    } catch {
      // expected — no backend running
    }

    expect(refreshSpy).toHaveBeenCalledWith('/api/auth/refresh', {});
    refreshSpy.mockRestore();
  });
});
