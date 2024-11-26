import json
import re
import time
from datetime import datetime, timezone
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery
import threading

# Global variable to hold target users
target_users = {}

def load_target_users(filename="target_users.json"):
    """Loads the target users and their messages from a JSON file."""
    try:
        with open(filename, "r") as f:
            loaded_users = json.load(f)
            # Normalize usernames using regex
            normalized_users = {normalize_username(k): v for k, v in loaded_users.items()}
            print("Target users reloaded:", normalized_users)
            return normalized_users
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{filename}'.")
        return {}

def normalize_username(username):
    """Normalize usernames by removing non-alphanumeric characters and converting to lowercase."""
    return re.sub(r'\W+', '', username.strip().lower())

def reload_target_users_thread():
    """Reloads the target users in a separate thread."""
    global target_users
    while True:
        target_users = load_target_users()
        time.sleep(300)  # Reload every 5 minutes

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
CLIENT_SECRET_FILE = "credential.json"

abusive_words = ["abuse1", "abuse2", "offensiveWord"]

def get_credentials():
    """Authenticate and get credentials."""
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return credentials

credentials = get_credentials()
youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def get_live_chat_id(video_id):
    """Get live chat ID from a video ID."""
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

def fetch_live_chat_messages(live_chat_id, next_page_token=None):
    """Fetch live chat messages."""
    response = youtube.liveChatMessages().list(
        liveChatId=live_chat_id,
        part="snippet,authorDetails",
        pageToken=next_page_token
    ).execute()
    return response.get("items", []), response.get("nextPageToken")

def detect_and_highlight_target_users(live_chat_id, messages, start_time):
    """Highlight messages from target users."""
    global target_users
    for message in messages:
        if "snippet" in message:
            message_time = datetime.fromisoformat(message["snippet"]["publishedAt"].replace("Z", "+00:00"))
            if message_time < start_time:
                continue

        raw_author_name = message["authorDetails"]["displayName"]
        normalized_author_name = normalize_username(raw_author_name)

        # Check if user is a target user
        if normalized_author_name in target_users:
            # Print the target user's message and our response
            target_message = message["snippet"]["textMessageDetails"]["messageText"]
            print(f"Target User Message: {raw_author_name}: '{target_message}'")

            highlighted_message = f"Highlight: {raw_author_name} said: '{target_message}'"
            print(f"Our Response: {highlighted_message}")
            post_message(live_chat_id, highlighted_message)

            # Check for abusive messages (only if message content was available)
            if "snippet" in message and "textMessageDetails" in message["snippet"]:
                text = message["snippet"]["textMessageDetails"]["messageText"]
                if any(word in text.lower() for word in abusive_words):
                    warning_message = f"@{raw_author_name}, this is a bot. Please maintain respect in the chat!"
                    post_message(live_chat_id, warning_message)

def post_message(live_chat_id, message):
    """Post a message to live chat."""
    print(f"Attempting to post message: {message}")
    try:
        request = youtube.liveChatMessages().insert(
            part="snippet",
            body={
                "snippet": {
                    "liveChatId": live_chat_id,
                    "type": "textMessageEvent",
                    "textMessageDetails": {
                        "messageText": message
                    },
                }
            },
        )
        response = request.execute()

        if "id" in response:
            print(f"Message posted successfully: {message}")
        else:
            print(f"Error: Message not posted: {response}")
            print(f"Full response: {response}")

    except HttpError as e:
        print(f"Failed to post message '{message}': {e}")
        print(f"Response Content: {e.content}")
        error_details = json.loads(e.content.decode('utf-8')) if e.content else {}
        print(f"Error Details: {error_details}")

        if "error" in error_details:
            error_code = error_details["error"].get("code")
            error_message = error_details["error"].get("message")
            print(f"Error Code: {error_code}, Error Message: {error_message}")
        else:
            print("Unexpected error structure.")

def main():
    global target_users
    video_id = "O6ppgl9tFvk"
    try:
        live_chat_id = get_live_chat_id(video_id)
        print("Live Chat ID:", live_chat_id)

        next_page_token = None
        program_start_time = datetime.now(timezone.utc)
        print(f"Program started at: {program_start_time.isoformat()} UTC")

        target_users = load_target_users()
        threading.Thread(target=reload_target_users_thread).start()

        while True:
            messages, next_page_token = fetch_live_chat_messages(live_chat_id, next_page_token)
            detect_and_highlight_target_users(live_chat_id, messages, program_start_time)
            time.sleep(15)  # Adjusted to 15 seconds

    except HttpError as e:
        if e.resp.status == 403 and "quotaExceeded" in str(e):
            print("Error:", e)
            print("Quota exceeded. Retrying in 100 seconds...")
            time.sleep(100)
        else:
            raise

if __name__ == "__main__":
    main()



