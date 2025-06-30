"use client";

import { Edit3, Loader2, MessageSquare, Sparkles } from "lucide-react";
import { useState } from "react";
import type { EmailDraft } from "@/baml_client/types";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

interface EmailPreviewProps {
	draft: EmailDraft | null;
	onChange: (draft: EmailDraft) => void;
	onRefine?: (feedback: string) => void;
	className?: string;
	readOnly?: boolean;
}

export function EmailPreview({
	draft,
	onChange,
	onRefine,
	className,
	readOnly = false,
}: EmailPreviewProps) {
	const [isEditing, setIsEditing] = useState(false);
	const [showFeedback, setShowFeedback] = useState(false);
	const [feedback, setFeedback] = useState("");
	const [isRefining, setIsRefining] = useState(false);
	const [formData, setFormData] = useState({
		subject: "",
		body: "",
		call_to_action: "",
	});

	// Initialize form when switching to edit mode
	const startEditing = () => {
		setFormData({
			subject: draft?.subject || "",
			body: draft?.body || "",
			call_to_action: draft?.call_to_action || "",
		});
		setIsEditing(true);
	};

	// Save form data directly as JSON
	const saveEdit = () => {
		onChange({
			subject: formData.subject.trim(),
			body: formData.body.trim(),
			call_to_action: formData.call_to_action.trim(),
		});
		setIsEditing(false);
	};

	// Handle feedback submission
	const handleFeedback = async () => {
		if (!feedback.trim() || !onRefine) return;

		setIsRefining(true);
		try {
			await onRefine(feedback.trim());
			setFeedback("");
			setShowFeedback(false);
		} catch (error) {
			console.error("Error refining content:", error);
		} finally {
			setIsRefining(false);
		}
	};

	if (isEditing) {
		return (
			<div className={cn("space-y-4", className)}>
				<div className="flex justify-between items-center">
					<h3 className="macos-text-title3 text-foreground">Edit Email</h3>
					<div className="flex gap-2">
						<Button variant="outline" size="sm" onClick={saveEdit}>
							Save
						</Button>
						<Button
							variant="outline"
							size="sm"
							onClick={() => setIsEditing(false)}
						>
							Cancel
						</Button>
					</div>
				</div>
				<div className="space-y-4">
					<div>
						<label className="block text-sm font-medium mb-2">Subject</label>
						<input
							type="text"
							placeholder="Email subject..."
							value={formData.subject}
							onChange={(e) =>
								setFormData((prev) => ({ ...prev, subject: e.target.value }))
							}
							className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring macos-text-body"
						/>
					</div>

					<div>
						<label className="block text-sm font-medium mb-2">Body</label>
						<Textarea
							placeholder="Email body content..."
							value={formData.body}
							onChange={(e) =>
								setFormData((prev) => ({ ...prev, body: e.target.value }))
							}
							rows={8}
							className="macos-text-body"
						/>
					</div>

					<div>
						<label className="block text-sm font-medium mb-2">
							Call to Action
						</label>
						<input
							type="text"
							placeholder="Call to action..."
							value={formData.call_to_action}
							onChange={(e) =>
								setFormData((prev) => ({
									...prev,
									call_to_action: e.target.value,
								}))
							}
							className="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring macos-text-body"
						/>
					</div>
				</div>
			</div>
		);
	}

	return (
		<div className={cn("space-y-4", className)}>
			<div className="flex justify-between items-center">
				<h3 className="macos-text-title3 text-foreground">Email Preview</h3>
				{!readOnly && (
					<div className="flex gap-2">
						<Button variant="outline" size="sm" onClick={startEditing}>
							<Edit3 className="w-4 h-4 mr-1" />
							Edit
						</Button>
						{onRefine && draft && (
							<Button
								variant="outline"
								size="sm"
								onClick={() => setShowFeedback(!showFeedback)}
							>
								<MessageSquare className="w-4 h-4 mr-1" />
								Feedback
							</Button>
						)}
					</div>
				)}
			</div>

			{/* Feedback Input */}
			{showFeedback && !readOnly && onRefine && (
				<div className="bg-muted/20 border border-border/40 rounded-lg p-4 space-y-3">
					<h4 className="macos-text-callout font-medium text-foreground">
						Provide feedback to refine this email
					</h4>
					<Textarea
						placeholder="e.g., Make it more casual, add a personal story, emphasize the key benefits..."
						value={feedback}
						onChange={(e) => setFeedback(e.target.value)}
						className="min-h-[100px]"
					/>
					<div className="flex justify-end gap-2">
						<Button
							variant="outline"
							size="sm"
							onClick={() => {
								setShowFeedback(false);
								setFeedback("");
							}}
						>
							Cancel
						</Button>
						<Button
							size="sm"
							onClick={handleFeedback}
							disabled={!feedback.trim() || isRefining}
						>
							{isRefining ? (
								<Loader2 className="w-4 h-4 mr-1 animate-spin" />
							) : (
								<Sparkles className="w-4 h-4 mr-1" />
							)}
							{isRefining ? "Refining..." : "Refine Email"}
						</Button>
					</div>
				</div>
			)}

			{/* Email Interface Mockup */}
			<div className="macos-material-content border border-border/60 rounded-lg overflow-hidden">
				{/* Email Header */}
				<div className="bg-muted/30 border-b border-border/40 p-4">
					<div className="space-y-2">
						<div className="flex items-center gap-2 macos-text-callout text-muted-foreground">
							<span className="w-12 text-right">From:</span>
							<span>you@company.com</span>
						</div>
						<div className="flex items-center gap-2 macos-text-callout text-muted-foreground">
							<span className="w-12 text-right">To:</span>
							<span>your-audience@email.com</span>
						</div>
						<div className="flex items-center gap-2 macos-text-body font-medium">
							<span className="w-12 text-right macos-text-callout text-muted-foreground">
								Subject:
							</span>
							<span className="text-foreground">
								{draft?.subject || "Your email subject will appear here"}
							</span>
						</div>
					</div>
				</div>

				{/* Email Body */}
				<div className="p-6 bg-white dark:bg-muted/10">
					<div className="prose prose-sm max-w-none">
						{draft?.body ? (
							<div className="macos-text-body text-foreground whitespace-pre-wrap leading-relaxed">
								{draft.body}
							</div>
						) : (
							<div className="macos-text-body text-muted-foreground italic">
								Your email content will appear here...
							</div>
						)}

						{draft?.call_to_action && (
							<div className="mt-6 p-4 bg-primary/5 border border-primary/20 rounded-md">
								<div className="macos-text-body font-medium text-primary">
									{draft.call_to_action}
								</div>
							</div>
						)}
					</div>
				</div>

				{/* Email Footer */}
				<div className="bg-muted/20 border-t border-border/40 p-3 macos-text-caption1 text-muted-foreground text-center">
					Email preview • Click Edit to modify content
				</div>
			</div>
		</div>
	);
}
