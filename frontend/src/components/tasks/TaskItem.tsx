'use client'

import { useState } from 'react'
import { X, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { Task } from '@/lib/types'

interface TaskItemProps {
  task: Task
  onToggle: (id: string, completed: boolean) => Promise<void>
  onDelete: (id: string) => Promise<void>
}

export function TaskItem({ task, onToggle, onDelete }: TaskItemProps) {
  const [isToggling, setIsToggling] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  const handleToggle = async () => {
    setIsToggling(true)
    try {
      await onToggle(task.id, !task.completed)
    } finally {
      setIsToggling(false)
    }
  }

  const handleDelete = async () => {
    setIsDeleting(true)
    try {
      await onDelete(task.id)
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <div
      className={cn(
        'flex items-center gap-3 p-4 border rounded-lg transition-colors',
        'hover:bg-gray-50',
        task.completed ? 'bg-gray-50 border-gray-200' : 'bg-white border-gray-200'
      )}
    >
      <button
        onClick={handleToggle}
        disabled={isToggling}
        className={cn(
          'w-5 h-5 rounded border-2 flex items-center justify-center transition-colors',
          'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
          task.completed
            ? 'bg-blue-600 border-blue-600'
            : 'border-gray-300 hover:border-blue-500'
        )}
        aria-label={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
      >
        {isToggling ? (
          <Loader2 className="w-3 h-3 text-white animate-spin" />
        ) : task.completed ? (
          <svg
            className="w-3 h-3 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={3}
              d="M5 13l4 4L19 7"
            />
          </svg>
        ) : null}
      </button>

      <div className="flex-1 min-w-0">
        <p
          className={cn(
            'text-sm font-medium truncate',
            task.completed ? 'text-gray-400 line-through' : 'text-gray-900'
          )}
        >
          {task.title}
        </p>
        {task.description && (
          <p
            className={cn(
              'text-xs truncate mt-1',
              task.completed ? 'text-gray-300' : 'text-gray-500'
            )}
          >
            {task.description}
          </p>
        )}
      </div>

      <button
        onClick={handleDelete}
        disabled={isDeleting}
        className={cn(
          'p-2 rounded-md transition-colors',
          'text-gray-400 hover:text-red-500 hover:bg-red-50',
          'focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2',
          'disabled:opacity-50 disabled:cursor-not-allowed'
        )}
        aria-label="Delete task"
      >
        {isDeleting ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <X className="w-4 h-4" />
        )}
      </button>
    </div>
  )
}
