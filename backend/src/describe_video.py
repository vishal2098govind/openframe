from typing import List, Tuple
from describe_image import describe_frame
from groq import Groq
from extract_frames import extract_frames_and_sync_words


def describe_frames(video_path: str, client: Groq) -> Tuple[list[str], str]:
    (frames, transcript) = extract_frames_and_sync_words(video_path, interval=1)

    frame_descriptions: List[str] = []
    for i, (f, words) in enumerate(frames):
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
