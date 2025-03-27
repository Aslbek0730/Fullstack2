"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Chart, ChartContainer, ChartTooltip, ChartTooltipContent, ChartTooltipItem } from "@/components/ui/chart"
import { Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer, XAxis, YAxis } from "recharts"

const courseProgressData = [
  { name: "Web Development", progress: 85 },
  { name: "React", progress: 65 },
  { name: "Data Science", progress: 45 },
  { name: "UI/UX Design", progress: 30 },
  { name: "Mobile Dev", progress: 15 },
]

const quizScoresData = [
  { name: "HTML Basics", score: 95 },
  { name: "CSS Layouts", score: 88 },
  { name: "JavaScript Fundamentals", score: 75 },
  { name: "React Hooks", score: 82 },
  { name: "State Management", score: 68 },
]

const timeSpentData = [
  { name: "Videos", value: 45 },
  { name: "Reading", value: 25 },
  { name: "Exercises", value: 20 },
  { name: "Quizzes", value: 10 },
]

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"]

export default function ProgressPage() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Learning Progress</h1>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="courses">Courses</TabsTrigger>
          <TabsTrigger value="assessments">Assessments</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle>Total Learning Time</CardTitle>
                <CardDescription>Hours spent learning</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold">42.5</div>
                <p className="text-xs text-muted-foreground">+12.5 hours since last month</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle>Courses Completed</CardTitle>
                <CardDescription>Finished courses</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold">3</div>
                <p className="text-xs text-muted-foreground">+1 since last month</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle>Average Quiz Score</CardTitle>
                <CardDescription>Across all assessments</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold">82%</div>
                <p className="text-xs text-muted-foreground">+5% since last month</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Course Progress</CardTitle>
                <CardDescription>Completion percentage by course</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ChartContainer
                    data={courseProgressData}
                    tooltip={
                      <ChartTooltip>
                        <ChartTooltipContent>
                          <ChartTooltipItem label="Course" value={(item) => item.name} />
                          <ChartTooltipItem label="Progress" value={(item) => `${item.progress}%`} />
                        </ChartTooltipContent>
                      </ChartTooltip>
                    }
                  >
                    <Chart>
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={courseProgressData}
                          layout="vertical"
                          margin={{
                            top: 10,
                            right: 10,
                            left: 80,
                            bottom: 0,
                          }}
                        >
                          <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
                          <XAxis
                            type="number"
                            domain={[0, 100]}
                            tickFormatter={(value) => `${value}%`}
                            className="text-xs text-muted-foreground"
                          />
                          <YAxis type="category" dataKey="name" className="text-xs text-muted-foreground" />
                          <Bar dataKey="progress" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]} barSize={20} />
                        </BarChart>
                      </ResponsiveContainer>
                    </Chart>
                  </ChartContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Time Distribution</CardTitle>
                <CardDescription>How you spend your learning time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ChartContainer
                    data={timeSpentData}
                    tooltip={
                      <ChartTooltip>
                        <ChartTooltipContent>
                          <ChartTooltipItem label="Activity" value={(item) => item.name} />
                          <ChartTooltipItem label="Time" value={(item) => `${item.value}%`} />
                        </ChartTooltipContent>
                      </ChartTooltip>
                    }
                  >
                    <Chart>
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={timeSpentData}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                          >
                            {timeSpentData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    </Chart>
                  </ChartContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="courses" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Course Details</CardTitle>
              <CardDescription>Detailed progress for each course</CardDescription>
            </CardHeader>
            <CardContent className="h-[500px] flex items-center justify-center">
              <p className="text-muted-foreground">Course details will appear here</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="assessments" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Quiz Scores</CardTitle>
              <CardDescription>Performance on assessments and quizzes</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ChartContainer
                  data={quizScoresData}
                  tooltip={
                    <ChartTooltip>
                      <ChartTooltipContent>
                        <ChartTooltipItem label="Quiz" value={(item) => item.name} />
                        <ChartTooltipItem label="Score" value={(item) => `${item.score}%`} />
                      </ChartTooltipContent>
                    </ChartTooltip>
                  }
                >
                  <Chart>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={quizScoresData}
                        margin={{
                          top: 10,
                          right: 10,
                          left: 10,
                          bottom: 40,
                        }}
                      >
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis
                          dataKey="name"
                          angle={-45}
                          textAnchor="end"
                          height={70}
                          className="text-xs text-muted-foreground"
                        />
                        <YAxis
                          domain={[0, 100]}
                          tickFormatter={(value) => `${value}%`}
                          className="text-xs text-muted-foreground"
                        />
                        <Bar dataKey="score" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} barSize={30} />
                      </BarChart>
                    </ResponsiveContainer>
                  </Chart>
                </ChartContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

