from datetime import datetime, timezone
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery

# Set the scopes required for accessing the YouTube API
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Load the OAuth 2.0 client credentials file
CLIENT_SECRET_FILE = "credential.json"

# Authenticate and get credentials
def get_credentials():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return credentials

# Authenticate and build the YouTube API client
credentials = get_credentials()
youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

# Function to get live chat ID from a video ID
def get_live_chat_id(video_id):
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

# Function to fetch live chat messages
def fetch_live_chat_messages(live_chat_id, next_page_token=None):
    response = youtube.liveChatMessages().list(
        liveChatId=live_chat_id,
        part="snippet,authorDetails",
        pageToken=next_page_token
    ).execute()

    return response.get("items", []), response.get("nextPageToken")

# Function to post a message to live chat
def post_message(live_chat_id, message):
    request = youtube.liveChatMessages().insert(
        part="snippet",
        body={
            "snippet": {
                "liveChatId": live_chat_id,
                "type": "textMessageEvent",
                "textMessageDetails": {"messageText": message},
            }
        },
    )
    response = request.execute()
    print("the response: ", response)
    print("Message posted:", message)

# List of abusive words (extend this list as needed)
abusive_words = ["abuse1", "abuse2", "offensiveWord"]

# Check for abuse in the chat messages
def detect_and_warn_abuse(live_chat_id, messages, start_time):
    for message in messages:
        # Parse message timestamp into offset-aware datetime
        message_time = datetime.fromisoformat(message["snippet"]["publishedAt"].replace("Z", "+00:00"))
        if message_time < start_time:
            continue  # Skip messages sent before the program started

        text = message["snippet"]["textMessageDetails"]["messageText"]
        author_name = message["authorDetails"]["displayName"]

        if "lakshita" in author_name or "Sonu Saini" in author_name or "Arvind" in author_name or "JIJA" in author_name:
            if "JIJA" in author_name:
                post_message(live_chat_id, "This is bot. Abe Majnoo @J tere gotiyan cut kardo kya?")
                print(f"Warning sent to {author_name} for message: {text}")
                continue
            warning_message = f"@{author_name}, this is bot. I will kick you."

            post_message(live_chat_id, warning_message)
            print(f"Warning sent to {author_name} for message: {text}")
        # Check for abusive words
        if any(word in text.lower() for word in abusive_words):
            warning_message = f"@{author_name}, this is a bot. Please maintain respect in the chat!"
            post_message(live_chat_id, warning_message)
            print(f"Warning sent to {author_name} for message: {text}")

# Specify the video ID of the live stream
video_id = "DnisQqKfptE"  # Replace with the actual video ID

# Main loop
try:
    # Get the live chat ID
    live_chat_id = get_live_chat_id(video_id)
    print("Live Chat ID:", live_chat_id)

    next_page_token = None
    processed_message_ids = set()  # Store IDs of processed messages

    # Log the start time of the program (UTC and offset-aware)
    program_start_time = datetime.now(timezone.utc)
    print(f"Program started at: {program_start_time.isoformat()} UTC")

    while True:
        # Fetch live chat messages starting from `nextPageToken`
        messages, next_page_token = fetch_live_chat_messages(live_chat_id, next_page_token)

        # Filter out already processed messages1
        new_messages = [msg for msg in messages if msg["id"] not in processed_message_ids]
        for msg in new_messages:
            processed_message_ids.add(msg["id"])

        # Detect and warn abusive messages, but only process messages after program start
        detect_and_warn_abuse(live_chat_id, new_messages, program_start_time)

        # Wait for a few seconds before fetching new messages
        time.sleep(5)

except Exception as e:
    print("Error:", e)
