import discord
from discord.ext import commands, tasks
import os
from rss import *
from datetime import timezone, datetime
import asyncio
import logging

def main(): 

    TOKEN = os.getenv("DISCORD_TOKEN")

    intents = discord.Intents.all()
    # intents.messages = True
    # intents.guilds = True
    # intents.reactions = True
    bot = commands.Bot(command_prefix='_', intents=intents, help_command=None)
 
    @bot.event
    async def on_ready():
        print(f'We have logged in as {bot.user}')

    @bot.command(name='startrss')
    async def start_feeds(ctx):
        current_time = datetime.now().strftime("%H:%M:%S")
        await ctx.send(f"[{current_time}] - Bot is answering")

    bot.run(TOKEN, log_level=logging.DEBUG)

if __name__ == "__main__":
    main()
