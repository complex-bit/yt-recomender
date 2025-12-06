"use client"

import type React from "react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface SearchInputProps {
  placeholder?: string
  onSearch?: (query: string) => void
  buttonText?: string
  value?: string
  onChange?: (value: string) => void
}

export function SearchInput({
  placeholder = "Describe what you want...",
  onSearch,
  buttonText = "Explore →",
  value: controlledValue,
  onChange: controlledOnChange,
}: SearchInputProps) {
  const [internalQuery, setInternalQuery] = useState("")
  const query = controlledValue !== undefined ? controlledValue : internalQuery
  const setQuery = controlledOnChange || setInternalQuery

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (onSearch && query.trim()) {
      onSearch(query)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <Input
        type="text"
        placeholder={placeholder}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="flex-1 rounded-lg border-2 border-[#D4C5B9] bg-white text-[#3E2723] placeholder:text-[#6B5B55] focus-visible:border-[#E76F51] focus-visible:ring-[#E76F51]"
      />
      <Button type="submit" className="bg-[#E76F51] hover:bg-[#d65a3a] text-white rounded-lg font-semibold px-6">
        {buttonText}
      </Button>
    </form>
  )
}
