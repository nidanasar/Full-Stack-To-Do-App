import { authApi } from './api'
import type { LoginRequest, RegisterRequest, User } from './types'

/**
 * Auth module for session management
 * Uses httpOnly cookies managed by the backend
 */

/**
 * Sign in with email and password
 * On success, backend sets httpOnly cookie
 */
export async function signIn(credentials: LoginRequest): Promise<{ user?: User; error?: string }> {
  const response = await authApi.login(credentials)

  if (response.error) {
    return { error: response.error }
  }

  return { user: response.data?.user }
}

/**
 * Register new user
 * On success, backend sets httpOnly cookie
 */
export async function signUp(data: RegisterRequest): Promise<{ user?: User; error?: string }> {
  const response = await authApi.register(data)

  if (response.error) {
    return { error: response.error }
  }

  return { user: response.data?.user }
}

/**
 * Sign out current user
 * Backend clears httpOnly cookie
 */
export async function signOut(): Promise<{ error?: string }> {
  const response = await authApi.logout()

  if (response.error) {
    return { error: response.error }
  }

  return {}
}

/**
 * Get current session/user
 * Checks if user is authenticated via /auth/me endpoint
 */
export async function getSession(): Promise<{ user?: User; error?: string }> {
  const response = await authApi.me()

  if (response.error) {
    return { error: response.error }
  }

  return { user: response.data }
}

/**
 * Check if user is authenticated
 * Returns true if session exists
 */
export async function isAuthenticated(): Promise<boolean> {
  const { user } = await getSession()
  return !!user
}
