"use client"

import { useChat } from "ai/react"
import { useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Bot, Send, User } from "lucide-react"
import { cn } from "@/lib/utils"

export function AIChat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: "/api/chat",
  })
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center space-y-4 text-center">
            <Bot className="h-12 w-12 text-primary" />
            <div className="space-y-2">
              <h3 className="text-lg font-semibold">AI Learning Assistant</h3>
              <p className="text-sm text-muted-foreground">
                Ask me anything about your course materials, assignments, or concepts you're struggling with.
              </p>
            </div>
            <div className="grid gap-2">
              <Button
                variant="outline"
                className="text-sm"
                onClick={() => handleInputChange({ target: { value: "Explain the Context API in React" } } as any)}
              >
                Explain the Context API in React
              </Button>
              <Button
                variant="outline"
                className="text-sm"
                onClick={() =>
                  handleInputChange({
                    target: { value: "What's the difference between useReducer and useState?" },
                  } as any)
                }
              >
                What's the difference between useReducer and useState?
              </Button>
              <Button
                variant="outline"
                className="text-sm"
                onClick={() =>
                  handleInputChange({ target: { value: "Give me practice exercises for React hooks" } } as any)
                }
              >
                Give me practice exercises for React hooks
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn("flex items-start gap-3", message.role === "user" ? "justify-end" : "")}
              >
                {message.role !== "user" && (
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-primary text-primary-foreground">
                      <Bot className="h-4 w-4" />
                    </AvatarFallback>
                  </Avatar>
                )}
                <div
                  className={cn(
                    "rounded-lg px-4 py-2 max-w-[80%]",
                    message.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted",
                  )}
                >
                  <p className="text-sm">{message.content}</p>
                </div>
                {message.role === "user" && (
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-muted">
                      <User className="h-4 w-4" />
                    </AvatarFallback>
                  </Avatar>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      <div className="border-t p-4">
        <form onSubmit={handleSubmit} className="flex items-end gap-2">
          <Textarea
            placeholder="Ask a question about your course..."
            value={input}
            onChange={handleInputChange}
            className="min-h-24 flex-1 resize-none"
          />
          <Button type="submit" size="icon" disabled={isLoading || !input.trim()}>
            <Send className="h-4 w-4" />
            <span className="sr-only">Send message</span>
          </Button>
        </form>
      </div>
    </div>
  )
}

