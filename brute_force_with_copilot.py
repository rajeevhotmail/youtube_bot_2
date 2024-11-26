from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Set up Chrome options to reuse the user session
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(r"user-data-dir=D:\selenium_profile")  # Use a different path

# Set up the web driver with options
driver = webdriver.Chrome(options=chrome_options)

# Directly open the live video URL
video_url = "https://www.youtube.com/watch?v=RgCGzEZqi_k"
driver.get(video_url)

# Pause to allow manual login
print("Please log in to your YouTube account in the browser window.")
time.sleep(120)  # Wait for 2 minutes for manual login

# Wait for the page to load and ads to complete (5 minutes total)
time.sleep(180)  # Additional wait time after manual login

# Use WebDriverWait to ensure the chat box is clickable
chat_box = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "input"))
)

# Scroll to the chat box to ensure it is visible
driver.execute_script("arguments[0].scrollIntoView();", chat_box)

# Click the chat box to focus
chat_box.click()

# Type and send messages
messages = [
    "Hello everyone!",
    "Interesting topic!",
    "What do you think about the recent news?",
    "Can someone explain more on this?",
    "Great insights, thanks for sharing!",
    "Is there a follow-up to this discussion?",
    "Any resources to read more about this?"
]

for message in messages:
    chat_box.send_keys(message)
    chat_box.send_keys(Keys.RETURN)
    time.sleep(5)  # Wait a bit before sending the next message

# Close the browser after sending messages
driver.quit()
