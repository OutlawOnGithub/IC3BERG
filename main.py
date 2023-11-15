import discord
from discord.ext import commands, tasks
import os
import json
from rss import *
def main():
    TOKEN = 'MTE3MzY4MzQwMzUzOTg4MjEwNg.GMUCfQ.qj-Dg5gQTSqZms90nS1NPWK1xBsIWHRxtMozgM'

    intents = discord.Intents.all()
    intents.messages = True
    intents.guilds = True
    intents.reactions = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    rss = RSS()

    feed_urls = ['http://www.bleepingcomputer.com/feed/']

    channel_name = 'infosec'
    previous_entry_id_per_server = {}
    fetching_status_per_server = {}

    @bot.event
    async def on_ready():
        print(f'We have logged in as {bot.user}')

    @tasks.loop(minutes = 5) # repeat after every 5 minutes
    async def fetch_feeds():
        feeds_list = ['https://krebsonsecurity.com/feed/','http://www.bleepingcomputer.com/feed/']
        for guild in bot.guilds:
            channel = discord.utils.get(guild.channels, name='infosec', type=discord.ChannelType.text)
            if channel:
                news_feed = feedparser.parse('http://www.bleepingcomputer.com/feed/')
                print(news_feed.entries[0])
                embed = rss.fetch_a_feed(news_feed)
                if embed:
                    await channel.send(embed=embed)
                else:
                    print('fetched already')

    @bot.command(name='startfeeds')
    async def start_feeds(ctx):
        guild_id = ctx.guild.id
        fetching_status_per_server[guild_id] = True
        fetch_feeds.start()
        print(f"Fetching started for server {ctx.guild.name}...")
        await ctx.send('RSS feed updates will now be fetched every 30 minutes.')

    @bot.command(name='stopfeeds')
    async def stop_feeds(ctx):
        guild_id = ctx.guild.id
        fetching_status_per_server[guild_id] = False
        print(f"Fetching stopped for server {ctx.guild.name}.")
        await ctx.send('RSS feed updates fetching has been stopped.')

    @bot.command(name='status')
    async def status(ctx):
        guild_id = ctx.guild.id
        status = fetching_status_per_server.get(guild_id, False)

        if status:
            await ctx.send(f'The bot is currently fetching RSS feed updates in {ctx.guild.name}.')
        else:
            await ctx.send(f'The bot is currently not fetching RSS feed updates in `{ctx.guild.name}`.')

    # keep_alive()
    bot.run(TOKEN)
    # try:
    #     bot.run(TOKEN)
    # except discord.errors.HTTPException:
    #     print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
    #     os.system('kill 1')
    #     os.system("keep_alive.py")

if __name__ == "__main__":
    main()
