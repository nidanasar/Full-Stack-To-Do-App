'use client'

import { useState, useMemo } from 'react'
import { TaskItem } from './TaskItem'
import { TaskForm } from './TaskForm'
import { TaskFilter } from './TaskFilter'
import { EmptyState } from './EmptyState'
import { tasksApi } from '@/lib/api'
import type { Task, TaskFilter as FilterType } from '@/lib/types'

interface TaskListProps {
  initialTasks: Task[]
}

export function TaskList({ initialTasks }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks)
  const [filter, setFilter] = useState<FilterType>('all')
  const [error, setError] = useState<string | null>(null)

  // Filter tasks based on current filter
  const filteredTasks = useMemo(() => {
    switch (filter) {
      case 'active':
        return tasks.filter(t => !t.completed)
      case 'completed':
        return tasks.filter(t => t.completed)
      default:
        return tasks
    }
  }, [tasks, filter])

  // Calculate counts for filter tabs
  const counts = useMemo(() => ({
    all: tasks.length,
    active: tasks.filter(t => !t.completed).length,
    completed: tasks.filter(t => t.completed).length,
  }), [tasks])

  // Create new task
  const handleCreate = async (title: string) => {
    setError(null)

    const { data, error: apiError } = await tasksApi.create({ title })

    if (apiError) {
      setError(apiError)
      throw new Error(apiError)
    }

    if (data) {
      setTasks(prev => [data, ...prev])
    }
  }

  // Toggle task completion with optimistic update
  const handleToggle = async (id: string, completed: boolean) => {
    setError(null)

    // Optimistic update
    setTasks(prev =>
      prev.map(t => (t.id === id ? { ...t, completed } : t))
    )

    const { error: apiError } = await tasksApi.update(id, { completed })

    if (apiError) {
      // Revert on error
      setTasks(prev =>
        prev.map(t => (t.id === id ? { ...t, completed: !completed } : t))
      )
      setError(apiError)
    }
  }

  // Delete task with optimistic update
  const handleDelete = async (id: string) => {
    setError(null)

    // Store task for potential restoration
    const taskToDelete = tasks.find(t => t.id === id)

    // Optimistic delete
    setTasks(prev => prev.filter(t => t.id !== id))

    const { error: apiError } = await tasksApi.delete(id)

    if (apiError && taskToDelete) {
      // Restore on error
      setTasks(prev => [...prev, taskToDelete])
      setError(apiError)
    }
  }

  return (
    <div>
      <TaskForm onSubmit={handleCreate} />

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {tasks.length > 0 && (
        <TaskFilter
          current={filter}
          onChange={setFilter}
          counts={counts}
        />
      )}

      {filteredTasks.length === 0 ? (
        tasks.length === 0 ? (
          <EmptyState />
        ) : (
          <p className="text-center text-gray-500 py-8">
            No {filter} tasks
          </p>
        )
      ) : (
        <div className="space-y-2">
          {filteredTasks.map(task => (
            <TaskItem
              key={task.id}
              task={task}
              onToggle={handleToggle}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  )
}
