import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Since we use localStorage for JWT tokens (client-side only),
// middleware can't check authentication status.
// Auth is handled client-side - the tasks page will redirect on 401.

export function middleware(request: NextRequest) {
  // Allow all requests to pass through
  // Client-side auth will handle redirects
  return NextResponse.next()
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico|.*\\..*$).*)',
  ],
}
