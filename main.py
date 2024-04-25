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
from utils.hash import *
from html import unescape
import psycopg2



def main():
    TOKEN = os.getenv("DISCORD_TOKEN")
    DB_PW = os.getenv("POSTGRES_PASSWORD")
    PREFIX = os.getenv("BOT_PREFIX")
    SCHEME = os.getenv("SCHEME")

    bot = commands.Bot(
        command_prefix=PREFIX,
        intents=discord.Intents.all(),
        activity=discord.Activity(type=discord.ActivityType.playing, name=PREFIX+"help"),
        help_command=None,
    )   
    
    channel_name = "infosec"

    # for guild in bot.guilds:
    #         guild_id = guild.id
    #         enabled = False
    #         print("trying to init db")

    #         # Insert guild_id and enabled status into the server table
    #         cursor.execute(
    #             f"INSERT INTO {SCHEME}.server (guild_id, enabled) VALUES (%s, %s);",
    #             (guild_id, enabled)
    #         )

    #print("inited db")

    rss_instance = RSS()
    tools_instance = Tools()
    ip_instance = IP()
    meta_instance = Meta()
    hash_instance = Hash()

    @bot.event
    async def on_ready():
        print(f"We have logged in as {bot.user}")

    @tasks.loop(seconds=20)
    async def fetch_feeds():
        for feed in rss_instance.feed_list:
            feed_url = feed["url"]
            latest_fetch = feed["latest_fetch"]

            news_feed = feedparser.parse(feed_url)

            if news_feed.entries:
                if latest_fetch != news_feed.entries[0]["link"]:
                    # Use unescape to decode HTML entities
                    decoded_description = unescape(remove_html_tags(news_feed.entries[0]["description"]))
                    embed = discord.Embed(
                        title=news_feed.entries[0]["title"],
                        url=news_feed.entries[0]["link"],
                        description=decoded_description,
                        color=discord.Color.blue(),
                    )
                    if "author" in news_feed.entries[0]:
                        embed.set_author(name=news_feed.entries[0]["author"])
                    current_time_gmt = datetime.now(timezone.utc)
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

                    feed["latest_fetch"] = news_feed.entries[0]["link"]

    @bot.command()
    async def test(ctx):

        # Connect to PostgreSQL
        conn = psycopg2.connect(
        dbname="iceberg",
        user="iceberg",
        password=DB_PW,
        host="postgres",  # This is the name of the PostgreSQL container
        port="5432"  # Default PostgreSQL port
        )

        cursor = conn.cursor()

        server_query = f"SELECT * FROM {SCHEME}.server;"
        cursor.execute(server_query)
        server_records = cursor.fetchall()
        await ctx.send(server_records)

        # Close cursor and connection
        cursor.close()
        conn.close()


    @bot.command()
    async def testEnroll(ctx):
        # Connect to PostgreSQL
        conn = psycopg2.connect(
        dbname="iceberg",
        user="iceberg",
        password=DB_PW,
        host="postgres",  # This is the name of the PostgreSQL container
        port="5432"  # Default PostgreSQL port
        )

        cursor = conn.cursor()

        cursor.execute(
            f"SELECT COUNT(*) FROM {SCHEME}.server WHERE guild_id = %s;",
            (ctx.guild.id,)
        )

        # Commit the changes to the database
        #conn.commit()
        count = cursor.fetchone()[0]
        # Close cursor and connection
        
        cursor.close()
        conn.close()
        await ctx.send(count)

    @bot.command()
    async def addserv(ctx):
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname="iceberg",
            user="iceberg",
            password=DB_PW,
            host="postgres",  # This is the name of the PostgreSQL container
            port="5432"  # Default PostgreSQL port
        )

        cursor = conn.cursor()

        # Check if the server ID already exists in the database
        cursor.execute(
            f"SELECT COUNT(*) FROM {SCHEME}.server WHERE guild_id = %s;",
            (ctx.guild.id,)
        )
        count = cursor.fetchone()[0]

        if count == 0:
            # If the server ID doesn't exist, insert it into the database
            cursor.execute(
                f"INSERT INTO {SCHEME}.server (guild_id) VALUES (%s);",
                (ctx.guild.id,)
            )
            conn.commit()
            await ctx.send("Server enrolled successfully!")
        else:
            await ctx.send("Server already enrolled!")

        # Close cursor and connection
        cursor.close()
        conn.close()


    @bot.command()
    async def delserv(ctx):
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname="iceberg",
            user="iceberg",
            password=DB_PW,
            host="postgres",  # This is the name of the PostgreSQL container
            port="5432"  # Default PostgreSQL port
        )

        cursor = conn.cursor()

        # Check if the server ID exists in the database
        cursor.execute(
            f"SELECT COUNT(*) FROM {SCHEME}.server WHERE guild_id = %s;",
            (ctx.guild.id,)
        )
        count = cursor.fetchone()[0]

        if count > 0:
            # If the server ID exists, delete it from the database
            cursor.execute(
                f"DELETE FROM {SCHEME}.server WHERE guild_id = %s;",
                (ctx.guild.id,)
            )
            conn.commit()
            await ctx.send("Server removed successfully!")
        else:
            await ctx.send("Server ID not found in the database.")

        # Close cursor and connection
        cursor.close()
        conn.close()

    @bot.command()
    async def showserv(ctx):
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname="iceberg",
            user="iceberg",
            password=DB_PW,
            host="postgres",  # This is the name of the PostgreSQL container
            port="5432"  # Default PostgreSQL port
        )

        cursor = conn.cursor()

        # Retrieve all enrolled servers from the database
        cursor.execute(f"SELECT guild_id FROM {SCHEME}.server;")
        enrolled_servers = cursor.fetchall()

        if enrolled_servers:
            # If there are enrolled servers, format and send the list
            enrolled_list = "\n".join([f"Server ID: {server[0]}" for server in enrolled_servers])
            await ctx.send(f"Enrolled servers:\n{enrolled_list}")
        else:
            await ctx.send("No servers enrolled.")

        # Close cursor and connection
        cursor.close()
        conn.close()





    @bot.group(case_insensitive = True)
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

    @rss.command(name="del", aliases=['rm'])
    async def rss_del(ctx, feed_url):
        await ctx.send(embed=rss_instance.del_feed(ctx, feed_url=feed_url))

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

    @bot.group(case_insensitive=True)
    async def hash(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=hash_instance.default(ctx))

    @hash.command(name="md5")
    async def md5(ctx, string):
        await ctx.send(embed=hash_instance.md5(ctx, string))

    @hash.command(name="sha1")
    async def sha1(ctx, string):
        await ctx.send(embed=hash_instance.sha1(ctx, string))

    @hash.command(name="sha256")
    async def sha256(ctx, string):
        await ctx.send(embed=hash_instance.sha256(ctx, string))

    @hash.command(name="help")
    async def help(ctx):
        await ctx.send(embed=hash_instance.help(ctx))

    def remove_html_tags(text):
        clean_text = re.sub(r'<[^>]+>', '', text)
        return clean_text

    bot.run(TOKEN, log_level=logging.INFO)


if __name__ == "__main__":
    main()