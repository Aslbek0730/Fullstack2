import { streamText } from "ai"
import { openai } from "@ai-sdk/openai"

export async function POST(req: Request) {
  const { messages } = await req.json()

  // Create a system message for the AI assistant
  const systemMessage = {
    role: "system",
    content: `You are an AI learning assistant for an educational platform. 
    You help students understand course materials, answer their questions, and provide additional resources.
    You specialize in web development, particularly React and related technologies.
    Be concise, helpful, and encouraging. If you don't know something, admit it and suggest where they might find the answer.
    Current course context: Advanced React Techniques - covering hooks, context API, and state management.`,
  }

  // Add the system message to the beginning of the messages array
  const augmentedMessages = [systemMessage, ...messages]

  const result = streamText({
    model: openai("gpt-4o"),
    messages: augmentedMessages,
  })

  return result.toResponse()
}

