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
    intents.messages = True
    intents.guilds = True
    intents.reactions = True
    bot = commands.Bot(command_prefix='_', intents=intents, help_command=None)

    feed_dict = {
        'https://krebsonsecurity.com/feed/' : '',
        'http://www.bleepingcomputer.com/feed/' : '',
    }

    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

    channel_name = 'infosec'
    fetching_status_per_server = {}

    @bot.event
    async def on_ready():
        print(f'We have logged in as {bot.user}')

    @tasks.loop(minutes = 5) # repeat after every 5 minutes
    async def fetch_feeds():
        #print(feed_dict)
        print(f"I am fetching !")
        for feed_url in feed_dict.keys():

            news_feed = feedparser.parse(feed_url)
            if feed_dict[feed_url] != news_feed.entries[0]['id']: #test si c'est nouveau 
                embed = discord.Embed(
                    title=news_feed.entries[0]['title'],
                    url=news_feed.entries[0]['link'],
                    description=news_feed.entries[0]['description'],
                    color=discord.Color.blue()
                )
                # if 'img' in news_feed.entries[0]:
                #     embed.set_image(url=news_feed.entries[0]['img']['url'])
                embed.set_author(name=news_feed.entries[0]['author'])
                current_time_gmt = datetime.now(timezone.utc)
                formatted_time = current_time_gmt.strftime("%H:%M:%S %d/%m/%Y %Z")
                embed.set_footer(text=f"{formatted_time}")
                
                for guild in bot.guilds:
                    channel = discord.utils.get(guild.channels, name=channel_name, type=discord.ChannelType.text)
                    if channel:
                        await channel.send(embed=embed)
                    else:
                        print('fetched already')
            feed_dict[feed_url] = news_feed.entries[0]['id']


    @bot.command(name='startrss')
    async def start_feeds(ctx):
        guild_id = ctx.guild.id
        fetching_status_per_server[guild_id] = True
        if not fetch_feeds.is_running():
            #fetch_feeds.start()
            #print(f"Fetching started for all servers")#server {ctx.guild.name}...")
            #await ctx.send('RSS feed updates will now be fetched every 5 minutes.')
            print(f"Fetching - Started - {ctx.guild}")
            await ctx.send('RSS feeds are disabled until we fix the lag issue')
        else:
            await ctx.send('RSS feed updates are already being fetched.')


    @bot.command(name='stoprss')
    async def stop_feeds(ctx):
        guild_id = ctx.guild.id
        if fetch_feeds.is_running():
            fetching_status_per_server[guild_id] = False
            print(f"Fetching - Stopped - {ctx.guild}")
            fetch_feeds.cancel()
            #await ctx.send('RSS feed updates fetching has been stopped.')
            await ctx.send('RSS feeds are disabled until we fix the lag issue')
        else:
            fetch_feeds.cancel()
            await ctx.send('The bot is not currently fetching.')


    @bot.command(name='addrss')
    async def add_feed(ctx, feed_url=''):
        if feed_url:
            print(f"Added feed : {feed_url}")
            feed_dict[feed_url] = ''
            print(f"AddRSS - Success - {feed_url} - {ctx.guild}")
            await ctx.send(f'You successfully added the RSS feed : `{feed_url}`')
        else:
            print(f"AddRSS - Fail - {ctx.guild}")
            await ctx.send(f'A feed url is required')
      

    @bot.command(name='status')
    async def status(ctx):
        #guild_id = ctx.guild.id
        if fetch_feeds.is_running():
            print(f"Status - Fetching - {ctx.guild}")
            await ctx.send(f'The bot is currently fetching RSS feed updates in all servers.')
        else:
            print(f"Status - Not fetching - {ctx.guild}")
            await ctx.send(f'The bot is not fetching RSS feed updates in all servers.')


    @bot.command(name='help')
    async def help(ctx):
        embed = discord.Embed(
                    title="Command list",
                    #url="https://github.com/OutlawOnGithub",
                    color=discord.Color.blue()
                )
        embed.add_field(name='_startrss', value='Starts fetching the saved RSS flux', inline=False)
        embed.add_field(name='_stoprss', value='Stops fetching and sending the news', inline=False)
        embed.add_field(name='_addrss <feed_url>', value='Adds a new RSS flux to fetch', inline=False)
        embed.add_field(name='_status', value='Displays if the bot is currently fetching the news or not', inline=False)
        embed.add_field(name='_info', value='Displays information about the makers of this bot', inline=False)
        embed.add_field(name='_help', value='Displays this help message', inline=False)
        embed.set_footer(text='For any requests, DM `ox6cfc1ab7`')

        print(f"Help - {ctx.guild}")
        await ctx.send(embed=embed)


    @bot.command(name='info')
    async def info(ctx):
        embed = discord.Embed(
                    title="Informations about IC3BERG",
                    url="https://github.com/OutlawOnGithub/IC3BERG/",
                    description="""This bot is a personal project by two IT students, Outlaw and Ayerman/Firzam.
                                   It is currently in development and will, in the future, include numerous functionalities related to cybersecurity.
                                   The project will be opensourced on Github once we deploy the v1.0.0""",
                    color=discord.Color.blue()
                )
        print(f"Info - {ctx.guild}")
        await ctx.send(embed=embed)


    bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
 
if __name__ == "__main__":
    main()
