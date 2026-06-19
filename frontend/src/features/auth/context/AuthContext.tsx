import { createContext, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { ReactNode } from 'react';
import type { AuthTokens, SessionState, TwoFactorChallenge, User } from '@/shared/types';
import { setAccessToken, setRefreshToken, getRefreshToken, setTenantId, setOnLogout, setOnTokenRotation } from '@/shared/services/api';
import { setTenantCookie, getTenantCookie, clearTenantCookie, setRefreshTokenCookie, getRefreshTokenCookie, clearRefreshTokenCookie } from '@/shared/utils/tenantCookie';
import * as authService from '../services/auth.service';

interface AuthContextValue {
  session: SessionState;
  login: (email: string, password: string, tenant: string) => Promise<AuthTokens | TwoFactorChallenge>;
  verify2fa: (challengeToken: string, code: string, tempToken?: string) => Promise<void>;
  forgotPassword: (email: string) => Promise<string>;
  resetPassword: (token: string, password: string) => Promise<string>;
  logout: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
  hasAnyPermission: (permissions: string[]) => boolean;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [session, setSession] = useState<SessionState>({ status: 'loading' });
  const tenantRef = useRef<string>('');

  const updateTokens = useCallback((tokens: AuthTokens) => {
    setAccessToken(tokens.access_token);
  }, []);

  const clearSession = useCallback(() => {
    setAccessToken(null);
    setRefreshToken(null);
    setTenantId(null);
    tenantRef.current = '';
    clearTenantCookie();
    clearRefreshTokenCookie();
    setSession({ status: 'unauthenticated' });
  }, []);

  const doLogout = useCallback(async () => {
    try {
      await authService.logout();
    } catch {
      // Ignore logout errors
    }
    clearSession();
  }, [clearSession]);

  useEffect(() => {
    setOnLogout(() => { clearSession(); });
    setOnTokenRotation((newRefreshToken) => {
      setRefreshTokenCookie(newRefreshToken);
    });
  }, [clearSession]);

  useEffect(() => {
    const attemptRefresh = async () => {
      const savedTenant = getTenantCookie();
      const savedRefreshToken = getRefreshTokenCookie();
      if (!savedTenant || !savedRefreshToken) {
        setSession({ status: 'unauthenticated' });
        return;
      }
      tenantRef.current = savedTenant;
      setTenantId(savedTenant);
      setRefreshToken(savedRefreshToken);
      try {
        const tokens = await authService.refreshToken();
        updateTokens(tokens);
        setRefreshToken(tokens.refresh_token);
        setRefreshTokenCookie(tokens.refresh_token);
        const user = await authService.getCurrentUser();
        setSession({ status: 'authenticated', user, tokens });
      } catch {
        clearSession();
      }
    };
    attemptRefresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = useCallback(async (email: string, password: string, tenant: string): Promise<AuthTokens | TwoFactorChallenge> => {
    setTenantId(tenant);
    tenantRef.current = tenant;
    setTenantCookie(tenant);
    const result = await authService.login({ email, password });

    if ('requires_2fa' in result && result.requires_2fa === true) {
      return result;
    }

    const tokens = result as AuthTokens;
    updateTokens(tokens);
    setRefreshToken(tokens.refresh_token);
    setRefreshTokenCookie(tokens.refresh_token);
    const user = await authService.getCurrentUser();
    setSession({ status: 'authenticated', user, tokens });
    return result;
  }, [updateTokens]);

  const verify2faCallback = useCallback(async (challengeToken: string, code: string, tempToken?: string) => {
    const tokens = await authService.verify2fa({ challenge_token: challengeToken, code, temp_token: tempToken });
    updateTokens(tokens);
    setRefreshToken(tokens.refresh_token);
    setRefreshTokenCookie(tokens.refresh_token);
    const user = await authService.getCurrentUser();
    setSession({ status: 'authenticated', user, tokens });
  }, [updateTokens]);

  const forgotPassword = useCallback(async (email: string): Promise<string> => {
    const result = await authService.forgotPassword({ email });
    return result.message ?? 'Si el email existe, recibirá un enlace de recuperación';
  }, []);

  const resetPassword = useCallback(async (token: string, password: string): Promise<string> => {
    const result = await authService.resetPassword({ token, password });
    return result.message ?? 'Contraseña actualizada correctamente';
  }, []);

  const hasPermission = useCallback((permission: string): boolean => {
    if (session.status !== 'authenticated') return false;
    return session.user.permissions.includes(permission);
  }, [session]);

  const hasAnyPermission = useCallback((permissions: string[]): boolean => {
    if (session.status !== 'authenticated') return false;
    return permissions.some((p) => session.user.permissions.includes(p));
  }, [session]);

  const value = useMemo<AuthContextValue>(
    () => ({ session, login, verify2fa: verify2faCallback, forgotPassword, resetPassword, logout: doLogout, hasPermission, hasAnyPermission }),
    [session, login, verify2faCallback, forgotPassword, resetPassword, doLogout, hasPermission, hasAnyPermission],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
