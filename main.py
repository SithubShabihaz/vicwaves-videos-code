import os
import requests
from moviepy.editor import ImageClip, AudioFileClip

# GitHub Actions se aane wala data
IMAGE_URL = os.environ.get("IMAGE_URL")
AUDIO_URL = os.environ.get("AUDIO_URL")
CALLBACK_URL = os.environ.get("CALLBACK_URL")

def make_video():
    # 1. Download Files
    with open("image.webp", "wb") as f:
        f.write(requests.get(IMAGE_URL).content)
    with open("audio.mp3", "wb") as f:
        f.write(requests.get(AUDIO_URL).content)

    # 2. Generate Video
    image_clip = ImageClip("image.webp")
    audio_clip = AudioFileClip("audio.mp3")
    
    video_clip = image_clip.set_duration(audio_clip.duration)
    video_clip = video_clip.set_audio(audio_clip)
    
    video_clip.write_videofile("final_video.mp4", fps=24, codec="libx264", audio_codec="aac", logger=None)

    # 3. Send Video Back to n8n
    with open("final_video.mp4", "rb") as f:
        files = {'file': ('final_video.mp4', f, 'video/mp4')}
        requests.post(CALLBACK_URL, files=files)

if __name__ == "__main__":
    make_video()
