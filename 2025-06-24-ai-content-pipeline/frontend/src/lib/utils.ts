import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const formatDuration = (seconds: number | undefined) => {
  if (seconds === undefined) return "N/A"
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  const parts = []
  if (hours > 0) parts.push(`${hours}h`)
  if (minutes > 0) parts.push(`${minutes}m`)
  if (secs > 0 || (hours === 0 && minutes === 0)) parts.push(`${secs}s`)

  return parts.length > 0 ? parts.join(" ") : "0s"
}

export const formatDate = (dateString: string | undefined, options?: Intl.DateTimeFormatOptions) => {
  if (!dateString) return "N/A"
  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }
  return new Date(dateString).toLocaleString(undefined, options || defaultOptions)
}

export const formatFileSize = (bytes: number | undefined) => {
  if (bytes === undefined) return "N/A"
  if (bytes === 0) return "0 Bytes"
  const k = 1024
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"]
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
}
