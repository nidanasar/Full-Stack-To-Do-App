'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { LogOut } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { signOut } from '@/lib/auth'

interface LogoutButtonProps {
  variant?: 'primary' | 'ghost'
}

export function LogoutButton({ variant = 'ghost' }: LogoutButtonProps) {
  const router = useRouter()
  const [loading, setLoading] = useState(false)

  const handleLogout = async () => {
    setLoading(true)
    try {
      await signOut()
      router.push('/login')
      router.refresh()
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Button
      variant={variant}
      size="sm"
      onClick={handleLogout}
      loading={loading}
    >
      <LogOut className="w-4 h-4 mr-2" />
      Logout
    </Button>
  )
}
