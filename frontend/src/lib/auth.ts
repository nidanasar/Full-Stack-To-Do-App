import { authApi, setToken, clearToken, getToken } from './api'
import type { LoginRequest, RegisterRequest, User } from './types'

/**
 * Auth module for session management
 * Uses JWT token stored in localStorage
 */

/**
 * Sign in with email and password
 * On success, stores JWT token
 */
export async function signIn(credentials: LoginRequest): Promise<{ user?: User; error?: string }> {
  const response = await authApi.login(credentials)

  if (response.error) {
    return { error: response.error }
  }

  if (response.data?.token) {
    setToken(response.data.token)
  }

  return { user: response.data?.user }
}

/**
 * Register new user
 * On success, stores JWT token
 */
export async function signUp(data: RegisterRequest): Promise<{ user?: User; error?: string }> {
  const response = await authApi.register(data)

  if (response.error) {
    return { error: response.error }
  }

  if (response.data?.token) {
    setToken(response.data.token)
  }

  return { user: response.data?.user }
}

/**
 * Sign out current user
 * Clears stored JWT token
 */
export async function signOut(): Promise<{ error?: string }> {
  clearToken()
  return {}
}

/**
 * Get current session/user
 * Checks if user is authenticated via /auth/me endpoint
 */
export async function getSession(): Promise<{ user?: User; error?: string }> {
  const token = getToken()
  if (!token) {
    return { error: 'No token' }
  }

  const response = await authApi.me()

  if (response.error) {
    return { error: response.error }
  }

  return { user: response.data }
}

/**
 * Check if user is authenticated
 * Returns true if token exists
 */
export function isAuthenticated(): boolean {
  return !!getToken()
}
