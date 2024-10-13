import os
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from groq import Groq

from extract_frtdb import get_rtdb_frames
from complete_chat import complete_chat
from describe_video import describe_frames

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/converse_video")
async def converse_video(file: UploadFile = File(...)):
    if file.content_type not in ["video/mp4", "video/x-msvideo", "video/quicktime"]:
        raise HTTPException(
            status_code=400, detail="Invalid video format. Only mp4, avi, and mov formats are supported.")

    try:
        # Save the uploaded video to a temporary location
        client = Groq()

        video_path = f"/tmp/{file.filename}"
        with open(video_path, "wb") as f:
            bytes = await file.read()
            f.write(bytes)

        # Process the video and extract frames and words
        (frame_descriptions, transcript) = describe_frames(video_path, client)
        system_message, chat_completion = complete_chat(
            client,
            frame_descriptions,
            transcript,
        )

        # Return frames and corresponding words
        return JSONResponse(content={"chat": chat_completion.to_dict(), "prompt": system_message})
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred while processing the video: {e}")

    finally:
        # Cleanup: Delete the video file from temporary storage
        if os.path.exists(video_path):
            os.remove(video_path)


@app.post("/converse_frtdb")
async def converse_video():
    try:
        # Save the uploaded video to a temporary location
        client = Groq()

        # Process the video and extract frames and words
        (frame_descriptions, transcript) = get_rtdb_frames(client)
        system_message, chat_completion = complete_chat(
            client,
            frame_descriptions,
            transcript,
        )

        # Return frames and corresponding words
        return JSONResponse(content={"chat": chat_completion.to_dict(), "prompt": system_message})
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail=f"An error occurred while processing the video: {e}")
