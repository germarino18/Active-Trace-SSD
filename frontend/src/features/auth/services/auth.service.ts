import * as api from '@/shared/services/api';
import type { AuthTokens, User, TwoFactorChallenge } from '@/shared/types';
import type { LoginRequest, TwoFactorRequest, ForgotPasswordRequest, ResetPasswordRequest } from '../types/auth.types';

export async function login(data: LoginRequest): Promise<AuthTokens | TwoFactorChallenge> {
  return api.post<AuthTokens | TwoFactorChallenge>('/api/auth/authenticate', data);
}

export async function verify2fa(data: TwoFactorRequest): Promise<AuthTokens> {
  // Backend route is /api/auth/login (phase 2), field is totp_code not code
  return api.post<AuthTokens>('/api/auth/login', {
    challenge_token: data.challenge_token,
    totp_code: data.code,
  });
}

export async function refreshToken(): Promise<AuthTokens> {
  return api.post<AuthTokens>('/api/auth/refresh', { refresh_token: api.getRefreshToken() });
}

export async function logout(): Promise<void> {
  const rt = api.getRefreshToken();
  if (rt) {
    await api.post<void>('/api/auth/logout', { refresh_token: rt });
  }
}

export async function forgotPassword(data: ForgotPasswordRequest): Promise<{ message: string }> {
  return api.post<{ message: string }>('/api/auth/forgot', data);
}

export async function resetPassword(data: ResetPasswordRequest): Promise<{ message: string }> {
  return api.post<{ message: string }>('/api/auth/reset', data);
}

export async function getCurrentUser(): Promise<User> {
  return api.get<User>('/api/auth/me');
}
