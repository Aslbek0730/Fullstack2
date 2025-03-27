import Link from "next/link"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"

const recentCourses = [
  {
    id: 2,
    title: "Advanced React Techniques",
    progress: 35,
    lastAccessed: "2 hours ago",
    image: "/placeholder.svg?height=40&width=40",
  },
  {
    id: 3,
    title: "Data Science Fundamentals",
    progress: 65,
    lastAccessed: "Yesterday",
    image: "/placeholder.svg?height=40&width=40",
  },
  {
    id: 4,
    title: "UI/UX Design Principles",
    progress: 10,
    lastAccessed: "3 days ago",
    image: "/placeholder.svg?height=40&width=40",
  },
]

export function RecentCourses() {
  return (
    <div className="space-y-4">
      {recentCourses.map((course) => (
        <div key={course.id} className="flex items-center gap-4">
          <Avatar className="h-10 w-10 rounded-md">
            <AvatarImage src={course.image} alt={course.title} />
            <AvatarFallback className="rounded-md">{course.title.substring(0, 2)}</AvatarFallback>
          </Avatar>
          <div className="flex-1 space-y-1">
            <Link href={`/dashboard/courses/${course.id}`} className="font-medium hover:underline">
              {course.title}
            </Link>
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Last accessed {course.lastAccessed}</span>
              <span>{course.progress}%</span>
            </div>
            <Progress value={course.progress} className="h-1" />
          </div>
        </div>
      ))}
    </div>
  )
}

