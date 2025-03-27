"use client"

import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { BookOpen, CheckCircle, Clock, ArrowLeft } from "lucide-react"
import Link from "next/link"
import { VideoPlayer } from "@/components/video-player"
import { LessonList } from "@/components/lesson-list"
import { CourseQuiz } from "@/components/course-quiz"
import { ChatbotButton } from "@/components/chatbot-button"

export default function CoursePage({ params }: { params: { id: string } }) {
  // In a real app, you would fetch course data based on the ID
  const course = {
    id: Number.parseInt(params.id),
    title: "Advanced React Techniques",
    description: "Master advanced React concepts including hooks, context, and performance optimization.",
    instructor: "Michael Chen",
    level: "Advanced",
    duration: "6 weeks",
    lessons: 18,
    progress: 35,
    currentLesson: 7,
    image: "/placeholder.svg?height=220&width=400",
    overview:
      "This comprehensive course covers advanced React concepts and best practices for building scalable and performant applications. You'll learn how to leverage React's latest features, optimize your components, and structure complex applications.",
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-2">
        <Link href="/dashboard/courses">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
            <span className="sr-only">Back to courses</span>
          </Button>
        </Link>
        <h1 className="text-2xl font-bold tracking-tight md:text-3xl">{course.title}</h1>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardContent className="p-0">
              <VideoPlayer />
              <div className="p-6">
                <div className="mb-4 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{course.level}</Badge>
                    <div className="flex items-center gap-1 text-sm text-muted-foreground">
                      <Clock className="h-4 w-4" />
                      <span>{course.duration}</span>
                    </div>
                    <div className="flex items-center gap-1 text-sm text-muted-foreground">
                      <BookOpen className="h-4 w-4" />
                      <span>{course.lessons} lessons</span>
                    </div>
                  </div>
                  <ChatbotButton />
                </div>
                <h2 className="text-xl font-semibold">Lesson 7: Advanced State Management</h2>
                <div className="mt-2 flex items-center gap-2">
                  <Progress value={course.progress} className="h-2 w-full" />
                  <span className="text-sm font-medium">{course.progress}%</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Tabs defaultValue="content" className="mt-6">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="content">Content</TabsTrigger>
              <TabsTrigger value="exercises">Exercises</TabsTrigger>
              <TabsTrigger value="discussion">Discussion</TabsTrigger>
            </TabsList>
            <TabsContent value="content" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle>Lesson Content</CardTitle>
                  <CardDescription>Advanced state management techniques in React applications</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <h3 className="text-lg font-medium">Overview</h3>
                  <p>
                    In this lesson, we'll explore advanced state management patterns in React, including the Context
                    API, useReducer hook, and how to combine them for complex state management needs. We'll also look at
                    performance optimizations and when to consider external state management libraries.
                  </p>

                  <h3 className="text-lg font-medium">Key Topics</h3>
                  <ul className="ml-6 list-disc space-y-2">
                    <li>Understanding the Context API for global state</li>
                    <li>Using useReducer for complex state logic</li>
                    <li>Combining Context and useReducer</li>
                    <li>Performance considerations and optimizations</li>
                    <li>Comparing with Redux and other state management libraries</li>
                  </ul>

                  <div className="flex justify-between pt-4">
                    <Button variant="outline">Previous Lesson</Button>
                    <Button>
                      <CheckCircle className="mr-2 h-4 w-4" />
                      Mark as Complete
                    </Button>
                    <Button>Next Lesson</Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="exercises" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle>Practical Exercises</CardTitle>
                  <CardDescription>Apply what you've learned with these hands-on exercises</CardDescription>
                </CardHeader>
                <CardContent>
                  <CourseQuiz />
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="discussion" className="mt-4">
              <Card>
                <CardHeader>
                  <CardTitle>Discussion Forum</CardTitle>
                  <CardDescription>Engage with other students and instructors</CardDescription>
                </CardHeader>
                <CardContent className="h-[300px] flex items-center justify-center">
                  <p className="text-muted-foreground">Discussion forum will appear here</p>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        <div>
          <Card>
            <CardHeader>
              <CardTitle>Course Lessons</CardTitle>
              <CardDescription>
                {course.currentLesson} of {course.lessons} lessons completed
              </CardDescription>
            </CardHeader>
            <CardContent>
              <LessonList courseId={course.id} />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

