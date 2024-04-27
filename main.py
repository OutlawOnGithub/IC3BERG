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
        fetch_feeds.start()

    @tasks.loop(seconds=20)
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

        # Retrieve all servers where "enabled" is set to true
        cursor.execute(f"SELECT guild_id FROM {SCHEME}.server WHERE enabled = TRUE;")
        enabled_servers = cursor.fetchall()

        # Close cursor and connection
        cursor.close()
        conn.close()

        for server in enabled_servers:
            #refetch all feeds
            pass

        
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

        # Retrieve all enrolled servers from the database with their "enabled" status
        cursor.execute(f"SELECT guild_id, enabled FROM {SCHEME}.server;")
        enrolled_servers = cursor.fetchall()

        if enrolled_servers:
            # If there are enrolled servers, format and send the list with "enabled" status
            server_info = "\n".join([f"Server ID: {server[0]}, Enabled: {server[1]}" for server in enrolled_servers])
            await ctx.send(f"Enrolled servers:\n{server_info}")
        else:
            await ctx.send("No servers enrolled.")

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

    @bot.command()
    async def activefeeds(ctx):
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname="iceberg",
            user="iceberg",
            password=DB_PW,
            host="postgres",  # This is the name of the PostgreSQL container
            port="5432"  # Default PostgreSQL port
        )

        cursor = conn.cursor()

        # Fetch the enabled status for the current server (guild)
        cursor.execute(
            f"SELECT enabled FROM {SCHEME}.server WHERE guild_id = %s;",
            (ctx.guild.id,)
        )
        enabled_status = cursor.fetchone()

        if enabled_status and enabled_status[0] is True:
            # If the RSS feed is enabled for the current server, fetch the feeds associated with it
            cursor.execute(
                f"SELECT url, last_fetched, description FROM {SCHEME}.rss WHERE guild_id = %s;",
                (ctx.guild.id,)
            )
            feeds = cursor.fetchall()

            if feeds:
                # If there are feeds associated with the server, format and send them
                feed_list = "```Enabled: True\n\n"
                feed_list += "Feeds:\n"
                feed_list += "URL                | Last Fetched     | Description\n"
                feed_list += "-----------------------------------------\n"
                for feed in feeds:
                    feed_list += f"{feed[0]:<18} | {feed[1]:<16} | {feed[2]}\n"
                feed_list += "```"
                await ctx.send(feed_list)
            else:
                await ctx.send("No feeds found for this server.")
        else:
            await ctx.send("RSS feed is not enabled for this server.")

        # Close cursor and connection
        cursor.close()
        conn.close()


    @bot.command()
    async def addfeed(ctx, feed_url: str, *, description: str = ""):
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname="iceberg",
            user="iceberg",
            password=DB_PW,
            host="postgres",  # This is the name of the PostgreSQL container
            port="5432"  # Default PostgreSQL port
        )

        cursor = conn.cursor()

        # Insert the feed URL, last fetched (initialized to false), description, and guild ID into the database
        cursor.execute(
            f"INSERT INTO {SCHEME}.rss (url, last_fetched, description, guild_id) VALUES (%s, %s, %s, %s);",
            (feed_url, False, description, ctx.guild.id)
        )
        conn.commit()
        await ctx.send("Feed added successfully.")

        # Close cursor and connection
        cursor.close()
        conn.close()

    @bot.command()
    async def delfeed(ctx, feed_url: str):
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname="iceberg",
            user="iceberg",
            password=DB_PW,
            host="postgres",  # This is the name of the PostgreSQL container
            port="5432"  # Default PostgreSQL port
        )

        cursor = conn.cursor()

        # Delete the feed from the database based on its URL and the guild ID of the current server
        cursor.execute(
            f"DELETE FROM {SCHEME}.rss WHERE url = %s AND guild_id = %s;",
            (feed_url, ctx.guild.id)
        )
        conn.commit()

        if cursor.rowcount > 0:
            await ctx.send("Feed deleted successfully.")
        else:
            await ctx.send("No feed found with the provided URL.")

        # Close cursor and connection
        cursor.close()
        conn.close()



    @bot.group(case_insensitive = True)
    async def rss(ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=rss_instance.default(ctx))

    @rss.command(name="start")
    async def rss_start(ctx):
        await ctx.send(embed=rss_instance.start(ctx, SCHEME, DB_PW))

    @rss.command(name="stop")
    async def rss_stop(ctx):
        await ctx.send(embed=rss_instance.stop(ctx, SCHEME, DB_PW))

    @rss.command(name="status")
    async def rss_status(ctx):
        await ctx.send(embed=rss_instance.status(ctx, SCHEME, DB_PW))

    @rss.command(name="set", aliases=['setchannel'])
    async def rss_setchannel(ctx, channel_name: str):
        await ctx.send(embed=rss_instance.set_channel(ctx, channel_name, SCHEME, DB_PW))

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