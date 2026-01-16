import type {
  ApiResponse,
  Task,
  TaskCreate,
  TaskUpdate,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  User,
} from './types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

/**
 * Fetch wrapper with authentication and error handling
 * Uses credentials: 'include' for httpOnly cookie auth
 */
async function fetchWithAuth<T>(
  endpoint: string,
  options?: RequestInit
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      // Try to parse error message from response
      try {
        const errorData = await response.json()
        return { error: errorData.detail || `Request failed with status ${response.status}` }
      } catch {
        return { error: `Request failed with status ${response.status}` }
      }
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return { data: undefined as T }
    }

    const data = await response.json()
    return { data }
  } catch (err) {
    console.error('API Error:', err)
    return { error: 'Unable to connect. Check your internet connection.' }
  }
}

// ============================================
// Auth API
// ============================================

export const authApi = {
  /**
   * Login with email and password
   */
  login: (credentials: LoginRequest): Promise<ApiResponse<AuthResponse>> =>
    fetchWithAuth<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),

  /**
   * Register new user
   */
  register: (data: RegisterRequest): Promise<ApiResponse<AuthResponse>> =>
    fetchWithAuth<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  /**
   * Logout current user
   */
  logout: (): Promise<ApiResponse<void>> =>
    fetchWithAuth<void>('/auth/logout', {
      method: 'POST',
    }),

  /**
   * Get current user info
   */
  me: (): Promise<ApiResponse<User>> =>
    fetchWithAuth<User>('/auth/me'),
}

// ============================================
// Tasks API
// ============================================

export const tasksApi = {
  /**
   * Get all tasks for the current user
   */
  list: (): Promise<ApiResponse<Task[]>> =>
    fetchWithAuth<Task[]>('/tasks'),

  /**
   * Get a single task by ID
   */
  get: (id: string): Promise<ApiResponse<Task>> =>
    fetchWithAuth<Task>(`/tasks/${id}`),

  /**
   * Create a new task
   */
  create: (data: TaskCreate): Promise<ApiResponse<Task>> =>
    fetchWithAuth<Task>('/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  /**
   * Update a task (partial update)
   */
  update: (id: string, data: TaskUpdate): Promise<ApiResponse<Task>> =>
    fetchWithAuth<Task>(`/tasks/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  /**
   * Delete a task
   */
  delete: (id: string): Promise<ApiResponse<void>> =>
    fetchWithAuth<void>(`/tasks/${id}`, {
      method: 'DELETE',
    }),
}
