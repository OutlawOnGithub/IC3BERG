import discord
from discord.ext import commands, tasks
import os
import feedparser
from datetime import datetime, timezone
import asyncio
import logging
from utils.rss import *
from utils.ip import *
from utils.tools import *
from utils.meta import *


def main():
    TOKEN = os.getenv("DISCORD_TOKEN")


    bot = commands.Bot(
        command_prefix="_",
        intents=discord.Intents.all(),
        activity=discord.Activity(type=discord.ActivityType.playing, name="_help"),
        help_command=None,
    )

    channel_name = "infosec"
    fetching_status_per_server = {}

    rss_instance = RSS()
    tools_instance = Tools()
    ip_instance = IP()
    meta_instance = Meta()

    @bot.event
    async def on_ready():
        print(f"We have logged in as {bot.user}")

    @tasks.loop(minutes=20)
    async def fetch_feeds():
        for feed in rss_instance.feed_list:
            feed_url = feed["url"]
            already_fetched = feed["already_fetched"]

            if not already_fetched:
                news_feed = feedparser.parse(feed_url)

                if news_feed.entries:
                    embed = discord.Embed(
                        title=news_feed.entries[0]["title"],
                        url=news_feed.entries[0]["link"],
                        description=news_feed.entries[0]["description"]
                        .replace("<p>", "")
                        .replace("</p>", ""),
                        color=discord.Color.blue(),
                    )
                    embed.set_author(name=news_feed.entries[0]["author"])
                    current_time_gmt = datetime.datetime.now(timezone.utc)
                    formatted_time = current_time_gmt.strftime("%H:%M:%S %d/%m/%Y %Z")
                    embed.set_footer(text=f"{formatted_time}")

                    for guild in bot.guilds:
                        channel = discord.utils.get(
                            guild.channels,
                            name=channel_name,
                            type=discord.ChannelType.text,
                        )
                        if channel:
                            await channel.send(embed=embed)

                    feed["already_fetched"] = True

    @bot.group()
    async def rss(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=rss_instance.default(ctx))

    @rss.command(name="start")
    async def rss_start(ctx):
        if rss_instance.feed_list:
            if not fetch_feeds.is_running():
                fetch_feeds.start()
                await ctx.send("RSS feed updates will now be fetched every 20 minutes.")
            else:
                await ctx.send("RSS feed updates are already being fetched.")
        else:
            await ctx.send(
                "You must add a feed to fetch first ! Do `_rss add <feed_url>`"
            )

    @rss.command(name="stop")
    async def rss_stop(ctx):
        if fetch_feeds.is_running():
            fetch_feeds.cancel()
            await ctx.send("RSS feed updates fetching has been stopped.")
        else:
            fetch_feeds.cancel()
            await ctx.send("The bot is not currently fetching.")

    @rss.command(name="status")
    async def rss_status(ctx):
        if fetch_feeds.is_running():
            await ctx.send(
                f"The bot is currently fetching RSS feed updates in this server."
            )
        else:
            await ctx.send(f"The bot is not fetching RSS feed updates in this server.")

    @rss.command(name="add")
    async def rss_add(ctx, feed_url=""):
        await ctx.send(embed=rss_instance.add_feed(ctx, feed_url=feed_url))

    @rss.command(name="list")
    async def rss_list(ctx):
        await ctx.send(embed=rss_instance.list_feed(ctx))

    @bot.group(case_insensitive=True)
    async def tools(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=tools_instance.default())

    @tools.command(name="osint")
    async def osint(ctx):
        await ctx.send(embed=tools_instance.osint(ctx))

    @tools.command(name="bruteforce")
    async def bruteforce(ctx):
        await ctx.send(embed=tools_instance.bruteforce(ctx))

    @tools.command(name="deepweb")
    async def deepweb(ctx):
        await ctx.send(embed=tools_instance.deepweb(ctx))

    @tools.command(name="training")
    async def training(ctx):
        await ctx.send(embed=tools_instance.training(ctx))

    @bot.group(case_insensitive=True)
    async def ip(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=ip_instance.default(ctx))

    @ip.command(name="locate")
    async def ip_locate(ctx, ip_address: str):
        await ctx.send(embed=ip_instance.locate(ctx, ip_address=ip_address))

    @ip.command(name="rep", aliases=['reputation'])
    async def reputation(ctx, ip_address: str):
        await ctx.send(embed=ip_instance.reputation(ctx, ip_address=ip_address))

    @bot.command(name="help")
    async def help(ctx):
        await ctx.send(embed=meta_instance.help(ctx))

    @bot.command(name="info")
    async def info(ctx):
        await ctx.send(embed=meta_instance.info(ctx))

    bot.run(TOKEN, log_level=logging.DEBUG)


if __name__ == "__main__":
    main()