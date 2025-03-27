import * as React from "react"

const Chart = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ className, ...props }, ref) => {
  return <div className={className} ref={ref} {...props} />
})
Chart.displayName = "Chart"

const ChartContainer = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    data: any[]
    tooltip?: React.ReactNode
  }
>(({ className, data, tooltip, ...props }, ref) => {
  return (
    <div className={className} ref={ref} {...props}>
      {props.children}
      {tooltip}
    </div>
  )
})
ChartContainer.displayName = "ChartContainer"

const ChartTooltip = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return <div className={className} ref={ref} {...props} />
  },
)
ChartTooltip.displayName = "ChartTooltip"

const ChartTooltipContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return <div className={className} ref={ref} {...props} />
  },
)
ChartTooltipContent.displayName = "ChartTooltipContent"

interface ChartTooltipItemProps {
  label: string
  value: (item: any) => string
}

const ChartTooltipItem = ({ label, value }: ChartTooltipItemProps) => {
  return (
    <div>
      {label}: {value ? value : "N/A"}
    </div>
  )
}
ChartTooltipItem.displayName = "ChartTooltipItem"

export { Chart, ChartContainer, ChartTooltip, ChartTooltipContent, ChartTooltipItem }

