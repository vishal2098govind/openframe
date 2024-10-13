from typing import List, Tuple
import firebase_admin
from firebase_admin import credentials, db
import re
import base64
from datetime import datetime

from groq import Groq

from describe_image import describe_frame
from extract_frames import extract_frames_with_words


# Function to decode base64 string and save the image


def save_base64_image(image_string, file_name):
    image_data = base64.b64decode(image_string)
    with open(file_name, 'wb') as f:
        f.write(image_data)
    print(f"Image saved as {file_name}")

# Helper function to compare timestamps


def is_valid_timestamp(key, min_timestamp):
    try:
        # Extract timestamp from key and compare it with min_timestamp
        key_timestamp = datetime.strptime(key, '%Y%m%d_%H%M%S')
        return key_timestamp < min_timestamp
    except ValueError:
        # If the key doesn't match the expected timestamp format, skip it
        return False


def get_rtdb_frames(client: Groq) -> Tuple[list[str], str]:
    # Initialize the Firebase app (assuming your serviceAccountKey.json file is properly set up)
    cred = credentials.Certificate('backend/src/serviceAccountKey.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://openframe-34a6f-default-rtdb.firebaseio.com/'
    })

    # Define the base64 regex pattern (this should match base64 strings)
    base64_pattern = re.compile(
        r'^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$')

    # Define the minimum timestamp as a datetime object
    min_timestamp = datetime.strptime('20241013_132106', '%Y%m%d_%H%M%S')

    # Fetch the data from Firebase
    images_ref = db.reference('/images')
    audio_ref = db.reference('/audio/20241013_131959')
    images_data = images_ref.get()
    audio_data = audio_ref.get()

    # Filter and process only the base64 strings with valid timestamps
    frames: list[str] = []
    for key, value in images_data.items():
        if is_valid_timestamp(key, min_timestamp):
            if isinstance(value, str) and base64_pattern.match(value):
                # If the value matches the base64 pattern, decode and save the image
                print(f"Found base64 image data for key: {key}")
                frames.append(value)
                # save_base64_image(value, f"video_frames/{key}.jpg")
            else:
                print(f"Skipping non-base64 entry: {key}")
        else:
            print(
                f"Skipping key with timestamp earlier than {min_timestamp}: {key}")

    (transcript, frames_with_words) = extract_frames_with_words(
        frames, base64.b64decode(audio_data))

    frame_descriptions: List[str] = []
    for i, (f, words) in enumerate(frames_with_words):
        description = describe_frame(client, f, i)
        frame_desc = """Frame #{i}
- Description: 
    {description}

- Words Spoken in Frame #{i}(with start/end timestamp): 

{words}
            """.format(i=i+1, description=description, words="\n ".join(words) if words else "No words")

        frame_descriptions.append(frame_desc)
        print(frame_desc)

        print("\n\n")
    return (frame_descriptions, transcript)
