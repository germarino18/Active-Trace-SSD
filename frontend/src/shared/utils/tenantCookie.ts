// Only add Secure flag when served over HTTPS (not localhost dev)
const SECURE = typeof window !== 'undefined' && window.location.protocol === 'https:' ? '; Secure' : '';

function readCookie(name: string): string | null {
  const match = document.cookie
    .split('; ')
    .find((row) => row.startsWith(`${name}=`));
  if (!match) return null;
  return decodeURIComponent(match.split('=').slice(1).join('='));
}

function writeCookie(name: string, value: string): void {
  document.cookie = `${name}=${encodeURIComponent(value)}; SameSite=Strict${SECURE}; path=/`;
}

function deleteCookie(name: string): void {
  document.cookie = `${name}=; SameSite=Strict${SECURE}; path=/; Max-Age=0`;
}

const TENANT_COOKIE = 'js-trace-tenant';
const RT_COOKIE = 'js-trace-rt';

export function setTenantCookie(id: string): void { writeCookie(TENANT_COOKIE, id); }
export function getTenantCookie(): string | null { return readCookie(TENANT_COOKIE); }
export function clearTenantCookie(): void { deleteCookie(TENANT_COOKIE); }

export function setRefreshTokenCookie(token: string): void { writeCookie(RT_COOKIE, token); }
export function getRefreshTokenCookie(): string | null { return readCookie(RT_COOKIE); }
export function clearRefreshTokenCookie(): void { deleteCookie(RT_COOKIE); }
