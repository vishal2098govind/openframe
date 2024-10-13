from moviepy.editor import VideoFileClip


def extract_audio_intervals(video_path, interval_duration, output_folder):
    # Load the video file
    video = VideoFileClip(video_path)

    # Get the total duration of the video
    total_duration = video.duration

    # Extract the audio from the video
    audio = video.audio

    # Loop through the video duration at specified intervals
    for start_time in range(0, int(total_duration), interval_duration):
        # Set the end time for the current clip
        end_time = min(start_time + interval_duration, total_duration)

        # Extract the audio segment
        audio_clip = audio.subclip(start_time, end_time)

        # Define the output file name
        output_file = f"{output_folder}/audio_clip_{start_time}_to_{end_time}.mp3"

        # Write the audio segment to an MP3 file
        audio_clip.write_audiofile(output_file)
        print(
            f"Saved audio clip from {start_time} to {end_time} seconds as {output_file}")

    # Close the video and audio clips
    video.close()


# Example usage
video_path = "https://firebasestorage.googleapis.com/v0/b/askchuck.appspot.com/o/videos%2Fpizza_choice.mp4?alt=media&token=64938511-3244-4207-819a-26e5a5f0036c"  # Path to the input video
output_folder = "./audio_clips"  # Folder to save audio clips
interval_duration = 1  # Interval in seconds to extract audio

extract_audio_intervals(video_path, interval_duration, output_folder)
