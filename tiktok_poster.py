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
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
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
            
            print("Waiting for page elements to load...")
            time.sleep(15)

            # Screenshot lena taake pata chale page par kya khula hai
            page.screenshot(path="tiktok_error_screenshot.png")
            print("Screenshot saved as tiktok_error_screenshot.png")

            video_path = "final_video.mp4" 
            
            if os.path.exists(video_path):
                print(f"Uploading video: {video_path}")
                
                file_input = page.locator("input[type='file']")
                file_input.wait_for(state="attached", timeout=60000)
                file_input.set_input_files(video_path)
                
                print("Video file attached, waiting for upload processing...")
                time.sleep(15)

                print("Adding description...")
                caption_box = page.locator("div[contenteditable='true']").first
                caption_box.click()
                caption_box.fill(f"{post_title}\n\n{post_desc}")
                
                print("Clicking Publish button...")
                publish_btn = page.locator("button:has-text('Post')").first
                publish_btn.click()
                
                time.sleep(10)
                print("Video successfully published to TikTok!")
            else:
                print(f"Error: Video file {video_path} not found!")

        except Exception as e:
            print(f"An error occurred during TikTok upload: {e}")
            # Error ke waqt bhi screenshot lena
            page.screenshot(path="tiktok_crash_screenshot.png")
        
        finally:
            browser.close()

if __name__ == "__main__":
    upload_to_tiktok()
