'use client'

import { useState } from 'react'
import { Plus } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { cn } from '@/lib/utils'

interface TaskFormProps {
  onSubmit: (title: string) => Promise<void>
}

export function TaskForm({ onSubmit }: TaskFormProps) {
  const [title, setTitle] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const trimmedTitle = title.trim()

    if (!trimmedTitle) {
      setError('Title is required')
      return
    }

    if (trimmedTitle.length > 500) {
      setError('Title is too long (max 500 characters)')
      return
    }

    setLoading(true)
    setError('')

    try {
      await onSubmit(trimmedTitle)
      setTitle('')
    } catch {
      setError('Failed to create task. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mb-6">
      <div className="flex gap-2">
        <div className="flex-1">
          <input
            type="text"
            value={title}
            onChange={(e) => {
              setTitle(e.target.value)
              if (error) setError('')
            }}
            placeholder="Add a new task..."
            className={cn(
              'w-full px-4 py-2 border rounded-md',
              'text-gray-900 placeholder-gray-400',
              'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
              error ? 'border-red-500' : 'border-gray-300'
            )}
            disabled={loading}
          />
          {error && (
            <p className="text-sm text-red-600 mt-1">{error}</p>
          )}
        </div>
        <Button type="submit" loading={loading} className="shrink-0">
          <Plus className="w-4 h-4 mr-1" />
          Add
        </Button>
      </div>
    </form>
  )
}
