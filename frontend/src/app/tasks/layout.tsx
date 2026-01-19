import { Navbar } from '@/components/layout/Navbar'

export default function TasksLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar showLogout />
      <div className="flex-1">
        {children}
      </div>
    </div>
  )
}
