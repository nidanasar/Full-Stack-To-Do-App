'use client'

import { cn } from '@/lib/utils'
import type { TaskFilter as FilterType } from '@/lib/types'

interface TaskFilterProps {
  current: FilterType
  onChange: (filter: FilterType) => void
  counts: {
    all: number
    active: number
    completed: number
  }
}

const filters: { value: FilterType; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'active', label: 'Active' },
  { value: 'completed', label: 'Completed' },
]

export function TaskFilter({ current, onChange, counts }: TaskFilterProps) {
  return (
    <div className="flex items-center gap-2 mb-4">
      {filters.map(({ value, label }) => (
        <button
          key={value}
          onClick={() => onChange(value)}
          className={cn(
            'px-3 py-1.5 rounded-full text-sm font-medium transition-colors',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
            current === value
              ? 'bg-blue-100 text-blue-700'
              : 'text-gray-500 hover:bg-gray-100'
          )}
        >
          {label}
          <span className="ml-1 text-xs opacity-75">
            ({counts[value]})
          </span>
        </button>
      ))}
    </div>
  )
}
