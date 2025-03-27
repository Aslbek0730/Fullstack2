import { CourseCard } from "@/components/course-card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, Filter } from "lucide-react"

const courses = [
  {
    id: 1,
    title: "Introduction to Web Development",
    description: "Learn the basics of HTML, CSS, and JavaScript to build modern websites.",
    instructor: "Sarah Johnson",
    level: "Beginner",
    duration: "8 weeks",
    lessons: 24,
    progress: 0,
    image: "/placeholder.svg?height=220&width=400",
  },
  {
    id: 2,
    title: "Advanced React Techniques",
    description: "Master advanced React concepts including hooks, context, and performance optimization.",
    instructor: "Michael Chen",
    level: "Advanced",
    duration: "6 weeks",
    lessons: 18,
    progress: 35,
    image: "/placeholder.svg?height=220&width=400",
  },
  {
    id: 3,
    title: "Data Science Fundamentals",
    description: "Introduction to data analysis, visualization, and machine learning basics.",
    instructor: "Emily Rodriguez",
    level: "Intermediate",
    duration: "10 weeks",
    lessons: 30,
    progress: 65,
    image: "/placeholder.svg?height=220&width=400",
  },
  {
    id: 4,
    title: "UI/UX Design Principles",
    description: "Learn the core principles of user interface and experience design.",
    instructor: "David Kim",
    level: "Beginner",
    duration: "5 weeks",
    lessons: 15,
    progress: 10,
    image: "/placeholder.svg?height=220&width=400",
  },
  {
    id: 5,
    title: "Mobile App Development with React Native",
    description: "Build cross-platform mobile applications using React Native.",
    instructor: "Jessica Taylor",
    level: "Intermediate",
    duration: "8 weeks",
    lessons: 24,
    progress: 0,
    image: "/placeholder.svg?height=220&width=400",
  },
  {
    id: 6,
    title: "Cloud Computing and AWS",
    description: "Introduction to cloud infrastructure and Amazon Web Services.",
    instructor: "Robert Martinez",
    level: "Advanced",
    duration: "7 weeks",
    lessons: 21,
    progress: 0,
    image: "/placeholder.svg?height=220&width=400",
  },
]

export default function CoursesPage() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Courses</h1>
      </div>
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="flex w-full max-w-sm items-center space-x-2">
          <Input placeholder="Search courses..." className="flex-1" />
          <Button type="submit" size="icon" variant="ghost">
            <Search className="h-4 w-4" />
            <span className="sr-only">Search</span>
          </Button>
        </div>
        <div className="flex items-center gap-2">
          <Select defaultValue="all">
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by level" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Levels</SelectItem>
              <SelectItem value="beginner">Beginner</SelectItem>
              <SelectItem value="intermediate">Intermediate</SelectItem>
              <SelectItem value="advanced">Advanced</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="icon">
            <Filter className="h-4 w-4" />
            <span className="sr-only">Filter</span>
          </Button>
        </div>
      </div>
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {courses.map((course) => (
          <CourseCard key={course.id} course={course} />
        ))}
      </div>
    </div>
  )
}

