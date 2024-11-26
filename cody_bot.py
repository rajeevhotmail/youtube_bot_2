import json
import time
from datetime import datetime, timezone
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery
import threading

def load_target_users(filename="target_users.json"):
    try:
        with open(filename, "r") as f:
            target_users = json.load(f)
        print("Target users reloaded:", target_users)
        return target_users
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{filename}'.")
        return {}

def reload_target_users_thread():
    global target_users
    target_users = load_target_users()

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
CLIENT_SECRET_FILE = "credential.json"

strs = [
    "Dhoondho-dhoondho re saajana, dhoondho re saajana\nMore balam ka gola\nHo, dhoondho-dhoondho re saajana, dhoondho re saajana\nMore balam ka gola",
]

abusive_words = ["abuse1", "abuse2", "offensiveWord"]

def get_credentials():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return credentials

credentials = get_credentials()
youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

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

def fetch_live_chat_messages(live_chat_id, next_page_token=None):
    response = youtube.liveChatMessages().list(
        liveChatId=live_chat_id,
        part="snippet(textMessageDetails),authorDetails(displayName)",
        pageToken=next_page_token
    ).execute()
    return response.get("items", []), response.get("nextPageToken")

def detect_and_warn_abuse(live_chat_id, messages, start_time):
    global target_users
    processed_message_ids = set()

    for message in messages:
        message_id = message["id"]
        if message_id in processed_message_ids:
            continue

        processed_message_ids.add(message_id)

        message_time = datetime.fromisoformat(message["snippet"]["publishedAt"].replace("Z", "+00:00"))

        if message_time < start_time:
            print(f"Skipping message from {message['authorDetails']['displayName']} - sent before bot start")
            continue

        text = message["snippet"]["textMessageDetails"]["messageText"]
        author_name = message["authorDetails"]["displayName"]

        print(f"Processing message from {author_name} at {message_time}")

        for target_user in target_users:
            if target_user in author_name:
                special_message = target_users[target_user]
                if special_message:
                    post_message(live_chat_id, special_message)
                    print(f"Special message sent to {author_name}")
                break

        if any(word in text.lower() for word in abusive_words):
            warning_message = f"@{author_name}, this is a bot. Please maintain respect in the chat!"
            post_message(live_chat_id, warning_message)
            print(f"Warning sent to {author_name} for abusive language: {text}")

def post_message(live_chat_id, message):
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
            }
        )
        response = request.execute()
        print("Message posted:", message)
    except HttpError as e:
        print(f"Failed to post message '{message}': {e}")

def main():
    global target_users
    video_id = "5kuOkEI3cb4"  # Replace with the actual video ID

    try:
        live_chat_id = get_live_chat_id(video_id)
        print("Live Chat ID:", live_chat_id)

        next_page_token = None
        program_start_time = datetime.now(timezone.utc)
        print(f"Program started at: {program_start_time.isoformat()} UTC")

        target_users = load_target_users()

        while True:
            if input():
                threading.Thread(target=reload_target_users_thread).start()

            messages, next_page_token = fetch_live_chat_messages(live_chat_id, next_page_token)
            detect_and_warn_abuse(live_chat_id, messages, program_start_time)
            time.sleep(10)

    except HttpError as e:
        if e.resp.status == 403 and "quotaExceeded" in str(e):
            print("Error:", e)
            print("Quota exceeded. Retrying in 100 seconds...")
            time.sleep(100)
        else:
            raise

if __name__ == "__main__":
    main()
