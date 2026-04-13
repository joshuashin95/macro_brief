"""
bot/discord_bot.py

Sends the macro briefing to a Discord channel.
"""

import discord
import asyncio
from utils.config import DISCORD_BOT_TOKEN


async def post_briefing(channel_id: int, message: str):
    """Send a message to a Discord channel and disconnect."""

    class BriefingClient(discord.Client):
        async def on_ready(self):
            print(f"Logged in as {self.user}")
            channel = self.get_channel(channel_id) or await self.fetch_channel(channel_id)

            # Discord has a 2000 char limit — split if needed
            chunks = [message[i:i+1990] for i in range(0, len(message), 1990)]
            for chunk in chunks:
                await channel.send(chunk)

            print("Message sent.")
            await self.close()

    client = BriefingClient(intents=discord.Intents.default())
    await client.start(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(post_briefing(
        channel_id=int(__import__("utils.config", fromlist=["DISCORD_CHANNEL_ID"]).DISCORD_CHANNEL_ID),
        message="**test** — bot is working!"
    ))
