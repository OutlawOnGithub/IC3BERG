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

    rss_instance = RSS(SCHEME, DB_PW)
    tools_instance = Tools()
    ip_instance = IP()
    meta_instance = Meta()
    hash_instance = Hash()

    @bot.event
    async def on_ready():
        print(f"We have logged in as {bot.user}")
        fetch_feeds.start()

    @tasks.loop(seconds=30)
    async def fetch_feeds():
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname="iceberg",
            user="iceberg",
            password=DB_PW,
            host="postgres",  # This is the name of the PostgreSQL container
            port="5432"  # Default PostgreSQL port
        )

        cursor = conn.cursor()

        # Retrieve all servers where "enabled" is set to true and their corresponding RSS channel
        cursor.execute(f"SELECT guild_id, rss_channel FROM {SCHEME}.server WHERE enabled = TRUE;")
        enabled_servers = cursor.fetchall()

        for server_id, rss_channel_id in enabled_servers:
            # Fetch the server's selected RSS channel
            rss_channel = discord.utils.get(bot.get_guild(server_id).channels, id=rss_channel_id)

            if rss_channel:
                # Fetch the feeds associated with the server
                cursor.execute(f"SELECT url, last_fetched FROM {SCHEME}.rss WHERE guild_id = %s;", (server_id,))
                feeds = cursor.fetchall()

                for feed_url, latest_fetch in feeds:
                    # Parse the feed
                    news_feed = feedparser.parse(feed_url)

                    if news_feed.entries:
                        latest_link = news_feed.entries[0]["link"]
                        # Check if the latest fetched link is different from the current latest link
                        if latest_fetch != latest_link:
                            # Use unescape to decode HTML entities
                            decoded_description = unescape(remove_html_tags(news_feed.entries[0]["description"]))
                            embed = discord.Embed(
                                title=news_feed.entries[0]["title"],
                                url=latest_link,
                                description=decoded_description,
                                color=discord.Color.blue(),
                            )
                            if "author" in news_feed.entries[0]:
                                embed.set_author(name=news_feed.entries[0]["author"])
                            current_time_gmt = datetime.now(timezone.utc)
                            formatted_time = current_time_gmt.strftime("%H:%M:%S %d/%m/%Y %Z")
                            embed.set_footer(text=f"{formatted_time}")

                            # Send the embed to the RSS channel of the server
                            await rss_channel.send(embed=embed)

                            # Update the latest fetched link in the database
                            cursor.execute(
                                f"UPDATE {SCHEME}.rss SET last_fetched = %s WHERE url = %s AND guild_id = %s;",
                                (latest_link, feed_url, server_id)
                            )
                            conn.commit()


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

        if not count:
            # If the server ID doesn't exist, insert it into the database with "enabled" set to false
            cursor.execute(
                f"INSERT INTO {SCHEME}.server (guild_id, enabled) VALUES (%s, FALSE);",
                (ctx.guild.id,)
            )
            conn.commit()
            await ctx.send("Server added successfully!")
        else:
            await ctx.send("Server already enrolled.")

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

        if count:
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
    async def showfeeds(ctx):
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname="iceberg",
            user="iceberg",
            password=DB_PW,
            host="postgres",  # This is the name of the PostgreSQL container
            port="5432"  # Default PostgreSQL port
        )

        cursor = conn.cursor()

        # Fetch all rows from the "rss" table
        cursor.execute(f"SELECT * FROM {SCHEME}.rss;")
        feeds = cursor.fetchall()

        if feeds:
            # If there are feeds, format and send the table content
            table_content = "```URL                | Last Fetched     | Description       | Guild ID\n"
            table_content += "-------------------------------------------\n"
            for feed in feeds:
                table_content += f"{feed[0]:<18} | {feed[1]:<16} | {feed[2]:<17} | {feed[3]}\n"
            table_content += "```"
            await ctx.send("RSS Feeds:\n" + table_content)
        else:
            await ctx.send("No feeds found in the database.")

        # Close cursor and connection
        cursor.close()
        conn.close()


    @bot.group(case_insensitive = True)
    async def rss(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=rss_instance.default(ctx))

    @rss.command(name="start")
    async def rss_start(ctx):
        await ctx.send(embed=rss_instance.start(ctx))

    @rss.command(name="stop")
    async def rss_stop(ctx):
        await ctx.send(embed=rss_instance.stop(ctx))

    @rss.command(name="status")
    async def rss_status(ctx):
        await ctx.send(embed=rss_instance.status(ctx))

    @rss.command(name="set", aliases=['setchannel'])
    async def rss_setchannel(ctx, channel_name: str):
        await ctx.send(embed=rss_instance.set_channel(ctx, channel_name))

    @rss.command(name="add")
    async def rss_add(ctx, feed_url=""):
        await ctx.send(embed=rss_instance.add_feed(ctx, feed_url=feed_url))

    @rss.command(name="list")
    async def rss_list(ctx):
        await ctx.send(embed=rss_instance.list_feed(ctx))

    @rss.command(name="del", aliases=['rm', 'delete'])
    async def rss_del(ctx, feed_url):
        await ctx.send(embed=rss_instance.del_feed(ctx, feed_url))

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

    @tools.command(name="piracy")
    async def training(ctx):
        await ctx.send(embed=tools_instance.piracy(ctx))

    @tools.command(name="webdev")
    async def training(ctx):
        await ctx.send(embed=tools_instance.webdev(ctx))

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

    bot.run(TOKEN, log_level=logging.DEBUG)


if __name__ == "__main__":
    main()