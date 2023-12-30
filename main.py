import discord
from discord.ext import commands, tasks
import os
import feedparser
from datetime import datetime, timezone
import asyncio
import logging
from utils.rss import *

def main(): 

    TOKEN = os.getenv("DISCORD_TOKEN")

    bot = commands.Bot(command_prefix='_', intents=discord.Intents.all(), activity=discord.Activity(type=discord.ActivityType.playing, name="_help"), help_command=None)

    channel_name = 'infosec'
    fetching_status_per_server = {}

    rss_instance = RSS()
 
    @bot.event
    async def on_ready():
        print(f'We have logged in as {bot.user}')

    @tasks.loop(minutes=20)
    async def fetch_feeds():
        for feed in rss_instance.feed_list:
            feed_url = feed['url']
            already_fetched = feed['already_fetched']

            if not already_fetched:
                news_feed = feedparser.parse(feed_url)

                if news_feed.entries:
                    embed = discord.Embed(
                        title=news_feed.entries[0]['title'],
                        url=news_feed.entries[0]['link'],
                        description=news_feed.entries[0]['description'].replace("<p>", "").replace("</p>", ""),
                        color=discord.Color.blue()
                    )
                    embed.set_author(name=news_feed.entries[0]['author'])
                    current_time_gmt = datetime.datetime.now(timezone.utc)
                    formatted_time = current_time_gmt.strftime("%H:%M:%S %d/%m/%Y %Z")
                    embed.set_footer(text=f"{formatted_time}")

                    for guild in bot.guilds:
                        channel = discord.utils.get(guild.channels, name=channel_name, type=discord.ChannelType.text)
                        if channel:
                            await channel.send(embed=embed)

                    # Update 'already_fetched' and other relevant fields in your feed dictionary
                    feed['already_fetched'] = True
                    # You might want to store additional information about the feed in the dictionary
                    # such as the last fetched entry ID, etc.

    @bot.group()
    async def rss(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(embed = rss_instance.default(ctx))

    @rss.command(name='start')
    async def rss_start(ctx):
        if rss_instance.feed_list:
            if not fetch_feeds.is_running():
                fetch_feeds.start()
                await ctx.send('RSS feed updates will now be fetched every 5 minutes.')
            else:
                await ctx.send('RSS feed updates are already being fetched.')
        else:
            await ctx.send('You must add a feed to fetch first ! Do `_rss add <feed_url>`')

    @rss.command(name='stop')
    async def rss_stop(ctx):
        if fetch_feeds.is_running():
            fetch_feeds.cancel()
            await ctx.send('RSS feed updates fetching has been stopped.')
        else:
            fetch_feeds.cancel()
            await ctx.send('The bot is not currently fetching.')

    @rss.command(name='status')
    async def rss_status(ctx):
        if fetch_feeds.is_running():
            await ctx.send(f'The bot is currently fetching RSS feed updates in this server.')
        else:
            await ctx.send(f'The bot is not fetching RSS feed updates in this server.')

    @rss.command(name='add')
    async def rss_add(ctx, feed_url = ''):
        await ctx.send(embed = rss_instance.add_feed(ctx, feed_url=feed_url))

    @rss.command(name='list')
    async def rss_list(ctx):
        await ctx.send(embed = rss_instance.list_feed(ctx))

    async def tools(ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                    title="List of available tools lists",
                    #url="https://github.com/OutlawOnGithub",
                    color=discord.Color.green()
                )
            embed.add_field(name='OSINT', value='Open SOurce INTelligence', inline=False)
            embed.add_field(name='Bruteforce', value='To crack passwords/hashes', inline=False)
            embed.add_field(name='Deepweb', value='Deepweb related tools', inline=False)
            embed.add_field(name='Training', value='Several places to train your skills', inline=False)
            embed.set_footer(text='To access the list, _tools <field>, everything in lowercase`')

            await ctx.send(embed=embed)


    @tools.command(name='OSINT')
    async def osint(ctx):
        embed = discord.Embed(
                    title="List of useful OSINT tools",
                    #url="https://github.com/OutlawOnGithub",
                    color=discord.Color.green()
                )
        embed.add_field(name='Email checker', value='Holehe (CLI)', inline=False)
        embed.add_field(name='List of OSINT tools', value='OSINT MAPS', inline=False)
        embed.add_field(name='DeepWeb Scraper', value='OnionSearch', inline=False)
        embed.set_footer(text='For any requests, DM `ox6cfc1ab7`')

        await ctx.send(embed=embed)

    @tools.command(name='bruteforce')
    async def bruteforce(ctx):
        embed = discord.Embed(
                    title="List of useful bruteforce tools",
                    #url="https://github.com/OutlawOnGithub",
                    color=discord.Color.green()
                )
        embed.add_field(name='To be added...', value='', inline=False)
        embed.set_footer(text='For any requests, DM `ox6cfc1ab7`')

        await ctx.send(embed=embed)

    @tools.command(name='geoip')
    async def geoip(ctx):
        embed = discord.Embed(
                    title="List of useful GEOIP related tools",
                    #url="https://github.com/OutlawOnGithub",
                    color=discord.Color.green()
                )
        embed.add_field(name='To be added...', value='', inline=False)
        embed.set_footer(text='For any requests, DM `ox6cfc1ab7`')

        await ctx.send(embed=embed)

    @bot.command()
    async def locateip(ctx, ip_address: str):
        if ip_address != ".":
            api_url = f'http://ip-api.com/json/{ip_address}'
            response = requests.get(api_url)
            
            if response.status_code == 200:
                data = response.json()

                embed = discord.Embed(
                    title=f'IP Information for {ip_address}',
                    color=discord.Color.green()
                )
                if data["status"] != "fail":
                    try:
                        embed.add_field(name="Country", value=f"{data['country']} [{data['countryCode']}], {data['regionName']} {data['region']}", inline=False)
                        embed.add_field(name="City", value=f"{data['city']} - {data['zip']}", inline=False)
                        embed.add_field(name="Geolocation (Lat, Lon)", value=f"{data['lat']}, {data['lon']}", inline=False)
                        embed.add_field(name="Timezone", value=f"{data['timezone']}", inline=False)
                        embed.add_field(name="Organisation", value=f"{data['isp']} ({data['org']})", inline=False)
                        embed.add_field(name="AS Number", value=f"{data['as']}", inline=False)
                    except Exception as e:
                        await ctx.send(f"Failed to fetch information for {ip_address}. Please check the IP and try again.")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"Failed to fetch information for {ip_address}. Please check the IP and try again.")
            else:
                await ctx.send(f"Failed to fetch information for {ip_address}. Please check the IP and try again.")
        else:
            await ctx.send(f"Nice try little coquinou !")


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
        embed.add_field(name='_tools <field>', value='Displays tools for the corresponding field', inline=False)
        embed.add_field(name='_locateip <ip>', value='Displays several informations about the given IP', inline=False)
        embed.add_field(name='_info', value='Displays information about the makers of this bot', inline=False)
        embed.add_field(name='_help', value='Displays this help message', inline=False)
        embed.set_footer(text='For any requests, DM `ox6cfc1ab7`')

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
        await ctx.send(embed=embed)


    bot.run(TOKEN, log_level=logging.DEBUG)

if __name__ == "__main__":
    main()
 