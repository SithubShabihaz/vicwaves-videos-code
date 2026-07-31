import os
import textwrap
import requests
import subprocess
from urllib.parse import quote

IMAGE_URL = os.environ.get("IMAGE_URL")
AUDIO_URL = os.environ.get("AUDIO_URL")
CALLBACK_URL = os.environ.get("CALLBACK_URL")
POST_TITLE = os.environ.get("POST_TITLE", "Upcoming Social Security Adjustment")
POST_DESC = os.environ.get("POST_DESC", "The upcoming social security adjustment is drawing significant attention...")

def make_video():
    print("Downloading files...")
    
    # User-Agent header taake server request ko block na kare
    headers = {'User-Agent': 'Mozilla/5.0'}

    # 1. Download Image
    if IMAGE_URL:
        img_response = requests.get(IMAGE_URL, headers=headers)
        if img_response.status_code != 200 or len(img_response.content) < 100:
            raise Exception(f"Failed to download valid image from {IMAGE_URL}")
        with open("image.webp", "wb") as f:
            f.write(img_response.content)

    # 2. Download Audio (Spaces aur special characters ko handle karne ke liye safe encoding)
    if AUDIO_URL:
        encoded_audio_url = AUDIO_URL.replace(" ", "%20")
        audio_response = requests.get(encoded_audio_url, headers=headers)
        if audio_response.status_code != 200 or len(audio_response.content) < 100:
            raise Exception(f"Failed to download valid audio from {AUDIO_URL} (Status: {audio_response.status_code})")
        with open("audio.mp3", "wb") as f:
            f.write(audio_response.content)

    print("Generating video with Breaking News badge, Image, Title and Description...")

    # Title aur Description ko clean karna aur wrap karna
    clean_title = str(POST_TITLE).strip().replace("'", "").replace('"', "").replace(":", "-")
    wrapped_title = textwrap.wrap(clean_title, width=24)
    formatted_title = "\n".join(wrapped_title)

    clean_desc = str(POST_DESC).strip().replace("'", "").replace('"', "").replace(":", "-")
    wrapped_desc = textwrap.wrap(clean_desc, width=42)
    formatted_desc = "\n".join(wrapped_desc)

    # Linux GitHub runner par mojood standard bold font ka path:
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    # 3. FFmpeg command
    ffmpeg_command = [
        'ffmpeg',
        '-y',
        '-loop', '1',
        '-i', 'image.webp',
        '-i', 'audio.mp3',
        '-filter_complex',
        # Background 1080x1920 (black)
        f'color=c=black:s=1080x1920:d=10[base];'
        f'[0:v]scale=1080:-1[img];'
        f'[base][img]overlay=0:120[bg_with_img];'
        # Filter 1: Upar Red "Breaking News" Badge
        f'[bg_with_img]drawtext=fontfile=\'{font_path}\':text=\'Breaking News\':fontcolor=white:fontsize=46:box=1:boxcolor=red@0.95:boxborderw=18:x=(w-text_w)/2:y=80[with_badge];'
        # Filter 2: Image ke neeche Center-aligned Main Title
        f'[with_badge]drawtext=fontfile=\'{font_path}\':text=\'{formatted_title}\':fontcolor=white:fontsize=78:line_spacing=2:x=(w-text_w)/2:y=820[with_title];'
        # Filter 3: Title ke neeche Description Paragraph
        f'[with_title]drawtext=fontfile=\'{font_path}\':text=\'{formatted_desc}\':fontcolor=white@0.85:fontsize=35:line_spacing=4:x=(w-text_w)/2:y=1120[final]',
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
