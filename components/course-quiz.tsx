"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle, XCircle } from "lucide-react"

const quizQuestions = [
  {
    id: 1,
    question: "Which hook is best for complex state logic in React?",
    options: [
      { id: "a", text: "useState" },
      { id: "b", text: "useEffect" },
      { id: "c", text: "useReducer" },
      { id: "d", text: "useContext" },
    ],
    correctAnswer: "c",
  },
  {
    id: 2,
    question: "What is the primary purpose of the Context API?",
    options: [
      { id: "a", text: "To optimize performance" },
      { id: "b", text: "To share state across components without prop drilling" },
      { id: "c", text: "To handle side effects" },
      { id: "d", text: "To manage local component state" },
    ],
    correctAnswer: "b",
  },
  {
    id: 3,
    question: "When combining useReducer with Context, what is typically stored in the Context?",
    options: [
      { id: "a", text: "Only the state" },
      { id: "b", text: "Only the dispatch function" },
      { id: "c", text: "Both state and dispatch function" },
      { id: "d", text: "Neither state nor dispatch function" },
    ],
    correctAnswer: "c",
  },
]

export function CourseQuiz() {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [showResults, setShowResults] = useState(false)

  const handleAnswer = (value: string) => {
    setAnswers({ ...answers, [quizQuestions[currentQuestion].id]: value })
  }

  const handleNext = () => {
    if (currentQuestion < quizQuestions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
    } else {
      setShowResults(true)
    }
  }

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
    }
  }

  const handleReset = () => {
    setAnswers({})
    setCurrentQuestion(0)
    setShowResults(false)
  }

  const calculateScore = () => {
    let score = 0
    quizQuestions.forEach((question) => {
      if (answers[question.id] === question.correctAnswer) {
        score++
      }
    })
    return score
  }

  if (showResults) {
    const score = calculateScore()
    const percentage = Math.round((score / quizQuestions.length) * 100)

    return (
      <Card>
        <CardHeader>
          <CardTitle>Quiz Results</CardTitle>
          <CardDescription>
            You scored {score} out of {quizQuestions.length} ({percentage}%)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {quizQuestions.map((question) => {
            const isCorrect = answers[question.id] === question.correctAnswer
            return (
              <div key={question.id} className="space-y-2">
                <div className="flex items-start gap-2">
                  {isCorrect ? (
                    <CheckCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-green-500" />
                  ) : (
                    <XCircle className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-500" />
                  )}
                  <div>
                    <p className="font-medium">{question.question}</p>
                    <p className="text-sm text-muted-foreground">
                      Your answer: {question.options.find((option) => option.id === answers[question.id])?.text}
                    </p>
                    {!isCorrect && (
                      <p className="text-sm text-green-600">
                        Correct answer: {question.options.find((option) => option.id === question.correctAnswer)?.text}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </CardContent>
        <CardFooter>
          <Button onClick={handleReset}>Try Again</Button>
        </CardFooter>
      </Card>
    )
  }

  const question = quizQuestions[currentQuestion]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Exercise {currentQuestion + 1}</CardTitle>
        <CardDescription>
          Question {currentQuestion + 1} of {quizQuestions.length}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <p className="font-medium">{question.question}</p>
          <RadioGroup value={answers[question.id] || ""} onValueChange={handleAnswer}>
            {question.options.map((option) => (
              <div key={option.id} className="flex items-center space-x-2">
                <RadioGroupItem value={option.id} id={`option-${option.id}`} />
                <Label htmlFor={`option-${option.id}`}>{option.text}</Label>
              </div>
            ))}
          </RadioGroup>
        </div>
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button variant="outline" onClick={handlePrevious} disabled={currentQuestion === 0}>
          Previous
        </Button>
        <Button onClick={handleNext} disabled={!answers[question.id]}>
          {currentQuestion < quizQuestions.length - 1 ? "Next" : "Finish"}
        </Button>
      </CardFooter>
    </Card>
  )
}

