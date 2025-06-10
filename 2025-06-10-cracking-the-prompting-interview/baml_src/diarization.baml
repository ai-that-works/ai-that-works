
class SpeakerSegment {
    dialoge_index int @alias("index")
    speaker "DOCTOR" | "PATIENT" | "OTHER"
    assesment string[] @description(#"
        final assesment of the speaker given any prior clues in comments, use phrases not complete sentences
    "#)
}


function DiarizeTranscript(transcript: string[], context: string) -> SpeakerSegment[] {
    client CustomSonnet
    prompt #"
        Identify the speakers.

        {{ ctx.output_format(prefix="Answer with this schema:\n") }}

        if speaker is ambiguous, list relevant facts to help narrow down the speaker before the speaker field
        [
            ..,
            { 
                idx: N,
                // used first person pronouns
                // had an accident
                speaker: "PATIENT",
                assesment: [ .. ]
            }
        ]

        for context, {{ context }}

        {{ _.role('user') }}
        {% for line in transcript %}
        dialog_{{ loop.index0 }}:
        {{ line }}
        
        {% endfor %}
    "#
}

// Test the diarization function with a sample transcript
test diarize_conversation {
    functions [DiarizeTranscript]
    args {
        transcript [
            "Hello, how are you?"
            "I'm hurt! my knee hurts!"
            "I'm sorry to hear that."
            "Its been hurting for 3 days now."
            "He's been complaining about it for a while."
        ]
        context #"
            There were 4 poeple in the room:
            - Doctor Josh
            - Nurse Vaibhav
            - Patient Dexter
            - Unknown person
        "#
    }
}
