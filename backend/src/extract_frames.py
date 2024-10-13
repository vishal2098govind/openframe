import ffmpeg
from io import BytesIO
from typing import List, Tuple
import cv2
import base64
from PIL import Image

from transcribe_audio_bytes import transcribe_audio_bytes


def extract_frames(video_path: str, interval=1):
    # Open the video file
    vidcap = cv2.VideoCapture(video_path)

    if not vidcap.isOpened():
        print(f"Error: Unable to open video file {video_path}")
        return

    # Get the frames per second (fps) of the video
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    print(f"Frames per second: {fps}")

    # Calculate the frame interval
    frame_interval = int(fps * interval)

    success, image = vidcap.read()
    count = 0
    base64_frames: List[str] = []

    while success:
        if count % frame_interval == 0:
            # Convert the frame (BGR in OpenCV) to RGB (PIL format)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Convert the image to a PIL Image
            pil_image = Image.fromarray(image_rgb)

            # Save the image to a BytesIO object
            buffer = BytesIO()
            pil_image.save(buffer, format="JPEG")

            # Get the byte data from the buffer
            byte_data = buffer.getvalue()

            # Encode the byte data as Base64
            base64_data = base64.b64encode(byte_data).decode('utf-8')

            # Append the base64 string of the frame to the list
            base64_frames.append(base64_data)

            print(f"Frame {count // frame_interval} converted to Base64")

        success, image = vidcap.read()
        count += 1

    vidcap.release()
    return base64_frames


def extract_frames_and_sync_words(video_path: str, interval=1) -> Tuple[List[Tuple[str, List[str]]], str]:
    """
    Extracts frames and associates words spoken during each frame using Deepgram's STT.
    Returns a list of tuples where each tuple contains the base64 frame and corresponding words spoken.
    """
    # Open the video file
    vidcap = cv2.VideoCapture(video_path)

    if not vidcap.isOpened():
        print(f"Error: Unable to open video file {video_path}")
        return []

    # Get video properties
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Calculate the frame interval
    frame_interval = int(fps * interval)

    success, image = vidcap.read()
    count = 0
    base64_frames = []

    while success:
        if count % frame_interval == 0:
            # Get the current timestamp of the frame
            timestamp = count / fps  # Time in seconds for the frame

            # Convert the frame to a base64 image
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            buffer = BytesIO()
            pil_image.save(buffer, format="JPEG")
            byte_data = buffer.getvalue()
            base64_frame = base64.b64encode(byte_data).decode('utf-8')

            base64_frames.append(base64_frame)

        success, image = vidcap.read()
        count += 1

    vidcap.release()

    # Extract audio using ffmpeg for the entire video
    out, _ = (
        ffmpeg.input(video_path)
        .output('pipe:', format='wav')
        .run(capture_stdout=True, capture_stderr=True)
    )

    # Get audio transcription from Deepgram
    transcript, frames_with_words = extract_frames_with_words(
        base64_frames,
        out
    )

    return (frames_with_words, transcript)


def extract_frames_with_words(base64_frames: list[str], out: bytes):
    response = transcribe_audio_bytes(out)
    word_timings = response['results']['channels'][0]['alternatives'][0]['words']
    transcript = response['results']['channels'][0]['alternatives'][0]['transcript']

    # Group words with the corresponding frames based on their timestamps
    frames_with_words = []
    word_index = 0

    for i, _ in enumerate(base64_frames):
        words_for_frame = []

        while word_index < len(word_timings):
            word_info = word_timings[word_index]
            word_start = word_info['start']
            word_end = word_info['end']

            # Check if the word overlaps with the current frame time
            if word_start <= i+1:
                # if word_start <= frame_time <= word_end:
                words_for_frame.append(
                    f"word spoken:{word_info['word']}\n(start_timestamp:{word_start}, end_timestamp:{word_end})")
                word_index += 1
            else:
                break

        frames_with_words.append((base64_frames[i], words_for_frame))
        print(f"words: {words_for_frame}")
    return transcript, frames_with_words


# extract_frames_and_sync_words(
#     "https://firebasestorage.googleapis.com/v0/b/askchuck.appspot.com/o/videos%2Fpizza_choice.mp4?alt=media&token=64938511-3244-4207-819a-26e5a5f0036c")
