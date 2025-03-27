import Link from "next/link"
import { Button } from "@/components/ui/button"
import { CheckCircle, Lock, PlayCircle } from "lucide-react"

interface LessonListProps {
  courseId: number
}

export function LessonList({ courseId }: LessonListProps) {
  // In a real app, you would fetch lessons based on the courseId
  const lessons = [
    {
      id: 1,
      title: "Introduction to Advanced React",
      duration: "15 min",
      status: "completed",
    },
    {
      id: 2,
      title: "Understanding React Hooks",
      duration: "25 min",
      status: "completed",
    },
    {
      id: 3,
      title: "Custom Hooks",
      duration: "20 min",
      status: "completed",
    },
    {
      id: 4,
      title: "Context API Basics",
      duration: "30 min",
      status: "completed",
    },
    {
      id: 5,
      title: "Context API Advanced",
      duration: "35 min",
      status: "completed",
    },
    {
      id: 6,
      title: "useReducer Hook",
      duration: "25 min",
      status: "completed",
    },
    {
      id: 7,
      title: "Advanced State Management",
      duration: "40 min",
      status: "in-progress",
    },
    {
      id: 8,
      title: "Performance Optimization",
      duration: "30 min",
      status: "locked",
    },
    {
      id: 9,
      title: "React Suspense",
      duration: "25 min",
      status: "locked",
    },
    {
      id: 10,
      title: "Error Boundaries",
      duration: "20 min",
      status: "locked",
    },
  ]

  return (
    <div className="space-y-2">
      {lessons.map((lesson) => (
        <div key={lesson.id} className="flex items-center justify-between rounded-lg p-2 hover:bg-muted/50">
          <div className="flex items-center gap-2">
            {lesson.status === "completed" ? (
              <CheckCircle className="h-5 w-5 text-primary" />
            ) : lesson.status === "in-progress" ? (
              <PlayCircle className="h-5 w-5 text-primary" />
            ) : (
              <Lock className="h-5 w-5 text-muted-foreground" />
            )}
            <div>
              <p className={`text-sm font-medium ${lesson.status === "locked" ? "text-muted-foreground" : ""}`}>
                {lesson.title}
              </p>
              <p className="text-xs text-muted-foreground">{lesson.duration}</p>
            </div>
          </div>
          {lesson.status !== "locked" && (
            <Link href={`/dashboard/courses/${courseId}/lessons/${lesson.id}`}>
              <Button variant="ghost" size="sm">
                {lesson.status === "completed" ? "Review" : "Continue"}
              </Button>
            </Link>
          )}
        </div>
      ))}
    </div>
  )
}

