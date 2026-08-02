import os
import time
import json
from playwright.sync_api import sync_playwright, TimeoutError

def upload_to_tiktok():
    post_title = os.getenv("POST_TITLE", "Default Title")
    post_desc = os.getenv("POST_DESC", "Default Description")
    tiktok_cookies_json = os.getenv("TIKTOK_COOKIES", "")
    
    print("Starting TikTok browser automation with robust selectors...")

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
                    if "sameSite" in cookie and cookie["sameSite"] not in ["Strict", "Lax", "None"]:
                        cookie["sameSite"] = "Lax"
                    cleaned_cookies.append(cookie)
                context.add_cookies(cleaned_cookies)
                print("Session cookies loaded successfully.")
            except Exception as e:
                print(f"Error loading cookies: {e}")

        page = context.new_page()

        try:
            print("Navigating to TikTok Creator Center...")
            page.goto("https://www.tiktok.com/creator-center/upload?lang=en", timeout=60000)
            
            print("Waiting 15s for page elements to load...")
            time.sleep(15) 

            video_path = "final_video.mp4" 
            
            if os.path.exists(video_path):
                print(f"Uploading video file: {video_path}")
                
                # File input select kar ke video attach karna
                file_input = page.locator("input[type='file']")
                file_input.wait_for(state="attached", timeout=60000)
                file_input.set_input_files(video_path)
                
                print("Video attached, waiting 25s for upload & preview processing...")
                time.sleep(25) # Upload complete hone aur elements aane ka intezaar

                print("Adding description/caption...")
                # Caption box ke liye multiple reliable selectors try karna
                caption_filled = False
                
                try:
                    # Tareeqa 1: Contenteditable div
                    caption_box = page.locator("div[contenteditable='true']").first
                    caption_box.wait_for(state="visible", timeout=15000)
                    caption_box.click()
                    caption_box.fill(f"{post_title}\n\n{post_desc}")
                    caption_filled = True
                except:
                    print("Trying alternative caption selector...")
                    try:
                        # Tareeqa 2: Draft editor / textarea
                        caption_box = page.locator(".public-DraftEditor-content, textarea").first
                        caption_box.wait_for(state="visible", timeout=15000)
                        caption_box.click()
                        caption_box.fill(f"{post_title}\n\n{post_desc}")
                        caption_filled = True
                    except Exception as ex:
                        print(f"Could not fill caption automatically: {ex}")

                if caption_filled:
                    print("Description added successfully.")
                
                time.sleep(5)

                print("Clicking Publish button...")
                # Post/Publish button dhoond kar click karna
                try:
                    publish_btn = page.locator("button:has-text('Post'), button:has-text('Publish')").last
                    publish_btn.wait_for(state="visible", timeout=15000)
                    publish_btn.click()
                    print("Publish button clicked!")
                except Exception as e:
                    print(f"Error clicking publish button: {e}")
                
                print("Waiting 15s to finalize posting...")
                time.sleep(15)
                print("TikTok automation finished execution.")

            else:
                print(f"Error: Video file {video_path} not found!")

        except TimeoutError as te:
            print(f"TIMEOUT ERROR encountered: {te}")
        except Exception as e:
            print(f"An error occurred during TikTok upload: {e}")
        
        finally:
            browser.close()

if __name__ == "__main__":
    upload_to_tiktok()
