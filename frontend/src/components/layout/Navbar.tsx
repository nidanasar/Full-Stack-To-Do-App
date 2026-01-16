import Link from 'next/link'
import { CheckSquare } from 'lucide-react'
import { LogoutButton } from '@/components/auth/LogoutButton'

interface NavbarProps {
  showLogout?: boolean
}

export function Navbar({ showLogout = false }: NavbarProps) {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-4xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link
            href="/tasks"
            className="flex items-center gap-2 text-gray-900 hover:text-blue-600 transition-colors"
          >
            <CheckSquare className="w-6 h-6" />
            <span className="font-semibold text-lg">Todo App</span>
          </Link>

          {showLogout && (
            <LogoutButton />
          )}
        </div>
      </div>
    </header>
  )
}
