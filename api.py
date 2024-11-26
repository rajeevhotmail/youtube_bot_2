import googleapiclient.discovery
import sys
import re
import time

# Replace with your API key


# Build the YouTube API client
youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)

def get_live_chat_id(video_url):
    try:
        # Extract the video ID from the URL
        match = re.search(r"v=([^&]+)", video_url)
        if not match:
            raise ValueError("Invalid YouTube URL. Make sure it contains a video ID.")
        video_id = match.group(1)

        # Fetch the liveChatId using the YouTube API
        request = youtube.videos().list(
            part='snippet,liveStreamingDetails',
            id=video_id
        )
        response = request.execute()

        live_chat_id = response['items'][0]['liveStreamingDetails']['activeLiveChatId']
        return live_chat_id
    except IndexError:
        print("Could not find live chat for the given video. Is it live?")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def post_message(live_chat_id, message):
    try:
        # Make the API request to post a message
        youtube.liveChatMessages().insert(
            part="snippet",
            body={
                "snippet": {
                    "liveChatId": live_chat_id,
                    "type": "textMessageEvent",
                    "textMessageDetails": {
                        "messageText": message
                    }
                }
            }
        ).execute()
        print(f"Posted message: {message}")
    except Exception as e:
        print(f"Failed to post message: {message}. Error: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <YouTube Live URL>")
        sys.exit(1)

    video_url = sys.argv[1]

    # Fetch liveChatId from the video URL
    live_chat_id = get_live_chat_id(video_url)
    print(f"Live Chat ID: {live_chat_id}")

    # List of messages to post
    messages = [
        "Hello everyone!",
        "Hope you're enjoying the stream!",
        "Don't forget to like and subscribe!",
        "Feel free to ask any questions.",
        "Thanks for being here!"
    ]

    # Post messages in a loop
    try:
        while True:
            for message in messages:
                post_message(live_chat_id, message)
                time.sleep(30)  # Wait 30 seconds before posting the next message
    except KeyboardInterrupt:
        print("Stopped posting messages.")

if __name__ == "__main__":
    main()
