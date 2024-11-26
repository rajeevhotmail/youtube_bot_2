import random
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery

# Set the scopes required for accessing the YouTube API
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Load the OAuth 2.0 client credentials file
CLIENT_SECRET_FILE = "credential.json"  # Replace with the actual file name

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
    print("Message posted:", message)

# Specify the video ID of the live stream
video_id = "K5PaDWMsrps"  # Replace with the actual video ID

# Pool of messages
message_pool = [

    "anonymous, do kodi ka troll hai",
    "usske mutlab hai anonymous ki history naheen hai",
    "na atta ",
    "na patta?",


]

# Main loop
try:
    # Get the live chat ID
    live_chat_id = get_live_chat_id(video_id)
    print("Live Chat ID:", live_chat_id)

    while True:
        # Pick a random message from the pool
        message = random.choice(message_pool)

        # Post the message
        post_message(live_chat_id, message)

        # Wait for a random time between 30 to 60 seconds
        #time.sleep(random.randint(30, 60))
        time.sleep(1)


except Exception as e:
    print("Error:", e)
