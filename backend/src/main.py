from dotenv import load_dotenv
from groq import Groq

from describe_video import describe_frames

load_dotenv()

client = Groq()
frame_descriptions = describe_frames(client)
system_message = """
You are a smart AI that need to read through descriptions of different frames taken from a video and answer user's questions.

The following are frame-wise descriptions of a video:
"""
for i, f in enumerate(frame_descriptions):
    system_message += "{f}\n\n".format(f=f)

system_message += """
DO NOT mention the frames, scenes or descriptions in your answer, just answer the question.
DO NOT try to generalize or provide possible scenarios.
ONLY use the information in the description of the frames to answer the question.
BE concise and specific."""

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": system_message,
        },
        {
            "role": "user",
            "content": "What is happening in this video?",
        },
    ],
    model="llama-3.1-8b-instant"
)

print(chat_completion.choices[0].message.content)
