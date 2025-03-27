"use client"

import { Chart, ChartContainer, ChartTooltip, ChartTooltipContent, ChartTooltipItem } from "@/components/ui/chart"
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, XAxis, YAxis } from "recharts"

const data = [
  { date: "Mar 1", minutes: 45 },
  { date: "Mar 2", minutes: 60 },
  { date: "Mar 3", minutes: 30 },
  { date: "Mar 4", minutes: 90 },
  { date: "Mar 5", minutes: 75 },
  { date: "Mar 6", minutes: 45 },
  { date: "Mar 7", minutes: 60 },
  { date: "Mar 8", minutes: 120 },
  { date: "Mar 9", minutes: 90 },
  { date: "Mar 10", minutes: 60 },
  { date: "Mar 11", minutes: 45 },
  { date: "Mar 12", minutes: 30 },
  { date: "Mar 13", minutes: 75 },
  { date: "Mar 14", minutes: 90 },
  { date: "Mar 15", minutes: 60 },
  { date: "Mar 16", minutes: 45 },
  { date: "Mar 17", minutes: 60 },
  { date: "Mar 18", minutes: 75 },
  { date: "Mar 19", minutes: 90 },
  { date: "Mar 20", minutes: 120 },
  { date: "Mar 21", minutes: 60 },
  { date: "Mar 22", minutes: 45 },
  { date: "Mar 23", minutes: 30 },
  { date: "Mar 24", minutes: 60 },
  { date: "Mar 25", minutes: 75 },
  { date: "Mar 26", minutes: 90 },
  { date: "Mar 27", minutes: 60 },
  { date: "Mar 28", minutes: 45 },
  { date: "Mar 29", minutes: 60 },
  { date: "Mar 30", minutes: 75 },
]

export function LearningProgress() {
  return (
    <div className="h-[300px] w-full">
      <ChartContainer
        data={data}
        tooltip={
          <ChartTooltip>
            <ChartTooltipContent>
              <ChartTooltipItem label="Date" value={(item) => item.date} />
              <ChartTooltipItem label="Minutes" value={(item) => `${item.minutes} min`} />
            </ChartTooltipContent>
          </ChartTooltip>
        }
      >
        <Chart>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={data}
              margin={{
                top: 10,
                right: 10,
                left: 0,
                bottom: 0,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="date"
                tickLine={false}
                axisLine={false}
                tickMargin={10}
                tickFormatter={(value) => value.split(" ")[1]}
                className="text-xs text-muted-foreground"
              />
              <YAxis tickLine={false} axisLine={false} tickMargin={10} className="text-xs text-muted-foreground" />
              <Area
                type="monotone"
                dataKey="minutes"
                stroke="hsl(var(--primary))"
                fill="hsl(var(--primary)/0.2)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </Chart>
      </ChartContainer>
    </div>
  )
}

