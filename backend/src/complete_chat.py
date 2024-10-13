from groq import Groq


def complete_chat(client: Groq, frame_descriptions: list[str], transcript: str):
    system_message = """
You are a smart AI tasked with answering questions primarily based on the spoken words from the video's audio, along with their timestamps. You may use visual descriptions of frames as supplementary information when necessary.
The following are frame-wise descriptions of a video and the words spoken during each frame, along with their timestamps:
"""
    for _, f in enumerate(frame_descriptions):
        system_message += "{f}\n\n".format(f=f)

    system_message += f"""
**Following is the Full Transcript of audio spoken**:
    - {transcript}
DO NOT explicitly mention the frames, scenes, or descriptions in your answer.
DO NOT try to generalize or provide hypothetical scenarios.
ONLY use the spoken words (with their timestamps) and descriptions as supporting information.
Focus primarily on the spoken words from the audio to answer the user's question.
BE concise and specific in your responses."""

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": transcript,
            },
        ],
        model="llama-3.1-8b-instant"
    )

    print("complete prompt:")

    print(system_message)
    return system_message, chat_completion
