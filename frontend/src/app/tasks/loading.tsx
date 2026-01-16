import { TaskListSkeleton } from '@/components/ui/Skeleton'

export default function TasksLoading() {
  return (
    <main className="max-w-2xl mx-auto px-4 py-8">
      <div className="h-8 w-32 bg-gray-200 animate-pulse rounded mb-6" />
      <div className="h-12 w-full bg-gray-200 animate-pulse rounded mb-6" />
      <TaskListSkeleton />
    </main>
  )
}
