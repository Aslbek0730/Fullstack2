import Link from "next/link"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Clock, BookOpen } from "lucide-react"

interface Course {
  id: number
  title: string
  description: string
  instructor: string
  level: string
  duration: string
  lessons: number
  progress: number
  image: string
}

interface CourseCardProps {
  course: Course
}

export function CourseCard({ course }: CourseCardProps) {
  return (
    <Card className="overflow-hidden">
      <div className="aspect-video w-full overflow-hidden">
        <img
          src={course.image || "/placeholder.svg"}
          alt={course.title}
          className="h-full w-full object-cover transition-all hover:scale-105"
        />
      </div>
      <CardHeader className="p-4">
        <div className="flex items-center justify-between">
          <Badge variant="outline">{course.level}</Badge>
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            <span>{course.duration}</span>
          </div>
        </div>
        <Link href={`/dashboard/courses/${course.id}`} className="hover:underline">
          <h3 className="line-clamp-1 text-xl font-bold">{course.title}</h3>
        </Link>
        <div className="flex items-center gap-1 text-sm text-muted-foreground">
          <BookOpen className="h-4 w-4" />
          <span>{course.lessons} lessons</span>
        </div>
      </CardHeader>
      <CardContent className="p-4 pt-0">
        <p className="line-clamp-2 text-sm text-muted-foreground">{course.description}</p>
        <div className="mt-4">
          <div className="flex items-center justify-between text-sm">
            <span>Progress</span>
            <span>{course.progress}%</span>
          </div>
          <Progress value={course.progress} className="h-2" />
        </div>
      </CardContent>
      <CardFooter className="p-4">
        <Link href={`/dashboard/courses/${course.id}`} className="w-full">
          <Button className="w-full">{course.progress > 0 ? "Continue Learning" : "Start Course"}</Button>
        </Link>
      </CardFooter>
    </Card>
  )
}

