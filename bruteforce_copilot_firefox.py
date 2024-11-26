from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.edge.service import Service as EdgeService

# Set up Edge options to reuse the user session
edge_options = webdriver.EdgeOptions()
edge_options.add_argument("--disable-gpu")
edge_options.add_argument("--no-sandbox")
edge_options.add_argument("--disable-dev-shm-usage")
edge_options.add_argument(r"user-data-dir=C:\selenium_edge_profile")  # Use a different path

# Specify the Edge driver path
edge_driver_path = r"D:\WinInsProg\edgedriver_win64\msedgedriver.exe"

# Set up the web driver with options and specify the driver path using EdgeService
edge_service = EdgeService(executable_path=edge_driver_path)
driver = webdriver.Edge(service=edge_service, options=edge_options)

# Directly open the live video URL
video_url = "https://www.youtube.com/watch?v=IlRXhQYY6qI"
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
