export interface LoginRequest {
  email: string;
  password: string;
}

export interface TwoFactorRequest {
  challenge_token: string;
  code: string;
  temp_token?: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  password: string;
}
