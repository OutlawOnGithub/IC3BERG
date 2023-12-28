import discord
from discord.ext import commands, tasks
import os
import logging

def main(): 

    TOKEN = os.getenv("DISCORD_TOKEN")

    intents = discord.Intents(messages=True, message_content = True)    # intents.guilds = True

    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        print(f'We have logged in as {bot.user}')

    @bot.command(name='hi')
    async def say_hi(ctx):
        await ctx.send(f"Hi !")

    bot.run(TOKEN, log_level=logging.DEBUG)

if __name__ == "__main__":
    main()
