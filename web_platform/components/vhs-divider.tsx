export function VhsDivider({ text }: { text?: string }) {
  return (
    <div className="relative my-8">
      <div className="absolute inset-0 flex items-center">
        <div className="w-full border-t border-[#D4C5B9] opacity-50"></div>
      </div>
      {text && (
        <div className="relative flex justify-center">
          <span className="bg-[#FAF3E0] px-4 text-[#3E2723] font-['Zilla_Slab',serif] text-lg">{text}</span>
        </div>
      )}
    </div>
  )
}
