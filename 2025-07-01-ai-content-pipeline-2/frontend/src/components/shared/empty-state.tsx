import { Inbox } from "lucide-react"; // Or any other relevant icon
import type React from "react";
import { cn } from "@/lib/utils";

interface EmptyStateProps {
  Icon?: React.ElementType;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export function EmptyState({
  Icon = Inbox,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn("text-center py-12 macos-material-content p-6", className)}
    >
      <Icon className="w-16 h-16 text-muted-foreground mx-auto mb-6" />
      <h3 className="macos-text-title2 text-card-foreground mb-2">{title}</h3>
      {description && (
        <p className="macos-text-body text-muted-foreground mb-6">
          {description}
        </p>
      )}
      {action}
    </div>
  );
}
