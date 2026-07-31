import os
import requests
import sys
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, TextClip, ColorClip

IMAGE_URL = os.environ.get("IMAGE_URL")
AUDIO_URL = os.environ.get("AUDIO_URL")
CALLBACK_URL = os.environ.get("CALLBACK_URL")
# n8n ya command line se ane wala title (agar na mile toh default)
POST_TITLE = os.environ.get("POST_TITLE", "Breaking News & Latest Updates")

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

    print("Generating vertical video layout with text...")
    
    # 3. Load Audio and get duration
    audio_clip = AudioFileClip("audio.mp3")
    duration = audio_clip.duration

    # 4. Create Vertical Canvas (1080x1920) with Black Background
    bg_clip = ColorClip(size=(1080, 1920), color=(0, 0, 0)).set_duration(duration)

    # 5. Load and Resize Image to fit top (Width 1080, maintaining aspect ratio)
    image_clip = ImageClip("image.webp").set_duration(duration)
    # Image ko width 1080 par resize karna
    image_clip = image_clip.resize(width=1080)
    # Image ko top par set karna (y=0)
    image_clip = image_clip.set_position(("center", "top"))

    # 6. Create Title Text Clip (White bold text with black background box)
    # Note: ImageMagick ya system fonts ke mutabiq font adjust ho sakta hai
    try:
        txt_clip = TextClip(
            POST_TITLE,
            fontsize=45,
            color='white',
            font='Arial-Bold',
            size=(980, None), # Width limit taake text wrap ho jaye
            method='caption'
        ).set_duration(duration)
        
        # Text ko image ke neeche position dena (maslan y=1100 ya image ke baad)
        txt_clip = txt_clip.set_position(("center", 1150))
        
        # Combine everything using CompositeVideoClip
        video_clip = CompositeVideoClip([bg_clip, image_clip, txt_clip])
    except Exception as e:
        print(f"TextClip warning ({e}), falling back to image + background only...")
        # Agar TextClip mein font ka masla ho toh sirf background aur image combine karega
        video_clip = CompositeVideoClip([bg_clip, image_clip])

    # 7. Set Audio to Video
    video_clip = video_clip.set_audio(audio_clip)
    
    # 8. Write final video file
    video_clip.write_videofile("final_video.mp4", fps=24, codec="libx264", audio_codec="aac", logger=None)

    print("Sending video back to n8n...")
    # 9. Send Video Back to n8n via Callback URL
    if CALLBACK_URL:
        with open("final_video.mp4", "rb") as f:
            files = {'file': ('final_video.mp4', f, 'video/mp4')}
            requests.post(CALLBACK_URL, files=files)
    
    print("Done!")

if __name__ == "__main__":
    make_video()
