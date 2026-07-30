from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from moviepy.editor import ImageClip, AudioFileClip
import requests
import tempfile
import os

app = FastAPI(title="Video Generator API")

# n8n se aane wale data ka format
class VideoRequest(BaseModel):
    image_url: str
    audio_url: str

@app.post("/create-video")
def create_youtube_short(request: VideoRequest):
    try:
        # 1. Image (WebP) ko download kar ke temporary file main save karna
        img_response = requests.get(request.image_url)
        img_response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webp") as img_file:
            img_file.write(img_response.content)
            img_path = img_file.name
            
        # 2. Audio (MP3) ko download kar ke temporary file main save karna
        audio_response = requests.get(request.audio_url)
        audio_response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audio_file:
            audio_file.write(audio_response.content)
            audio_path = audio_file.name

        # 3. Final MP4 ke liye ek temporary path banana
        output_path = tempfile.mktemp(suffix=".mp4")

        # 4. MoviePy ke zariye Video Render karna
        image_clip = ImageClip(img_path)
        audio_clip = AudioFileClip(audio_path)
        
        # Video ki length audio ke barabar set karna
        video_clip = image_clip.set_duration(audio_clip.duration)
        video_clip = video_clip.set_audio(audio_clip)
        
        # MP4 file likhna (libx264 aur aac codecs ke sath)
        video_clip.write_videofile(
            output_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            logger=None # Console par extra text rokne ke liye
        )
        
        # Memory clear karna
        image_clip.close()
        audio_clip.close()
        
        # 5. Final video wapas n8n ko bhej dena
        return FileResponse(
            output_path, 
            media_type="video/mp4", 
            filename="youtube_short.mp4"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))