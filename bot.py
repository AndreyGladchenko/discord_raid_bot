import asyncio
import logging
import os
import sqlite3

import discord

from discord.ext import commands

from sqlite_update_subscribers import add_user
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix='!', intents=intents)

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    client.loop.create_task(check_and_send_messages())


async def send_message_to_user(_client, message, user_id):
    user = await _client.fetch_user(user_id)
    await user.send(message)


@client.event
async def on_message(message):
    if str(message.channel) == 'raid-alerts':
        username = message.content
        discord_id = message.author.id

        #REFACTOR THIS SHIT
        conn = sqlite3.connect('raid_events.db')
        add_user(discord_id, username)

        conn.commit()
        conn.close()
        if message:
            await message.delete()


async def check_and_send_messages():
    while True:
        conn = sqlite3.connect('raid_events.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM events_table WHERE alert_sent = false")
        events = cur.fetchall()

        if events:
            for event in events:
                timestamp, user, owner, success, attempts, obj, lock_type, alert_sent = event

                cur.execute("SELECT COUNT(*) FROM subscribers WHERE username=?", (owner,))
                owner_exists = cur.fetchone()[0]

                if alert_sent == 1:
                    continue

                if owner_exists:
                    try:
                        cur.execute("UPDATE events_table SET alert_sent = 1 WHERE timestamp = ?", (timestamp,))
                        conn.commit()
                    except Exception as e:
                        logging.error(f"Failed to update alert_sent for timestamp {timestamp}: {str(e)}")
                        continue

                    cur.execute("SELECT user_id FROM subscribers WHERE username=?", (owner,))
                    user_id = cur.fetchone()[0]

                    if lock_type:
                        await send_message_to_user(client,
                            f'Wake up {owner.capitalize()}! {user.capitalize()} is lockpicking your {obj}. He tried {attempts} times with{"" if success == "Yes" else " no"} success!',
                            user_id)
                    else:
                        await send_message_to_user(client,
                            f'Wake up {owner.capitalize()}! {user.capitalize()} just triggered your {obj}!',
                            user_id)

            conn.commit()
            conn.close()

        await asyncio.sleep(5)

client.run(DISCORD_TOKEN)
