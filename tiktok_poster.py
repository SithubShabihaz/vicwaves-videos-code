import os
import time
from playwright.sync_api import sync_playwright

def upload_to_tiktok():
    post_title = os.getenv("POST_TITLE", "Default Title")
    post_desc = os.getenv("POST_DESC", "Default Description")
    
    print("Starting TikTok browser automation...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto("https://www.tiktok.com/creator-center/upload?lang=en")
            time.sleep(5)

            # Yahan naam theek kar ke 'final_video.mp4' kar diya gaya hai
            video_path = "final_video.mp4" 
            
            if os.path.exists(video_path):
                print(f"Uploading video: {video_path}")
                file_input = page.locator("input[type='file']")
                file_input.set_input_files(video_path)
                
                time.sleep(10)

                print("Adding description...")
                caption_box = page.locator("div[contenteditable='true']").first
                caption_box.click()
                caption_box.fill(f"{post_title}\n\n{post_desc}")
                
                time.sleep(3)

                print("Clicking Publish button...")
                publish_btn = page.locator("button:has-text('Post')")
                publish_btn.click()
                
                time.sleep(10)
                print("Video successfully published to TikTok!")
            else:
                print(f"Error: Video file {video_path} not found!")

        except Exception as e:
            print(f"An error occurred during TikTok upload: {e}")
        
        finally:
            browser.close()

if __name__ == "__main__":
    upload_to_tiktok()
