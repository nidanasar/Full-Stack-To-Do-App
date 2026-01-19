'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { TaskList } from '@/components/tasks/TaskList'
import { TaskListSkeleton } from '@/components/ui/Skeleton'
import { tasksApi } from '@/lib/api'
import { isAuthenticated } from '@/lib/auth'
import type { Task } from '@/lib/types'

export default function TasksPage() {
  const router = useRouter()
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Check auth and fetch tasks
    async function loadTasks() {
      if (!isAuthenticated()) {
        router.push('/login')
        return
      }

      const response = await tasksApi.list()

      if (response.error) {
        if (response.error.includes('401')) {
          router.push('/login')
          return
        }
        setError(response.error)
      } else if (response.data) {
        setTasks(response.data)
      }

      setLoading(false)
    }

    loadTasks()
  }, [router])

  if (loading) {
    return (
      <main className="max-w-2xl mx-auto px-4 py-8">
        <div className="h-8 w-32 bg-gray-200 animate-pulse rounded mb-6" />
        <TaskListSkeleton />
      </main>
    )
  }

  if (error) {
    return (
      <main className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">My Tasks</h1>
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-600">{error}</p>
        </div>
      </main>
    )
  }

  return (
    <main className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">My Tasks</h1>
      <TaskList initialTasks={tasks} />
    </main>
  )
}
