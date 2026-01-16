import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { TaskList } from '@/components/tasks/TaskList'
import type { Task } from '@/lib/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

async function getTasks(): Promise<{ tasks: Task[]; needsAuth: boolean }> {
  const cookieStore = await cookies()
  const allCookies = cookieStore.getAll()
  const cookieHeader = allCookies
    .map(c => `${c.name}=${c.value}`)
    .join('; ')

  try {
    const response = await fetch(`${API_BASE}/tasks`, {
      headers: {
        'Content-Type': 'application/json',
        'Cookie': cookieHeader,
      },
      cache: 'no-store',
    })

    if (response.status === 401) {
      return { tasks: [], needsAuth: true }
    }

    if (!response.ok) {
      return { tasks: [], needsAuth: false }
    }

    const tasks = await response.json()
    return { tasks, needsAuth: false }
  } catch (error) {
    console.error('Failed to fetch tasks:', error)
    return { tasks: [], needsAuth: false }
  }
}

export const metadata = {
  title: 'My Tasks - Todo App',
  description: 'Manage your tasks',
}

export default async function TasksPage() {
  const { tasks, needsAuth } = await getTasks()

  if (needsAuth) {
    redirect('/login')
  }

  return (
    <main className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">My Tasks</h1>
      <TaskList initialTasks={tasks} />
    </main>
  )
}
