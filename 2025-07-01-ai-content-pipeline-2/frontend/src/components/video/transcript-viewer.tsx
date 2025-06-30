"use client";

import { Check, Copy, FileText } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { EmptyState } from "@/components/shared/empty-state";
import { ErrorMessage } from "@/components/shared/error-message";
import { LoadingIndicator } from "@/components/shared/loading-indicator";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { api } from "@/lib/apiClient"; // Assuming apiClient.ts

interface TranscriptViewerProps {
	videoId: string;
	initialTranscript?: string; // Allow passing initial transcript
}

export function TranscriptViewer({
	videoId,
	initialTranscript,
}: TranscriptViewerProps) {
	const [transcript, setTranscript] = useState<string | undefined>(
		initialTranscript,
	);
	const [loading, setLoading] = useState(!initialTranscript); // Only load if not provided
	const [error, setError] = useState<string | null>(null);
	const [copied, setCopied] = useState(false);

	const fetchTranscript = useCallback(async () => {
		setLoading(true);
		setError(null);
		try {
			const transcriptData = await api.getTranscript(videoId); // Assuming api.getTranscript
			setTranscript(transcriptData);
		} catch (err: any) {
			console.error("Failed to load transcript:", err);
			setError(err.message || "Failed to load transcript. Please try again.");
			setTranscript(undefined);
		} finally {
			setLoading(false);
		}
	}, [videoId]);

	useEffect(() => {
		if (!initialTranscript && videoId) {
			// Fetch only if no initial transcript and videoId is present
			fetchTranscript();
		} else if (initialTranscript) {
			setTranscript(initialTranscript); // Use initial transcript if provided
			setLoading(false); // Ensure loading is false if initial transcript is used
		}
	}, [videoId, initialTranscript, fetchTranscript]);

	// Effect to update transcript if initialTranscript prop changes (e.g. parent re-fetches)
	useEffect(() => {
		if (initialTranscript !== undefined && initialTranscript !== transcript) {
			setTranscript(initialTranscript);
		}
	}, [initialTranscript, transcript]);

	const copyToClipboard = async () => {
		if (!transcript) return;
		try {
			await navigator.clipboard.writeText(transcript);
			setCopied(true);
			toast.success("Transcript copied to clipboard!");
			setTimeout(() => setCopied(false), 2000);
		} catch (err) {
			console.error("Failed to copy transcript:", err);
			toast.error("Failed to copy transcript.");
		}
	};

	if (loading) {
		return <LoadingIndicator text="Loading transcript..." />;
	}

	if (error) {
		return <ErrorMessage message={error} onRetry={fetchTranscript} />;
	}

	if (!transcript) {
		return (
			<EmptyState
				Icon={FileText}
				title="No Transcript Available"
				description="A transcript for this video could not be found or is still processing."
				action={
					!initialTranscript ? (
						<Button onClick={fetchTranscript} variant="outline">
							Refresh Transcript
						</Button>
					) : undefined
				}
			/>
		);
	}

	return (
		<div className="space-y-4">
			<ScrollArea className="h-72 w-full rounded-md border p-4 bg-muted/20">
				<pre className="macos-text-body whitespace-pre-wrap break-words text-muted-foreground">
					{transcript}
				</pre>
			</ScrollArea>
			<Button
				onClick={copyToClipboard}
				variant="outline"
				className="w-full sm:w-auto bg-background text-foreground"
			>
				{copied ? (
					<Check className="w-4 h-4 mr-2 text-green-500" />
				) : (
					<Copy className="w-4 h-4 mr-2" />
				)}
				{copied ? "Copied!" : "Copy Transcript"}
			</Button>
		</div>
	);
}
