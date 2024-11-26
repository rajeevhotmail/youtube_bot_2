from datetime import datetime, timezone
import time
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery

# Set the scopes required for accessing the YouTube API
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Load the OAuth 2.0 client credentials file
CLIENT_SECRET_FILE = "credential.json"

# Initialize the last sent index
last_sent_index = -1  # Start with -1 (no message sent)

# List of strings to send
strs = [
    "Dhoondho-dhoondho re saajana, dhoondho re saajana\nMore balam ka gola\nHo, dhoondho-dhoondho re saajana, dhoondho re saajana\nMore balam ka gola",
    "Mora gola chandaa ka jaise haalaa re\nMora gola chandaa ka jaise haalaa re\nJaamen laale-laale, haan\nJaamen laale-laale motiyan kee latake maala",
    "Main soi thi, apanee ataiya\nThagava ne daaka daalaa\nLut gayi nindiya, gir gayi bindiya\nchaddi se khul gaya gola, golam",
    "Mora gola chandaa ka jaise haalaa re\nJaamen laale-laale, haan\nJaamen laale-laale motiyan kee latake maala\nHo, dhoondho-dhoondho re saajana, dhoondho re saajana",
    "More balam ka gola\ngola mora baalepan ka\nHo gayi re jaa kee choree\nO, chaila tora manavaa mailaa",
    "Laagi najariyaa tori, golam\nMora gola chandaa ka jaise haalaa re\nJaamen laale-laale, haan\nJaamen laale-laale motiyan kee latake maala",
    "Ho, dhoondho-dhoondho re saajana, dhoondho re saajana\nMore balam ka gola\ngola mora sejiya pe gir gaya\nDhoondhe re more naina",
    "Naa jaanoon piya tune churaay liya\nDaiya re kal kee raina, golam\nMora gola chandaa ka jaise haalaa re\nJaamen laale-laale, haan",
    "Jaamen laale-laale motiyan kee latake maala\nHo, dhoondho-dhoondho re saajana, dhoondho re saajana\nMore balam ka gola"
]

# List of abusive words (extend this list as needed)
abusive_words = ["abuse1", "abuse2", "offensiveWord"]

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
        part="snippet,authorDetails",
        pageToken=next_page_token
    ).execute()

    return response.get("items", []), response.get("nextPageToken")

# Function to post a message to live chat
def post_message(live_chat_id, message):
    try:
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
        request.execute()
        print("Message posted:", message)
    except HttpError as e:
        print(f"Failed to post message '{message}': {e}")

# Check for abuse in the chat messages
def detect_and_warn_abuse(live_chat_id, messages, start_time):
    global last_sent_index  # Declare as global to modify the global variable
    for message in messages:
        # Parse message timestamp into offset-aware datetime
        message_time = datetime.fromisoformat(message["snippet"]["publishedAt"].replace("Z", "+00:00"))
        if message_time < start_time:
            continue  # Skip messages sent before the program started

        text = message["snippet"]["textMessageDetails"]["messageText"]
        author_name = message["authorDetails"]["displayName"]

        if any(name in author_name for name in ["lakshita", "Sonu Saini", "planet_earth", "JIJA", "Arvind"]):
            if "JIJA" in author_name:
                post_message(live_chat_id, "This is bot. Abe Majnoo @J tere gotiyan cut kardo kya?")
                print(f"Warning sent to {author_name} for message: {text}")
                continue

            last_sent_index += 1
            if last_sent_index >= len(strs):
                last_sent_index = 0  # Reset to 0 instead of -1

            warning_message = f"@{author_name}, this is bot. " + strs[last_sent_index]
            post_message(live_chat_id, warning_message)
            print(f"Warning sent to {author_name} for message: {text}")

        # Check for abusive words
        if any(word in text.lower() for word in abusive_words):
            warning_message = f"@{author_name}, this is a bot. Please maintain respect in the chat!"
            post_message(live_chat_id, warning_message)
            print(f"Warning sent to {author_name} for message: {text}")

def main():
    global last_sent_index  # Declare as global to modify the global variable
    video_id = "QC4AF7UkTTo"  # Replace with the actual video ID

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

            # Filter out already processed messages
            new_messages = [msg for msg in messages if msg["id"] not in processed_message_ids]
            for msg in new_messages:
                processed_message_ids.add(msg["id"])

            # Detect and warn abusive messages, but only process messages after program start
            detect_and_warn_abuse(live_chat_id, new_messages, program_start_time)

            # Wait for a few seconds before fetching new messages
            time.sleep(5)

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
