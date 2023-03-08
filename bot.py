import asyncio
import logging
import sqlite3

import discord

from discord.ext import commands

from sqlite_update_subscribers import add_user

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix='!', intents=intents)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    client.loop.create_task(check_and_send_messages())


async def send_message_to_user(_client, message, user_id):
    user = await _client.fetch_user(user_id)
    await user.send(message)


@client.event
async def on_message(message):
    if str(message.channel) == 'test':
        username = message.content
        discord_id = message.author.id

        #REFACTOR THIS SHIT
        conn = sqlite3.connect('mydatabase.db')
        add_user(discord_id, username)

        conn.commit()
        conn.close()
        if message:
            await message.delete()


async def check_and_send_messages():
    while True:
        conn = sqlite3.connect('raid_events.db')
        c = conn.cursor()

        c.execute("SELECT timestamp, user, object, owner, success, attempts, lock_type, alert_sent FROM events_table WHERE alert_sent=0")
        alerts = c.fetchall()

        if len(alerts) == 0:
            print("No alerts to send.")
            return

        for alert in alerts:
            timestamp, user, obj, owner, success, attempts, lock_type, alert_sent = alert
            c.execute("SELECT COUNT(*) FROM subscribers WHERE username=?", (owner,))
            owner_exists = c.fetchone()[0]

            if owner_exists and alert_sent == 0:
                try:
                    c.execute("UPDATE events_table SET alert_sent=1 WHERE timestamp=?", (timestamp,))
                    conn.commit()
                except Exception as e:
                    logging.error(f"Failed to update alert_sent for timestamp {timestamp}: {str(e)}")
                    continue
                c.execute("SELECT user_id FROM subscribers WHERE username=?", (owner,))
                user_id = c.fetchone()[0]
                #
                # print(f"Alert for user {user_id}:")
                # print(f"Timestamp: {timestamp}")
                # print(f"Object: {obj}")
                # print(f"Owner: {owner}")
                # print(f"Lock Type: {lock_type}")
                if lock_type:
                    await send_message_to_user(client, f'Wake up {owner.capitalize()}! {user.capitalize()} is lockpicking your {obj}. He tried {attempts} times with{"" if success else " no"} success!', user_id)
                else:
                    await send_message_to_user(client,
                                               f'Wake up {owner.capitalize()}! {user.capitalize()} just triggered you {obj}!',
                                               user_id)
            # else:
            #     print(f"Owner {owner} is not subscribed.")

        conn.commit()
        conn.close()

        await asyncio.sleep(1)

client.run('MTA4MTYwMjczNjEwMzExMjc2NQ.GogHH9.2d8fxywJ--sLtcxY5CGrbk4r3uQeJJmnUcM8g0')
