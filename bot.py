import os
import discord
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
# from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL

load_dotenv()


OWNER_ID = int(os.getenv("OWNER_ID"))

# Spotify setup
sp = Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

# Discord setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def get_song_query(spotify_url):
    try:
        track = sp.track(spotify_url)
        title = track['name']
        artist = track['artists'][0]['name']
        return f"{title} {artist}"
    except Exception as e:
        print(f"Error getting Spotify track info: {e}")
        return None

# def search_youtube(query):
#     try:
#         search = VideosSearch(query, limit=1)
#         return search.result()['result'][0]['link']
#     except Exception as e:
#         print(f"Error searching YouTube: {e}")
#         return None


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
    print(f'Bot logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.id == OWNER_ID and message.content == "!shutdown":
        await message.channel.send("Ok Boss. See ya next time.")
        await client.close()

    if 'open.spotify.com/track' in message.content:
        spotify_url = message.content.strip().split()[0]  # grab the URL
        query = get_song_query(spotify_url)
        if query:
            youtube_link = search_youtube(query)
            if youtube_link:
                await message.channel.send(youtube_link)
            else:
                await message.channel.send("Couldn't find the song on YouTube.")
        else:
            await message.channel.send("Failed to get song info from Spotify.")

client.run(os.getenv("DISCORD_BOT_TOKEN"))
