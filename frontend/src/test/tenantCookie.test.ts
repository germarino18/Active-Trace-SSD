import { describe, it, expect, beforeEach } from 'vitest';
import {
  setTenantCookie, getTenantCookie, clearTenantCookie,
  setRefreshTokenCookie, getRefreshTokenCookie, clearRefreshTokenCookie,
} from '@/shared/utils/tenantCookie';

beforeEach(() => {
  document.cookie = 'js-trace-tenant=; Max-Age=0; path=/';
  document.cookie = 'js-trace-rt=; Max-Age=0; path=/';
});

describe('tenantCookie', () => {
  it('set writes cookie and get reads it back', () => {
    setTenantCookie('acme');
    expect(getTenantCookie()).toBe('acme');
  });

  it('get returns null when cookie is absent', () => {
    expect(getTenantCookie()).toBeNull();
  });

  it('clear removes the cookie', () => {
    setTenantCookie('acme');
    clearTenantCookie();
    expect(getTenantCookie()).toBeNull();
  });

  it('handles tenant IDs with special characters', () => {
    setTenantCookie('tenant=with+special');
    expect(getTenantCookie()).toBe('tenant=with+special');
  });
});

describe('refreshTokenCookie', () => {
  it('set writes cookie and get reads it back', () => {
    setRefreshTokenCookie('tok-abc-123');
    expect(getRefreshTokenCookie()).toBe('tok-abc-123');
  });

  it('get returns null when cookie is absent', () => {
    expect(getRefreshTokenCookie()).toBeNull();
  });

  it('clear removes the cookie', () => {
    setRefreshTokenCookie('tok-abc-123');
    clearRefreshTokenCookie();
    expect(getRefreshTokenCookie()).toBeNull();
  });
});
