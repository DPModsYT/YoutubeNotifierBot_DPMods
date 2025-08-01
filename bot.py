import requests
import os
from dotenv import load_dotenv

# Load from .env
load_dotenv()

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
CHANNEL_ID = os.getenv('CHANNEL_ID')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
LAST_VIDEO_FILE = 'last_video.txt'


def get_latest_video():
    url = (
        f'https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}'
        f'&channelId={CHANNEL_ID}&part=snippet,id&order=date&maxResults=1'
    )
    response = requests.get(url)
    data = response.json()

    if 'items' not in data or not data['items']:
        print("No video found.")
        return None, None

    item = data['items'][0]
    if item['id']['kind'] != "youtube#video":
        return None, None

    video_id = item['id']['videoId']
    title = item['snippet']['title']
    return video_id, title


def read_last_video_id():
    if not os.path.exists(LAST_VIDEO_FILE):
        return None
    with open(LAST_VIDEO_FILE, 'r') as f:
        return f.read().strip()


def save_last_video_id(video_id):
    with open(LAST_VIDEO_FILE, 'w') as f:
        f.write(video_id)


def send_to_telegram(video_id, title):
    video_url = f"https://youtu.be/{video_id}"
    message = f"📢 <b>New Video Uploaded</b>\n\n🎬 <b>{title}</b>\n\n🔗 {video_url}"

    send_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHANNEL_ID,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': False
    }

    response = requests.post(send_url, data=payload)
    data = response.json()

    if response.status_code == 200 and 'result' in data:
        message_id = data['result']['message_id']
        # Pin the message
        pin_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/pinChatMessage"
        pin_payload = {
            'chat_id': TELEGRAM_CHANNEL_ID,
            'message_id': message_id,
            'disable_notification': True
        }
        pin_response = requests.post(pin_url, data=pin_payload)
        print("Pinned:", pin_response.json())
    else:
        print("Telegram send failed:", data)


def main():
    video_id, title = get_latest_video()
    if not video_id:
        print("No new video found.")
        return

    last_video_id = read_last_video_id()
    if video_id != last_video_id:
        print("New video detected. Sending to Telegram...")
        send_to_telegram(video_id, title)
        save_last_video_id(video_id)
    else:
        print("Already posted this video.")


if __name__ == "__main__":
    main()
