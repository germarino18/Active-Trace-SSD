export interface User {
  id: string;
  email: string;
  nombre: string;
  apellido: string;
  roles: string[];
  permissions: string[];
  tenant_id: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
  requires_2fa?: false;
  challenge_token?: null;
}

export interface TwoFactorChallenge {
  requires_2fa: true;
  challenge_token: string;
  temp_token?: string;
}

export type LoginResponse = AuthTokens | TwoFactorChallenge;

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, string[]>;
  };
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export type SessionState =
  | { status: 'loading' }
  | { status: 'unauthenticated' }
  | { status: 'authenticated'; user: User; tokens: AuthTokens };

export interface MenuItem {
  label: string;
  path: string;
  icon: string;
  requiredPermissions?: string[];
  children?: MenuItem[];
}

export interface SidebarSection {
  label?: string;
  items: MenuItem[];
}
