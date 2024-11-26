from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Set up the web driver (make sure chromedriver.exe is in your PATH or specify the path directly)
driver = webdriver.Chrome()

# Open the URL
driver.get("https://www.youtube.com")

# Wait for the page to load
time.sleep(3)

# Find the search box element
search_box = driver.find_element(By.NAME, "search_query")

# Enter text into the search box
search_box.send_keys("current affairs live")

# Simulate pressing the Enter key
search_box.send_keys(Keys.RETURN)

# Wait for the search results to load
time.sleep(3)

# Navigate to a specific live video URL
driver.get("https://www.youtube.com/watch?v=IlRXhQYY6qI")

# Wait for the page to load
time.sleep(5)

# Find the live chat input box
# Ensure you use the correct attributes
#chat_box = driver.find_element(By.XPATH, "//input[@class='style-scope yt-live-chat-input-field' or @id='correct-id-if-any']")
chat_box = driver.find_element(By.XPATH, "//input[@id='input']")


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
