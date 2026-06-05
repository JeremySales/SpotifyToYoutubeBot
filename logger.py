import sqlite3
import os
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", "bot_logs.db")


def _conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS message_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                channel_id INTEGER NOT NULL,
                channel_name TEXT NOT NULL,
                message_id INTEGER NOT NULL,
                content_length INTEGER,
                word_count INTEGER,
                has_attachments INTEGER,
                is_command INTEGER,
                rate_limited INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS spotify_conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                spotify_url TEXT,
                track_name TEXT,
                artist TEXT,
                youtube_url TEXT,
                success INTEGER NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS twitter_conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                original_url TEXT NOT NULL,
                converted_url TEXT NOT NULL
            )
        """)


def log_message(message, rate_limited=False):
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO message_logs
                (timestamp, user_id, username, channel_id, channel_name,
                 message_id, content_length, word_count, has_attachments, is_command, rate_limited)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(),
                message.author.id,
                str(message.author),
                message.channel.id,
                str(message.channel),
                message.id,
                len(message.content),
                len(message.content.split()),
                int(len(message.attachments) > 0),
                int(message.content.startswith("!")),
                int(rate_limited),
            ),
        )


def log_twitter_conversion(message, original_url, converted_url):
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO twitter_conversions
                (timestamp, user_id, username, original_url, converted_url)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(),
                message.author.id,
                str(message.author),
                original_url,
                converted_url,
            ),
        )


def log_conversion(message, spotify_url, track_name, artist, youtube_url, success):
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO spotify_conversions
                (timestamp, user_id, username, spotify_url, track_name, artist, youtube_url, success)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(),
                message.author.id,
                str(message.author),
                spotify_url,
                track_name,
                artist,
                youtube_url,
                int(success),
            ),
        )
