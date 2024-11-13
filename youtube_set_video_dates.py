#!/usr/bin/env python3
from datetime import datetime, timedelta
import locale
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc

# The settings
date_start = "11 nov 2024"
number_of_days = 10
videos_per_date = 3
locale.setlocale(locale.LC_TIME, 'es_EC.utf8')
driver = uc.Chrome()
driver.set_page_load_timeout(60)
wait = WebDriverWait(driver, 60)

def set_video_data(driver: webdriver.Chrome, wait: WebDriverWait, date: str, is_short: bool, is_first: bool = False):
    # Clik each video and set all the required data
    # Open the first video
    video = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="video-thumbnail"]')))
    ActionChains(driver).move_to_element(video).click().perform()

    # Set the playlist
    select_list = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="basics"]/div[4]/div[3]/div[1]/ytcp-video-metadata-playlists/ytcp-text-dropdown-trigger/ytcp-dropdown-trigger/div/div[3]')))
    ActionChains(driver).move_to_element(select_list).click().perform()
    playlist = wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="checkbox-{1 if is_first else 0}"]'))) # The playlist that appears first is the last one saved

    ActionChains(driver).move_to_element(playlist).click().perform()
    ready_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="dialog"]/div[2]/ytcp-button[2]/ytcp-button-shape/button')))
    ActionChains(driver).move_to_element(ready_button).click().perform()

    # Open for more options
    show_more_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="toggle-button"]')))
    ActionChains(driver).move_to_element(show_more_button).click().perform()

    # Mark as AI
    is_ai_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="details"]/div/ytcp-video-metadata-editor-advanced/div[2]/ytkp-altered-content-select/div[2]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[1]')))
    ActionChains(driver).move_to_element(is_ai_button).click().perform()

    # Remove from feed
    feed_checkbox = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-advanced/div[9]/div[4]/ytcp-checkbox-lit/div')))
    ActionChains(driver).move_to_element(feed_checkbox).click().perform()

    # Click on next
    next_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="next-button"]')))
    ActionChains(driver).move_to_element(next_button).click().perform()

    if not is_short:
        # Click on add final screen
        add_final_screen_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="endscreens-button"]')))
        ActionChains(driver).move_to_element(add_final_screen_button).click().perform()

        # Click on import from other video
        import_from_video_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="import-endscreen-from-video-button"]')))
        ActionChains(driver).move_to_element(import_from_video_button).click().perform()

    else:
        # Click on the add content button
        add_content_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="shorts-content-links-add-button"]')))
        ActionChains(driver).move_to_element(add_content_button).click().perform()
    
    # Search for the video
    search_video_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search-yours"]')))
    search_video_input.send_keys("la maldición de la vacuna #terror #miedo")
    time.sleep(10)

    retry = 0
    while True:
        try:
            # Click on the video
            video_to_import = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="dialog"]/div[2]/div/ytcp-video-pick-dialog-contents/div/div/div/ytcp-entity-card')))
            time.sleep(10)
            ActionChains(driver).move_to_element(video_to_import).click().perform()
            time.sleep(10)
            break
        except Exception as e:
            print(e)
            retry += 1
            if retry >= 5:
                raise e
            time.sleep(5)

    if not is_short:
        # Click on save
        save_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="save-button"]')))
        ActionChains(driver).move_to_element(save_button).click().perform()
        time.sleep(10)

    # Click on next
    next_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="next-button"]')))
    ActionChains(driver).move_to_element(next_button).click().perform()
    time.sleep(10)

    # Click on next
    next_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="next-button"]')))
    ActionChains(driver).move_to_element(next_button).click().perform()
    time.sleep(10)

    retry = 0
    while True:
        try:
            # Click on expand to set the date
            expand_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="second-container-expand-button"]')))
            time.sleep(2)
            ActionChains(driver).move_to_element(expand_button).click().perform()

            # Click on the date input trigger
            date_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="datepicker-trigger"]')))
            time.sleep(2)
            ActionChains(driver).move_to_element(date_input).click().perform()

            # Set the date on the input box
            date_input_box = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="input-2"]/input')))
            time.sleep(2)
            date_input_box.send_keys("\b" * 20)
            date_input_box.send_keys(date)
            date_input_box.send_keys("\n")
            time.sleep(10)
            break
        except Exception as e:
            print(e)
            retry += 1
            if retry >= 5:
                raise e
            time.sleep(5)

    # Click on the done button
    done_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="done-button"]')))
    ActionChains(driver).move_to_element(done_button).click().perform()

driver.get("https://www.youtube.com/signin")

# Wait for the sign in to be done
input("Press Enter to continue after singing in")

# Change account to the one we want to use
account_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="avatar-btn"]')))
ActionChains(driver).move_to_element(account_button).click().perform()
change_account_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="items"]/ytd-compact-link-renderer[2]')))
ActionChains(driver).move_to_element(change_account_button).click().perform()
account_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="contents"]/ytd-account-item-renderer[2]')))
ActionChains(driver).move_to_element(account_button).click().perform()

def run_loop(is_short: bool):
    date = date_start
    videos_for_date = 0
    days = 0
    is_first = True
    while True:
        if not is_short:
            # Videos page
            driver.get("https://studio.youtube.com/channel/REDACTED_CHANNEL_ID/videos/upload?filter=%5B%7B%22name%22%3A%22VISIBILITY%22%2C%22value%22%3A%5B%22DRAFT%22%5D%7D%5D&sort=%7B%22columnType%22%3A%22views%22%2C%22sortOrder%22%3A%22DESCENDING%22%7D")
        else:
            # Shorts page
            driver.get("https://studio.youtube.com/channel/REDACTED_CHANNEL_ID/videos/short?filter=%5B%7B%22name%22%3A%22VISIBILITY%22%2C%22value%22%3A%5B%22DRAFT%22%5D%7D%5D&sort=%7B%22columnType%22%3A%22views%22%2C%22sortOrder%22%3A%22DESCENDING%22%7D")

        # Verify if the "no content" message is present
        videos_div = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="video-list"]/div/div[2]')))
        # If the div has the class "no-content", then there are no videos to set
        if "no-content" in videos_div.get_attribute("class"):
            print("No videos to set")
            break
        
        # Set the video
        set_video_data(driver, wait, date, is_short, is_first)
        is_first = False
        videos_for_date += 1
        time.sleep(10)
        # If we have set enough videos for the date, then we change the date
        if videos_for_date >= videos_per_date:
            print(f"Finished setting {'shorts' if is_short else 'videos'} for {date}")
            days += 1
            # If we have set the required number of days, then we break
            if days >= number_of_days:
                break
            videos_for_date = 0
            # Parse the current date
            current_date = datetime.strptime(date, "%d %b %Y")
            # Increment the date by one day
            new_date = current_date + timedelta(days=1)
            # Format the new date back to the required format
            date = new_date.strftime("%d %b %Y")

# Run for videos
run_loop(False)
# Run for shorts
# run_loop(True)

driver.quit()
