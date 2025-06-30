import {
	CheckCircle,
	Clock,
	FileText,
	Loader2,
	Video,
	XCircle,
} from "lucide-react"; // Added AlertTriangle

export const getVideoStatusIcon = (status: string | undefined) => {
	switch (status) {
		case "ready":
			return <CheckCircle className="w-5 h-5 text-green-500" />;
		case "failed":
			return <XCircle className="w-5 h-5 text-red-500" />;
		case "processing":
			return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
		default:
			return <Clock className="w-5 h-5 text-gray-500" />;
	}
};

export const getRecordingTypeIcon = (type: string | undefined) => {
	switch (type) {
		case "shared_screen_with_speaker_view":
		case "shared_screen_with_speaker_view(CC)":
			return <Video className="w-4 h-4 text-blue-600" />;
		case "audio_only":
			return <FileText className="w-4 h-4 text-green-600" />;
		case "audio_transcript":
			return <FileText className="w-4 h-4 text-purple-600" />;
		default:
			return <FileText className="w-4 h-4 text-gray-600" />;
	}
};
