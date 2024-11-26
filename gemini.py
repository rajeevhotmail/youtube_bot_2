
import json
import time
from datetime import datetime, timezone
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

import googleapiclient.discovery
import threading  # Import the threading module


def load_target_users(filename="target_users.json"):
    """Loads the target users and their messages from a JSON file."""
    try:
        with open(filename, "r") as f:
            target_users = json.load(f)
            print("Target users reloaded:", target_users)  # Print the reloaded data
            return target_users
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{filename}'.")
        return {}

def  reload_target_users_thread():

    """Reloads the target users in a separate thread."""
    global target_users
    target_users = load_target_users()


# Set the scopes required for accessing the YouTube API
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Load the OAuth 2.0 client credentials file
CLIENT_SECRET_FILE = "credential.json"

# List of strings to send (consider adding more variety)
strs = [
    "Dhoondho-dhoondho re saajana, dhoondho re saajana\nMore balam ka gola\nHo, dhoondho-dhoondho re saajana, dhoondho re saajana\nMore balam ka gola",
    # ... (rest of your strings)
]

# List of abusive words (extend this list as needed)
abusive_words = ["abuse1", "abuse2", "offensiveWord"]

# Authenticate and get credentials (unchanged)
def get_credentials():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return credentials

# Authenticate and build the YouTube API client (unchanged)
credentials = get_credentials()
youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

# Function to get live chat ID from a video ID (unchanged)
def get_live_chat_id(video_id):
    try:
        response = youtube.videos().list(
            part="liveStreamingDetails",
            id=video_id
        ).execute()

        if "items" in response and response["items"]:
            live_chat_id = response["items"][0].get("liveStreamingDetails", {}).get("activeLiveChatId")
            if live_chat_id:
                return live_chat_id
            else:
                raise Exception("No active live chat found for this video.")
        else:
            raise Exception("Video not found or does not have live chat.")
    except HttpError as e:
        print(f"Error while fetching live chat ID: {e}")
        raise

# Function to fetch live chat messages
def fetch_live_chat_messages(live_chat_id, next_page_token=None):
    response = youtube.liveChatMessages().list(
        liveChatId=live_chat_id,
        part="snippet(textMessageDetails),authorDetails(displayName)",  # Updated part parameter
        pageToken=next_page_token
    ).execute()

    return response.get("items", []), response.get("nextPageToken")

# Check for abuse in the chat messages
def detect_and_warn_abuse(live_chat_id, messages, start_time):
    global target_users  # Declare target_users as global
    processed_message_ids = set()  # Store IDs of processed messages to avoid duplicates
    for message in messages:
        message_id = message["id"]
        if message_id in processed_message_ids:
            continue  # Skip already processed messages
        processed_message_ids.add(message_id)

        # Parse message timestamp into offset-aware datetime
        message_time = datetime.fromisoformat(message["snippet"]["publishedAt"].replace("Z", "+00:00"))

        # Skip messages sent before the program started
        if message_time < start_time:
            continue

        text = message["snippet"]["textMessageDetails"]["messageText"]
        author_name = message["authorDetails"]["displayName"]

        # Check for target users and send special messages (Corrected Logic)
        for target_user in target_users:
            if target_user in author_name:  # Check if target_user is part of author_name
                special_message = target_users[target_user]
                if special_message:
                    post_message(live_chat_id, special_message)
                    print(f"Special message sent to {author_name}")
                break  # Exit the loop after finding a match

        # Check for abusive words
        if any(word in text.lower() for word in abusive_words):
            warning_message = f"@{author_name}, this is a bot. Please maintain respect in the chat!"
            post_message(live_chat_id, warning_message)
            print(f"Warning sent to {author_name} for abusive language: {text}")

# Function to post a message to live chat
def post_message(live_chat_id, message):
    try:
        request = youtube.liveChatMessages().insert(
            part="snippet",
            body={
                "snippet": {
                    "liveChatId": live_chat_id,
                    "type": "textMessageEvent",
                    "textMessageDetails": {
                        "messageText": message  # Corrected indentation
                    },
                }
            },
        )
        response = request.execute()

        # (Temporarily comment out the check to save quota)
        if "id" in response:
             print("Message posted:", message)
        else:
             print(f"Error: Message not posted: {response}")

        print("Message posted:", message)  # Print this regardless of success (for now)

    except HttpError as e:
        print(f"Failed to post message '{message}': {e}")

def main():
    global target_users
    video_id = "aPoMlkln8UQ"  # Replace with the actual video ID
    try:
        # Get the live chat ID

        live_chat_id = get_live_chat_id(video_id)
        print("Live Chat ID:", live_chat_id)

        next_page_token = None

        # Log the start time of the program (UTC and offset-aware)
        program_start_time = datetime.now(timezone.utc)
        print(f"Program started at: {program_start_time.isoformat()} UTC")


        target_users = load_target_users()
        while True:
            # Fetch live chat messages starting from `nextPageToken`


            if input():  # Check for any key press
                threading.Thread(target=reload_target_users_thread).start()  # Reload in a new thread

            messages, next_page_token = fetch_live_chat_messages(live_chat_id, next_page_token)

            # Detect and warn abusive messages, processing only new messages
            detect_and_warn_abuse(live_chat_id, messages, program_start_time)

            # Wait for a few seconds before fetching new messages (adjust as needed)
            time.sleep(10)


    except HttpError as e:
        if e.resp.status == 403 and "quotaExceeded" in str(e):  # Check for quota exceeded error
            print("Error:", e)
            print("Quota exceeded. Retrying in 100 seconds...")
            time.sleep(100)  # Wait for 60 seconds before retrying
        else:
            raise  # Re-raise other exceptions

if __name__ == "__main__":
    main()