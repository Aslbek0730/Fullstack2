import { Button } from "@/components/ui/button"
import { Calendar, Clock } from "lucide-react"

const upcomingLessons = [
  {
    id: 1,
    title: "Advanced State Management",
    course: "Advanced React Techniques",
    date: "Today",
    time: "2:00 PM - 3:30 PM",
  },
  {
    id: 2,
    title: "Data Visualization with D3",
    course: "Data Science Fundamentals",
    date: "Tomorrow",
    time: "10:00 AM - 11:30 AM",
  },
  {
    id: 3,
    title: "User Research Methods",
    course: "UI/UX Design Principles",
    date: "Mar 30, 2025",
    time: "1:00 PM - 2:30 PM",
  },
]

export function UpcomingLessons() {
  return (
    <div className="space-y-4">
      {upcomingLessons.map((lesson) => (
        <div
          key={lesson.id}
          className="flex flex-col gap-2 rounded-lg border p-4 sm:flex-row sm:items-center sm:justify-between"
        >
          <div className="space-y-1">
            <h3 className="font-medium">{lesson.title}</h3>
            <p className="text-sm text-muted-foreground">{lesson.course}</p>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                <span>{lesson.date}</span>
              </div>
              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                <span>{lesson.time}</span>
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              Reschedule
            </Button>
            <Button size="sm">Join</Button>
          </div>
        </div>
      ))}
    </div>
  )
}

