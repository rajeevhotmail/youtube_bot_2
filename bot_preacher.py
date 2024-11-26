import openai
import time
from datetime import datetime, timezone
from googletrans import Translator
import emoji
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery

# Set your OpenAI API key
openai.api_key = "your-openai-api-key"

# Google API Setup
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
CLIENT_SECRET_FILE = "credential.json"

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

def post_message(live_chat_id, message):
    """Post a message to live chat."""
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
    except HttpError as e:
        print(f"Failed to post message '{message}': {e}")

# Input Preprocessing
translator = Translator()

def preprocess_message(content):
    """Preprocess troll message to normalize and translate it."""
    # Remove emojis and replace with descriptive text
    content = emoji.demojize(content, delimiters=("", " "))

    # Detect language
    lang_detected = translator.detect(content).lang
    print(f"Detected language: {lang_detected}")

    # Translate to English if not already English
    if lang_detected != "en":
        content = translator.translate(content, src=lang_detected, dest="en").text
        print(f"Translated content: {content}")

    return content

# Generate Dynamic Responses
def generate_dynamic_response(content):
    """Generate a response based on processed input."""
    content = preprocess_message(content)  # Normalize input

    prompt = f"The user wrote: '{content}'. Write a witty, kind, and thoughtful 4-line response."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a kind assistant that writes inclusive and clever responses."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error generating response: {e}")
        return None

# Fetch and Respond to Live Chat Messages
def fetch_live_chat_messages(live_chat_id, next_page_token=None):
    """Fetch live chat messages."""
    try:
        response = youtube.liveChatMessages().list(
            liveChatId=live_chat_id,
            part="snippet",
            pageToken=next_page_token
        ).execute()
        return response.get("items", []), response.get("nextPageToken")
    except HttpError as e:
        print(f"Error fetching live chat messages: {e}")
        return [], None

def listen_and_respond(live_chat_id):
    """Listen to live chat and respond dynamically."""
    next_page_token = None
    processed_messages = set()  # Keep track of processed messages to avoid duplicates
    bot_start_time = datetime.now(timezone.utc)  # Record bot start time in UTC

    while True:
        messages, next_page_token = fetch_live_chat_messages(live_chat_id, next_page_token)
        for message in messages:
            content = message["snippet"].get("textMessageDetails", {}).get("messageText", "")
            timestamp = message["snippet"]["publishedAt"]
            message_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

            # Skip messages posted before the bot started
            if message_time < bot_start_time:
                continue

            # Skip empty or already processed messages
            if not content or content in processed_messages:
                continue

            print(f"New message: {content}")
            response = generate_dynamic_response(content)
            if response:
                post_message(live_chat_id, response)
                processed_messages.add(content)  # Mark message as processed

        time.sleep(10)  # Wait before fetching new messages

# Main Entry Point
if __name__ == "__main__":
    video_id = "LgoJHYsNB2w"  # Replace with your video ID
    try:
        live_chat_id = get_live_chat_id(video_id)  # Fetch live chat ID
        print(f"Live Chat ID: {live_chat_id}")
        listen_and_respond(live_chat_id)  # Start listening and responding
    except Exception as e:
        print(f"Error: {e}")
