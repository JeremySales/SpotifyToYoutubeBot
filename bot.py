import os
import re
import time
import discord
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from yt_dlp import YoutubeDL
from logger import init_db, log_message, log_conversion, log_twitter_conversion

load_dotenv()

OWNER_ID = int(os.getenv("OWNER_ID"))
RATE_LIMIT_SECONDS = 30

# Spotify setup
sp = Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

# Discord setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

_cooldowns: dict[int, float] = {}

TWITTER_PATTERN = re.compile(r'https?://(?:www\.)?(?:x|twitter)\.com/\S+')


def convert_twitter_url(url: str) -> str:
    return re.sub(r'(?:www\.)?(?:x|twitter)\.com', 'fxtwitter.com', url)


def is_rate_limited(user_id: int) -> bool:
    now = time.monotonic()
    if now - _cooldowns.get(user_id, 0) < RATE_LIMIT_SECONDS:
        return True
    _cooldowns[user_id] = now
    return False


def get_song_query(spotify_url):
    try:
        track = sp.track(spotify_url)
        title = track['name']
        artist = track['artists'][0]['name']
        return title, artist
    except Exception as e:
        print(f"Error getting Spotify track info: {e}")
        return None, None


def search_youtube(query):
    with YoutubeDL({'quiet': True}) as ydl:
        try:
            results = ydl.extract_info(f"ytsearch:{query}", download=False)['entries']
            if results:
                return f"https://www.youtube.com/watch?v={results[0]['id']}"
        except Exception as e:
            print(f"Error searching YouTube: {e}")
    return None


@client.event
async def on_ready():
    init_db()
    print(f'Bot logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.id == OWNER_ID and message.content == "!shutdown":
        await message.channel.send("Ok Boss. See ya next time.")
        await client.close()
        return

    has_spotify = 'open.spotify.com/track' in message.content
    twitter_match = TWITTER_PATTERN.search(message.content)

    if not has_spotify and not twitter_match:
        return

    if is_rate_limited(message.author.id):
        log_message(message, rate_limited=True)
        await message.reply(f"Slow down — one link every {RATE_LIMIT_SECONDS} seconds.")
        return

    log_message(message)

    if has_spotify:
        spotify_url = message.content.strip().split()[0]
        track_name, artist = get_song_query(spotify_url)
        if not track_name:
            log_conversion(message, spotify_url, None, None, None, success=False)
            await message.channel.send("Failed to get song info from Spotify.")
        else:
            youtube_url = search_youtube(f"{track_name} {artist}")
            if youtube_url:
                log_conversion(message, spotify_url, track_name, artist, youtube_url, success=True)
                await message.channel.send(youtube_url)
            else:
                log_conversion(message, spotify_url, track_name, artist, None, success=False)
                await message.channel.send("Couldn't find the song on YouTube.")

    if twitter_match:
        original_url = twitter_match.group(0)
        converted_url = convert_twitter_url(original_url)
        log_twitter_conversion(message, original_url, converted_url)
        await message.channel.send(converted_url)


client.run(os.getenv("DISCORD_BOT_TOKEN"))
