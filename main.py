import os
import requests
from moviepy.editor import ImageClip, AudioFileClip

IMAGE_URL = os.environ.get("IMAGE_URL")
AUDIO_URL = os.environ.get("AUDIO_URL")
CALLBACK_URL = os.environ.get("CALLBACK_URL")

def make_video():
    print("Downloading files...")
    
    # 1. Download Image with error handling
    img_response = requests.get(IMAGE_URL)
    if img_response.status_code != 200 or len(img_response.content) < 100:
        raise Exception(f"Failed to download valid image from {IMAGE_URL}")
    with open("image.webp", "wb") as f:
        f.write(img_response.content)

    # 2. Download Audio with error handling
    audio_response = requests.get(AUDIO_URL)
    if audio_response.status_code != 200 or len(audio_response.content) < 100:
        raise Exception(f"Failed to download valid audio from {AUDIO_URL}")
    with open("audio.mp3", "wb") as f:
        f.write(audio_response.content)

    print("Generating video...")
    # 3. Generate Video
    image_clip = ImageClip("image.webp")
    audio_clip = AudioFileClip("audio.mp3")
    
    video_clip = image_clip.set_duration(audio_clip.duration)
    video_clip = video_clip.set_audio(audio_clip)
    
    video_clip.write_videofile("final_video.mp4", fps=24, codec="libx264", audio_codec="aac", logger=None)

    print("Sending video back to n8n...")
    # 4. Send Video Back to n8n
    with open("final_video.mp4", "rb") as f:
        files = {'file': ('final_video.mp4', f, 'video/mp4')}
        requests.post(CALLBACK_URL, files=files)
    
    print("Done!")

if __name__ == "__main__":
    make_video()
