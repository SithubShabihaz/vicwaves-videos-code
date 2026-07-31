import os
import textwrap
import requests
import subprocess

IMAGE_URL = os.environ.get("IMAGE_URL")
AUDIO_URL = os.environ.get("AUDIO_URL")
CALLBACK_URL = os.environ.get("CALLBACK_URL")
POST_TITLE = os.environ.get("POST_TITLE", "Trump Warns Mamdani")

def make_video():
    print("Downloading files...")
    
    # 1. Download Image
    img_response = requests.get(IMAGE_URL)
    if img_response.status_code != 200 or len(img_response.content) < 100:
        raise Exception(f"Failed to download valid image from {IMAGE_URL}")
    with open("image.webp", "wb") as f:
        f.write(img_response.content)

    # 2. Download Audio
    audio_response = requests.get(AUDIO_URL)
    if audio_response.status_code != 200 or len(audio_response.content) < 100:
        raise Exception(f"Failed to download valid audio from {AUDIO_URL}")
    with open("audio.mp3", "wb") as f:
        f.write(audio_response.content)

    print("Generating video with bold font and left/right spacing...")

    # Title ko clean karna
    clean_title = str(POST_TITLE).strip().replace("'", "").replace('"', "").replace(":", "-")

    # Text wrapping: width=22 rakhne se text dono sides (left aur right) se andar rahega aur katega nahi
    wrapped_lines = textwrap.wrap(clean_title, width=22)
    formatted_title = "\n".join(wrapped_lines)

    # Linux GitHub runner par mojood standard bold font ka path:
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    # 3. FFmpeg command: Breaking news remove kar diya gaya hai aur x=60 se left/right margin set hai
    ffmpeg_command = [
        'ffmpeg',
        '-y',
        '-loop', '1',
        '-i', 'image.webp',
        '-i', 'audio.mp3',
        '-filter_complex',
        # Background 1080x1920 (black), image top par overlay=0:0
        f'color=c=black:s=1080x1920:d=10[base];'
        f'[0:v]scale=1080:-1[img];'
        f'[base][img]overlay=0:0[bg_with_img];'
        # Main Bold Title (x=60 se left margin mil gaya hai, aur boxborderw=30 se padding set hai)
        f'[bg_with_img]drawtext=fontfile=\'{font_path}\':text=\'{formatted_title}\':fontcolor=white:fontsize=75:line_spacing=4:box=1:boxcolor=black@0.95:boxborderw=30:x=60:y=800[final]',
        '-map', '[final]',
        '-map', '1:a',
        '-shortest',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        'final_video.mp4'
    ]

    # Run command
    result = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise Exception(f"FFmpeg failed: {result.stderr}")

    print("Sending video back to n8n...")
    if CALLBACK_URL:
        with open("final_video.mp4", "rb") as f:
            files = {'file': ('final_video.mp4', f, 'video/mp4')}
            requests.post(CALLBACK_URL, files=files)
    
    print("Done!")

if __name__ == "__main__":
    make_video()
