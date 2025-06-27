import { Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface LoadingIndicatorProps {
  text?: string
  className?: string
  iconClassName?: string
  fullPage?: boolean
}

export function LoadingIndicator({
  text = "Loading...",
  className,
  iconClassName,
  fullPage = false,
}: LoadingIndicatorProps) {
  if (fullPage) {
    return (
      <div className="fixed inset-0 flex flex-col items-center justify-center macos-material-popover z-50">
        <Loader2 className={cn("w-10 h-10 animate-spin text-primary mb-3", iconClassName)} />
        {text && <p className="macos-text-body font-medium text-muted-foreground">{text}</p>}
      </div>
    )
  }
  return (
    <div className={cn("flex flex-col items-center justify-center py-10 macos-material-content", className)}>
      <Loader2 className={cn("w-8 h-8 animate-spin text-primary mb-2", iconClassName)} />
      {text && <p className="macos-text-body text-muted-foreground">{text}</p>}
    </div>
  )
}
