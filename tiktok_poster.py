import os
import time
import json
from playwright.sync_api import sync_playwright

def upload_to_tiktok():
    post_title = os.getenv("POST_TITLE", "Default Title")
    post_desc = os.getenv("POST_DESC", "Default Description")
    tiktok_cookies_json = os.getenv("TIKTOK_COOKIES", "")
    
    print("Starting TikTok browser automation with session cookies...")

    with sync_playwright() as p:
        # Headless ko True rakha hai taake cloud par chale
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800} # Browser ka size bara rakhna zaroori hai
        )

        if tiktok_cookies_json:
            try:
                cookies = json.loads(tiktok_cookies_json)
                cleaned_cookies = []
                for cookie in cookies:
                    if "sameSite" in cookie:
                        val = cookie["sameSite"]
                        if val not in ["Strict", "Lax", "None"]:
                            cookie["sameSite"] = "Lax"
                    cleaned_cookies.append(cookie)
                
                context.add_cookies(cleaned_cookies)
                print("Successfully loaded and cleaned TikTok session cookies.")
            except Exception as e:
                print(f"Error loading cookies: {e}")

        page = context.new_page()

        try:
            print("Navigating to TikTok Creator Center...")
            page.goto("https://www.tiktok.com/creator-center/upload?lang=en", timeout=60000)
            
            # Page ko poori tarah load hone ke liye 15 seconds ka sakoon se intezar
            print("Waiting for page elements to load...")
            time.sleep(15)

            video_path = "final_video.mp4" 
            
            if os.path.exists(video_path):
                print(f"Uploading video: {video_path}")
                
                # File input box ke liye thora lamba wait dena (upto 60 seconds)
                file_input = page.locator("input[type='file']")
                file_input.wait_for(state="attached", timeout=60000)
                file_input.set_input_files(video_path)
                
                print("Video file attached, waiting for upload processing...")
                time.sleep(15) # Video upload hone ka intezar

                print("Adding description...")
                # Caption box ke liye behtar selector
                caption_box = page.locator("div[contenteditable='true']").first
                caption_box.click()
                caption_box.fill(f"{post_title}\n\n{post_desc}")
                
                time.sleep(5)

                print("Clicking Publish button...")
                # Post button dhoond kar click karna
                publish_btn = page.locator("button:has-text('Post')").first
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
