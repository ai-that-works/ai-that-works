"use client";

import { AlertTriangle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ErrorMessageProps {
	title?: string;
	message: string;
	onRetry?: () => void;
	className?: string;
}

export function ErrorMessage({
	title = "An Error Occurred",
	message,
	onRetry,
	className,
}: ErrorMessageProps) {
	return (
		<Alert variant="destructive" className={cn("my-4", className)}>
			<AlertTriangle className="h-5 w-5" />
			<AlertTitle>{title}</AlertTitle>
			<AlertDescription>
				{message}
				{onRetry && (
					<Button
						onClick={onRetry}
						variant="outline"
						size="sm"
						className="mt-3 bg-destructive text-destructive-foreground hover:bg-destructive/90"
					>
						Try Again
					</Button>
				)}
			</AlertDescription>
		</Alert>
	);
}
