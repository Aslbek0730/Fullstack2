"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { MessageSquare } from "lucide-react"
import { AIChat } from "@/components/ai-chat"

export function ChatbotButton() {
  const [open, setOpen] = useState(false)

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="outline" size="sm" className="gap-1">
          <MessageSquare className="h-4 w-4" />
          AI Assistant
        </Button>
      </SheetTrigger>
      <SheetContent className="w-full sm:max-w-md">
        <SheetHeader>
          <SheetTitle>AI Learning Assistant</SheetTitle>
        </SheetHeader>
        <div className="mt-4 flex h-[calc(100vh-8rem)] flex-col">
          <AIChat />
        </div>
      </SheetContent>
    </Sheet>
  )
}

