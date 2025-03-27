"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { getCourses } from "../api/apiService"

interface Course {
  id: number
  title: string
  description: string
  instructor_name: string
  category_name: string
  level: string
  lesson_count: number
  thumbnail: string
}

const CourseList: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setLoading(true)
        const data = await getCourses()
        setCourses(data)
        setError(null)
      } catch (err: any) {
        setError("Failed to load courses. Please try again later.")
        console.error("Error fetching courses:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchCourses()
  }, [])

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-md bg-destructive/15 p-4 text-destructive">
        <p>{error}</p>
      </div>
    )
  }

  return (
    <div>
      <h2 className="mb-6 text-2xl font-bold">Available Courses</h2>

      {courses.length === 0 ? (
        <p className="text-muted-foreground">No courses available.</p>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {courses.map((course) => (
            <div key={course.id} className="overflow-hidden rounded-lg border bg-card shadow-sm">
              <div className="aspect-video w-full overflow-hidden">
                <img
                  src={course.thumbnail || "/placeholder.svg?height=220&width=400"}
                  alt={course.title}
                  className="h-full w-full object-cover"
                />
              </div>
              <div className="p-4">
                <h3 className="mb-2 text-xl font-bold">{course.title}</h3>
                <p className="mb-2 text-sm text-muted-foreground">{course.description}</p>
                <div className="flex flex-wrap gap-2">
                  <span className="rounded-full bg-primary/10 px-2 py-1 text-xs font-medium text-primary">
                    {course.level}
                  </span>
                  <span className="rounded-full bg-muted px-2 py-1 text-xs font-medium">{course.category_name}</span>
                  <span className="rounded-full bg-muted px-2 py-1 text-xs font-medium">
                    {course.lesson_count} lessons
                  </span>
                </div>
                <p className="mt-2 text-sm font-medium">Instructor: {course.instructor_name}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default CourseList

