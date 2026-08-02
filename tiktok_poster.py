import os
import time
import json
from playwright.sync_api import sync_playwright, TimeoutError

def upload_to_tiktok():
    post_title = os.getenv("POST_TITLE", "Default Title")
    post_desc = os.getenv("POST_DESC", "Default Description")
    tiktok_cookies_json = os.getenv("TIKTOK_COOKIES", "")
    
    print("Starting TikTok browser automation with enhanced loading...")

    with sync_playwright() as p:
        # 1. Browser ka size bara rakhein taake mobile view na khule
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Cookies Load Karein
        if tiktok_cookies_json:
            try:
                cookies = json.loads(tiktok_cookies_json)
                cleaned_cookies = []
                for cookie in cookies:
                    if "sameSite" in cookie and cookie["sameSite"] not in ["Strict", "Lax", "None"]:
                        cookie["sameSite"] = "Lax"
                    cleaned_cookies.append(cookie)
                context.add_cookies(cleaned_cookies)
                print("Session cookies loaded.")
            except Exception as e:
                print(f"Error loading cookies: {e}")

        page = context.new_page()

        try:
            # 2. Upload page par jayein
            print("Navigating to TikTok Creator Center...")
            # Timeout 60 seconds kar diya hai
            page.goto("https://www.tiktok.com/creator-center/upload?lang=en", timeout=60000)
            
            # 3. IMP: Page load hone ke baad mazeed 20 seconds ka intezaar (Sakoon se)
            print("Waiting 20s for page elements and popups to stabilize...")
            time.sleep(20) 

            video_path = "final_video.mp4" 
            
            if os.path.exists(video_path):
                print(f"Uploading video: {video_path}")
                
                # 4. File input dhoondein (ab 60 seconds tak wait karega)
                file_input_selector = "input[type='file']"
                # Pehle check karein ke element attached hai ya nahi
                page.wait_for_selector(file_input_selector, state="attached", timeout=60000)
                
                # Ab file upload karein
                file_input = page.locator(file_input_selector)
                file_input.set_input_files(video_path)
                
                # 5. IMP: Upload hone ke baad 15 seconds ka intezaar (Progress bar complete hone ke liye)
                print("Video attached, waiting 15s for upload to process...")
                time.sleep(15) 

                print("Adding description...")
                # Description box dhoond kar fill karein
                caption_box = page.locator("div[contenteditable='true']").first
                caption_box.click()
                caption_box.fill(f"{post_title}\n\n{post_desc}")
                
                time.sleep(5)

                print("Clicking Publish button...")
                # Publish button click karein
                publish_btn = page.locator("button:has-text('Post')").first
                publish_btn.click()
                
                # 6. IMP: Final publish hone ka intezaar
                print("Publishing, waiting 15s to complete...")
                time.sleep(15)
                print("Video successfully published to TikTok!")
                
                # Success ke baad screenshot lein (yeh dekhne ke liye ke post ho gayi)
                page.screenshot(path="tiktok_success.png")

            else:
                print(f"Error: Video file {video_path} not found!")

        except TimeoutError:
            print("TIMEOUT ERROR: Could not find file input or page element.")
            # Timeout hone par screenshot lein (debug ke liye)
            page.screenshot(path="tiktok_timeout_error.png")
        except Exception as e:
            print(f"An error occurred during TikTok upload: {e}")
            page.screenshot(path="tiktok_general_error.png")
        
        finally:
            browser.close()

if __name__ == "__main__":
    upload_to_tiktok()
