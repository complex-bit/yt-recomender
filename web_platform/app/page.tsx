"use client"

import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Clapperboard } from "lucide-react"

export default function Page() {
  const router = useRouter()

  const handleGoogleLogin = () => {
    // TODO: Implement Google OAuth login
    // For now, navigate to explore page to show genre wheel
    router.push("/flow/explore")
  }

  return (
    <div className="min-h-screen bg-[#FAF3E0] relative overflow-hidden flex items-center justify-center">
      {/* Subtle film grain overlay */}
      <div className="fixed inset-0 bg-[url('/noise.png')] opacity-[0.03] pointer-events-none"></div>

      <div className="relative z-10 text-center px-4">
        {/* Logo/Icon */}
        <div className="mb-8 flex justify-center">
          <div className="w-32 h-32 rounded-full bg-[#E76F51] flex items-center justify-center shadow-2xl relative overflow-hidden before:content-[''] before:absolute before:inset-0 before:bg-[url('/noise.png')] before:opacity-10 before:pointer-events-none">
            <Clapperboard className="h-16 w-16 text-white" />
          </div>
        </div>

        {/* Title */}
        <h1 className="font-['Zilla_Slab',serif] text-7xl md:text-8xl font-bold text-[#3E2723] mb-6 text-balance">
          WhyExplore
        </h1>

        {/* Subtitle */}
        <p className="text-2xl md:text-3xl text-[#6B5B55] mb-12 text-pretty max-w-2xl mx-auto">
          Discover videos you'll actually want to watch
        </p>

        <Button
          onClick={handleGoogleLogin}
          className="bg-white hover:bg-gray-50 text-[#3E2723] rounded-full px-12 py-8 text-xl font-bold shadow-xl hover:shadow-2xl transition-all hover:-translate-y-1 flex items-center gap-4 mx-auto border-2 border-[#E0E0E0]"
        >
          Sign in with Google
          <svg className="w-8 h-8" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              fill="#4285F4"
            />
            <path
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              fill="#34A853"
            />
            <path
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              fill="#FBBC05"
            />
            <path
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              fill="#EA4335"
            />
          </svg>
        </Button>

        {/* Tagline */}
        <p className="text-sm text-[#6B5B55] mt-8 italic">"If a vintage film camera and YouTube had a baby"</p>
      </div>
    </div>
  )
}
