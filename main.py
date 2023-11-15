import discord
from discord.ext import commands, tasks
import os
from rss import *
import asyncio
from dotenv import load_dotenv

def main():
    load_dotenv()
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

    @tasks.loop(seconds = 20) # repeat after every 5 minutes
    async def fetch_feeds():
        print(feed_dict)
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
            print(feed_dict)

    @bot.command(name='startfeeds')
    async def start_feeds(ctx):
        guild_id = ctx.guild.id
        fetching_status_per_server[guild_id] = True
        if fetch_feeds.is_running():
            print('alreasdy running')
            fetch_feeds.cancel()
            asyncio.sleep(3)
            fetch_feeds.start()
        else:

            fetch_feeds.start()
        print(f"Fetching started for all servers")#server {ctx.guild.name}...")
        await ctx.send('RSS feed updates will now be fetched every 5 minutes.')

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

    bot.run(TOKEN)

if __name__ == "__main__":
    main()
