import * as api from '@/shared/services/api';
import type { AuthTokens, User, TwoFactorChallenge } from '@/shared/types';
import type { LoginRequest, TwoFactorRequest, ForgotPasswordRequest, ResetPasswordRequest } from '../types/auth.types';

export async function login(data: LoginRequest): Promise<AuthTokens | TwoFactorChallenge> {
  return api.post<AuthTokens | TwoFactorChallenge>('/api/auth/authenticate', data);
}

export async function verify2fa(data: TwoFactorRequest): Promise<AuthTokens> {
  return api.post<AuthTokens>('/api/auth/verify-2fa', data);
}

export async function refreshToken(): Promise<AuthTokens> {
  return api.post<AuthTokens>('/api/auth/refresh', {});
}

export async function logout(): Promise<void> {
  await api.post<void>('/api/auth/logout', {});
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
