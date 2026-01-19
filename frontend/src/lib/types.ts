// User entity from API
export interface User {
  id: string
  email: string
  created_at: string
}

// Task entity from API
export interface Task {
  id: string
  user_id: string
  title: string
  description: string | null
  completed: boolean
  created_at: string
  updated_at: string
}

// For creating new tasks
export interface TaskCreate {
  title: string
  description?: string
}

// For updating tasks (partial)
export interface TaskUpdate {
  title?: string
  description?: string | null
  completed?: boolean
}

// API response wrapper
export interface ApiResponse<T> {
  data?: T
  error?: string
}

// Auth request types
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  name?: string
}

// Auth response from login/register
export interface AuthResponse {
  token: string
  user: User
}

// Task filter options
export type TaskFilter = 'all' | 'active' | 'completed'

// Form error type
export interface FormError {
  field: string
  message: string
}
