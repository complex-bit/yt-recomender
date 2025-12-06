"use client"

import React, { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Send, Bot, User, Sparkles } from "lucide-react"
import { type GenreTreeNode } from "@/lib/api"

interface ChatMessage {
  id: string
  type: 'user' | 'system'
  content: string
  timestamp: Date
  genrePath?: GenreTreeNode[]
  results?: number
}

interface SemanticSearchChatProps {
  selectedGenrePath: GenreTreeNode[]
  onSearch: (query: string, chatHistory: ChatMessage[]) => void
  isLoading?: boolean
  onChatUpdate?: (chatHistory: ChatMessage[]) => void
  initialChatHistory?: ChatMessage[]
}

export const SemanticSearchChat = React.forwardRef<
  { addSystemResponse: (content: string, results?: number) => void },
  SemanticSearchChatProps
>(function SemanticSearchChat({
  selectedGenrePath,
  onSearch,
  isLoading = false,
  onChatUpdate,
  initialChatHistory = []
}, ref) {
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>(initialChatHistory)
  const [currentMessage, setCurrentMessage] = useState("")

  const handleSendMessage = () => {
    if (!currentMessage.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: currentMessage,
      timestamp: new Date(),
      genrePath: selectedGenrePath
    }

    const updatedHistory = [...chatHistory, userMessage]
    setChatHistory(updatedHistory)
    onChatUpdate?.(updatedHistory)

    // Call the search function
    onSearch(currentMessage, updatedHistory)

    setCurrentMessage("")
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const getGenrePathString = (path: GenreTreeNode[]) => {
    return path.map(node => node.name).join(' → ')
  }

  const clearChat = () => {
    setChatHistory([])
    onChatUpdate?.([])
  }

  // Function to add system response to chat
  const addSystemResponse = (content: string, results?: number) => {
    const systemMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'system',
      content,
      timestamp: new Date(),
      results
    }

    const updatedHistory = [...chatHistory, systemMessage]
    setChatHistory(updatedHistory)
    onChatUpdate?.(updatedHistory)
  }

  // Expose addSystemResponse for parent component
  React.useImperativeHandle(ref, () => ({
    addSystemResponse
  }))

  return (
    <Card className="bg-[#FFF9F0] border-[#E0E0E0] h-full flex flex-col">
      <CardHeader className="pb-4 border-b border-[#E0E0E0]">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2 text-[#3E2723]">
            <Sparkles className="h-5 w-5" />
            Semantic Search
          </CardTitle>
          {chatHistory.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={clearChat}
              className="text-[#6B5B55] hover:text-[#3E2723]"
            >
              Clear Chat
            </Button>
          )}
        </div>

        {selectedGenrePath.length > 0 && (
          <div className="mt-3">
            <Badge variant="secondary" className="bg-[#E76F51] text-white">
              {getGenrePathString(selectedGenrePath)}
            </Badge>
          </div>
        )}
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-4 gap-4">
        {/* Chat History */}
        <ScrollArea className="flex-1 pr-4">
          <div className="space-y-4">
            {chatHistory.length === 0 ? (
              <div className="text-center text-[#6B5B55] py-8">
                <Sparkles className="h-12 w-12 mx-auto mb-4 text-[#E76F51]" />
                <p className="text-lg font-medium mb-2">
                  {selectedGenrePath.length > 0
                    ? `Search within ${getGenrePathString(selectedGenrePath)}`
                    : "Describe what you want to watch"
                  }
                </p>
                <p className="text-sm">
                  Try: "I want to learn about space exploration" or "Show me funny cooking videos"
                </p>
              </div>
            ) : (
              chatHistory.map((message) => (
                <div
                  key={message.id}
                  className={`flex items-start gap-3 ${
                    message.type === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.type === 'system' && (
                    <div className="w-8 h-8 rounded-full bg-[#E76F51] flex items-center justify-center flex-shrink-0">
                      <Bot className="h-4 w-4 text-white" />
                    </div>
                  )}

                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      message.type === 'user'
                        ? 'bg-[#E76F51] text-white'
                        : 'bg-white border border-[#E0E0E0]'
                    }`}
                  >
                    <p className="text-sm">{message.content}</p>
                    {message.genrePath && message.genrePath.length > 0 && (
                      <div className="mt-2">
                        <Badge
                          variant="secondary"
                          className="text-xs bg-opacity-20 bg-white"
                        >
                          {getGenrePathString(message.genrePath)}
                        </Badge>
                      </div>
                    )}
                    {message.results !== undefined && (
                      <div className="mt-2 text-xs opacity-70">
                        Found {message.results} results
                      </div>
                    )}
                    <div className="mt-1 text-xs opacity-50">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>

                  {message.type === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-[#6B5B55] flex items-center justify-center flex-shrink-0">
                      <User className="h-4 w-4 text-white" />
                    </div>
                  )}
                </div>
              ))
            )}

            {isLoading && (
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-[#E76F51] flex items-center justify-center flex-shrink-0">
                  <Bot className="h-4 w-4 text-white" />
                </div>
                <div className="bg-white border border-[#E0E0E0] rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-[#E76F51] rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-[#E76F51] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-[#E76F51] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="text-sm text-[#6B5B55]">Searching...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        {/* Input Area */}
        <div className="flex gap-2">
          <Input
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              selectedGenrePath.length > 0
                ? `Search within ${selectedGenrePath[selectedGenrePath.length - 1]?.name}...`
                : "Describe what you want to watch..."
            }
            disabled={isLoading}
            className="flex-1 bg-white border-[#E0E0E0] focus:border-[#E76F51]"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!currentMessage.trim() || isLoading}
            className="bg-[#E76F51] hover:bg-[#D65A3F] text-white px-4"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>

        {/* Quick Suggestions */}
        {chatHistory.length === 0 && (
          <div className="space-y-2">
            <p className="text-xs text-[#6B5B55] font-medium">Quick suggestions:</p>
            <div className="flex flex-wrap gap-2">
              {[
                "I want to learn something new",
                "Show me entertaining content",
                "Find deep dives on topics",
                "Something relaxing to watch"
              ].map((suggestion) => (
                <Button
                  key={suggestion}
                  variant="outline"
                  size="sm"
                  className="text-xs h-7 border-[#E76F51] text-[#E76F51] hover:bg-[#E76F51] hover:text-white"
                  onClick={() => setCurrentMessage(suggestion)}
                  disabled={isLoading}
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
})