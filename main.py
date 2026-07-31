import os
import textwrap
import requests
import subprocess

IMAGE_URL = os.environ.get("IMAGE_URL")
AUDIO_URL = os.environ.get("AUDIO_URL")
CALLBACK_URL = os.environ.get("CALLBACK_URL")
POST_TITLE = os.environ.get("POST_TITLE", "Breaking News And Latest Updates")

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

    print("Generating video with Breaking News badge and bold title...")

    # Title ko clean karna aur Sentence Case rakhna
    clean_title = str(POST_TITLE).strip().replace("'", "").replace('"', "").replace(":", "-")
    formatted_sentence = clean_title.capitalize()

    # Text wrapping: Baray font ke liye width choti rakhi hai taake text theek se wrap ho
    wrapped_lines = textwrap.wrap(formatted_sentence, width=26)
    formatted_title = "\n".join(wrapped_lines)

    # 3. FFmpeg command: Pehle Breaking News ka badge, phir main bara title draw karega
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
        # Filter 1: Upar "Breaking News" ka blue/dark rounded style box aur text
        f'[bg_with_img]drawtext=text=\'Breaking News\':fontcolor=white:fontsize=40:box=1:boxcolor=navy@0.9:boxborderw=18:x=(w-text_w)/2:y=1010[with_badge];'
        # Filter 2: Neeche main bara bold title
        f'[with_badge]drawtext=text=\'{formatted_title}\':fontcolor=white:fontsize=70:line_spacing=-2:box=1:boxcolor=black@0.95:boxborderw=25:x=50:y=1120[final]',
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
