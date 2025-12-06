import type React from "react"
import { FlowProvider } from "@/lib/flow-context"

export default function FlowLayout({ children }: { children: React.ReactNode }) {
  return (
    <FlowProvider>
      <div className="min-h-screen bg-[#FAF3E0] relative overflow-hidden">
        {/* Subtle film grain overlay */}
        <div className="fixed inset-0 bg-[url('/noise.png')] opacity-[0.03] pointer-events-none"></div>

        <div className="relative z-10 container mx-auto px-4 py-8 max-w-6xl">{children}</div>
      </div>
    </FlowProvider>
  )
}
