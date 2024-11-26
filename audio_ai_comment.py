import openai
import time
import datetime
import speech_recognition as sr
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery
import os

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

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

# Audio Transcription
def transcribe_audio():
    """Capture audio and transcribe it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening to the anchor...")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language="en-US")
            print(f"Anchor said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, could not understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"Error with speech recognition: {e}")
            return None

# Generate Witty Comments
def generate_witty_comment(transcription):
    """Generate a witty comment based on the anchor's speech."""
    if not transcription:
        return None  # If transcription failed, skip generating a comment

    prompt = f"""You are a witty assistant. The anchor said: "{transcription}".
    Respond with a humorous or clever comment suitable for a live chat."""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Replace with "gpt-4" if desired
            messages=[
                {"role": "system", "content": "You are a witty assistant for live chat."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
        )
        comment = response["choices"][0]["message"]["content"].strip()
        print(f"Witty comment: {comment}")
        return comment
    except Exception as e:
        print(f"Error generating witty comment: {e}")
        return None

# Main Listening and Posting Loop
def listen_and_comment(live_chat_id):
    """Continuously listen to the anchor and post witty comments."""
    api_call_count = 0
    API_LIMIT = 300  # Set a daily limit for API calls (adjust based on quota)
    start_time = datetime.datetime.utcnow()  # Track when the bot started

    while api_call_count < API_LIMIT:
        transcription = transcribe_audio()
        if transcription:
            # Generate and post witty comment
            witty_comment = generate_witty_comment(transcription)
            if witty_comment:
                post_message(live_chat_id, witty_comment)
                api_call_count += 1  # Increment API call count

        # Log the bot's running time
        current_time = datetime.datetime.utcnow()
        print(f"Bot running since: {start_time.isoformat()}. Current time: {current_time.isoformat()}")
        time.sleep(120)  # Wait 5 minutes before the next iteration

    print("Daily API limit reached. Stopping bot.")

# Main Entry Point
if __name__ == "__main__":
    video_id = "IroXq9mZ5Zw"  # Replace with your video ID
    try:
        live_chat_id = get_live_chat_id(video_id)  # Fetch live chat ID
        print(f"Live Chat ID: {live_chat_id}")
        listen_and_comment(live_chat_id)  # Start listening and posting comments
    except Exception as e:
        print(f"Error: {e}")
