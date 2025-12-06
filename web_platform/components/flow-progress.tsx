import { Check } from "lucide-react"
import { cn } from "@/lib/utils"

interface FlowProgressProps {
  currentStep: number
}

const steps = [
  { number: 1, label: "Explore" },
  { number: 2, label: "Discover" },
]

export function FlowProgress({ currentStep }: FlowProgressProps) {
  return (
    <div className="flex items-center justify-center gap-2 mb-12">
      {steps.map((step, index) => (
        <div key={step.number} className="flex items-center">
          <div className="flex flex-col items-center gap-2">
            <div
              className={cn(
                "w-12 h-12 rounded-full flex items-center justify-center font-bold transition-all duration-300 relative overflow-hidden",
                step.number < currentStep
                  ? "bg-[#2A9D8F] text-white"
                  : step.number === currentStep
                    ? "bg-[#E76F51] text-white shadow-lg scale-110"
                    : "bg-[#D4C5B9] text-[#6B5B55]",
                "before:content-[''] before:absolute before:inset-0 before:bg-[url('/noise.png')] before:opacity-10 before:pointer-events-none",
              )}
            >
              {step.number < currentStep ? <Check className="h-6 w-6" /> : step.number}
            </div>
            <span
              className={cn(
                "text-xs font-semibold whitespace-nowrap",
                step.number === currentStep ? "text-[#E76F51]" : "text-[#6B5B55]",
              )}
            >
              {step.label}
            </span>
          </div>

          {index < steps.length - 1 && (
            <div
              className={cn(
                "w-16 h-1 mx-2 rounded-full transition-all duration-300",
                step.number < currentStep ? "bg-[#2A9D8F]" : "bg-[#D4C5B9]",
              )}
            />
          )}
        </div>
      ))}
    </div>
  )
}
