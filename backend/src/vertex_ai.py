
import vertexai
from vertexai.generative_models import GenerativeModel, Part

PROJECT_ID = "askchuck"
vertexai.init(project=PROJECT_ID, location="us-central1")

model = GenerativeModel("gemini-2.0-flash-001")

prompt = """
You are a smart AI that need to go through the video and answer any question being asked in the video based on what you saw in the video.
"""

video_file = Part.from_uri(
    uri="https://firebasestorage.googleapis.com/v0/b/askchuck.appspot.com/o/videos%2Fpizza_choice.mp4?alt=media&token=64938511-3244-4207-819a-26e5a5f0036c",
    mime_type="video/mp4",
)

contents = [video_file, prompt]

response = model.generate_content(contents)
print(response.text)
