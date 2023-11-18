import discord
from discord.ext import commands, tasks
import os
from rss import *
import asyncio

def main(): 

    TOKEN = os.getenv("DISCORD_TOKEN")

    intents = discord.Intents.all()
    intents.messages = True
    intents.guilds = True
    intents.reactions = True
    bot = commands.Bot(command_prefix='_', intents=intents)

    rss = RSS()

    feed_dict = {
        'https://krebsonsecurity.com/feed/' : '',
        'http://www.bleepingcomputer.com/feed/' : '',
    }

    channel_name = 'infosec'
    fetching_status_per_server = {}

    @bot.event
    async def on_ready():
        print(f'We have logged in as {bot.user}')

    @tasks.loop(minutes = 5) # repeat after every 5 minutes
    async def fetch_feeds():
        #print(feed_dict)
        for feed_url in feed_dict.keys():

            news_feed = feedparser.parse(feed_url)
            if feed_dict[feed_url] != news_feed.entries[0]['id']: #test si c'est nouveau 
                embed = discord.Embed(
                    title=news_feed.entries[0]['title'],
                    url=news_feed.entries[0]['link'],
                    description=news_feed.entries[0]['summary'],
                    color=discord.Color.blue()
                )
                embed.set_author(name=news_feed.entries[0]['author'])
                embed.set_footer(text=f"{datetime.datetime.utcnow()}")
                
                for guild in bot.guilds:
                    channel = discord.utils.get(guild.channels, name=channel_name, type=discord.ChannelType.text)
                    if channel:
                        await channel.send(embed=embed)
                    else:
                        print('fetched already')
            feed_dict[feed_url] = news_feed.entries[0]['id']

    @bot.command(name='startfeeds')
    async def start_feeds(ctx):
        guild_id = ctx.guild.id
        fetching_status_per_server[guild_id] = True
        if not fetch_feeds.is_running():
            fetch_feeds.start()
            print(f"Fetching started for all servers")#server {ctx.guild.name}...")
            await ctx.send('RSS feed updates will now be fetched every 5 minutes.')
        else:
            await ctx.send('RSS feed updates are already being fetched.')

    @bot.command(name='stopfeeds')
    async def stop_feeds(ctx):
        guild_id = ctx.guild.id
        if fetch_feeds.is_running():
            fetching_status_per_server[guild_id] = False
            print(f"Fetching stopped for all servers.")
            fetch_feeds.cancel()
            await ctx.send('RSS feed updates fetching has been stopped.')
        else:
            fetch_feeds.cancel()
            await ctx.send('The bot is not currently fetching.')

    @bot.command(name='status')
    async def status(ctx):
        #guild_id = ctx.guild.id
        status = fetch_feeds.is_running()

        if status:
            print("Status : Fetching")
            await ctx.send(f'The bot is currently fetching RSS feed updates in all servers.')
        else:
            print("Status : Not fetching")
            await ctx.send(f'The bot is not fetching RSS feed updates in all servers.')

    bot.run(TOKEN)

if __name__ == "__main__":
    main()
