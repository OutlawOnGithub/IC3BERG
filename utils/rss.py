import discord
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import psycopg2
import random
from time import sleep


class RSS:
    def __init__(self, SCHEME, DB_PW) -> None:
        self.scheme = SCHEME
        self.db_pw = DB_PW


    def default(self, ctx):
        embed = discord.Embed(
            title="List of RSS commands", color=discord.Color.orange()
        )
        embed.add_field(
            name="_rss start", value="Starts fetching the feeds", inline=False
        )
        embed.add_field(name="_rss stop", value="Stops the feed fetching", inline=False)
        embed.add_field(
            name="_rss status",
            value="Tells if the bot is currently fetching feeds or not",
            inline=False,
        )
        embed.add_field(name="_rss add", value="Adds a feed to fetch", inline=False)
        embed.add_field(
            name="_rss del", value="Remove a feed from your list", inline=False
        )
        embed.add_field(
            name="_rss list", value="Lists the active feeds in the server", inline=False
        )
        embed.add_field(
            name="_rss channel",
            value="Sets the channel where the news are sent",
            inline=False,
        )
        embed.set_footer(text="For any requests, DM `ox6cfc1ab7`")

        return embed
    
    def register(self, ctx):
        # Connect to PostgreSQL
        with psycopg2.connect(
            dbname="iceberg",
            user="iceberg",
            password=self.db_pw,
            host="postgres",  # This is the name of the PostgreSQL container
            port="5432"  # Default PostgreSQL port
        ) as conn:
            with conn.cursor() as cursor:
        # Check if the current server (guild) is registered in the "server" table
                cursor.execute(
                    f"SELECT guild_id FROM {self.scheme}.server WHERE guild_id = %s;",
                    (ctx.guild.id,)
                )
                server_exists = cursor.fetchone()

                if server_exists is None:
                    # If the server is not registered, insert it with default values
                    cursor.execute(
                        f"INSERT INTO {self.scheme}.server (guild_id, enabled, rss_channel) VALUES (%s, %s, %s);",
                        (ctx.guild.id, True, None)  #adds the server to the DB and sets it on
                    )
                    conn.commit()  # Commit the insertion
                    # Optionally notify the user that the server was registered
                    return discord.Embed(
                        title="Server registered",
                        description="This server has been successfully registered in the database.\nYou now have to select your RSS channel with _rss set <channel_name>",
                        color=discord.Color.orange()
                    )
                else:
                    return discord.Embed(
                        title="This server is already registered",
                        color=discord.Color.orange()
                    )

    def start(self, ctx):
    # Connect to PostgreSQL
        with psycopg2.connect(
            dbname="iceberg",
            user="iceberg",
            password=self.db_pw,
            host="postgres",  # This is the name of the PostgreSQL container
            port="5432"  # Default PostgreSQL port
        ) as conn:
            with conn.cursor() as cursor:
                # Check if the current server (guild) is registered in the "server" table
                cursor.execute(
                    f"SELECT guild_id FROM {self.scheme}.server WHERE guild_id = %s;",
                    (ctx.guild.id,)
                )
                server_exists = cursor.fetchone()

                if server_exists is None:
                    return discord.Embed(
                        title="Server not registered",
                        description="You have to register the server first !",
                        color=discord.Color.orange()
                    )

                # Check if the bot is currently fetching feeds for the server
                cursor.execute(
                    f"SELECT enabled FROM {self.scheme}.server WHERE guild_id = %s;",
                    (ctx.guild.id,)
                )
                status = cursor.fetchone()

                if status is not None and not status[0]:  # Check if the status is not None and is False (not running)
                    # Check if there is a channel ID associated with the server ID
                    cursor.execute(
                        f"SELECT rss_channel FROM {self.scheme}.server WHERE guild_id = %s;",
                        (ctx.guild.id,)
                    )
                    channel_id = cursor.fetchone()

                    # Check if there are any feeds added for this server
                    cursor.execute(
                        f"SELECT COUNT(*) FROM {self.scheme}.rss WHERE guild_id = %s;",
                        (ctx.guild.id,)
                    )
                    nb_feeds = cursor.fetchone()[0]

                    if channel_id and channel_id[0] is not None:
                        if nb_feeds > 0:
                            # Set the bot as enabled for this server
                            cursor.execute(
                                f"UPDATE {self.scheme}.server SET enabled = TRUE WHERE guild_id = %s;",
                                (ctx.guild.id,)
                            )

                            # Set 'last_fetched' to NULL for all feeds associated with this guild
                            cursor.execute(
                                f"UPDATE {self.scheme}.rss SET last_fetched = NULL WHERE guild_id = %s;",
                                (ctx.guild.id,)
                            )

                            # Commit the transaction to apply both updates
                            conn.commit()

                            return discord.Embed(
                                title="The bot has started fetching your feeds",
                                description=f"Number of feeds used: {nb_feeds}/25",
                                color=discord.Color.orange()
                            )
                        else:
                            return discord.Embed(
                                title="Please add feeds",
                                description="No feeds added for this server. Use _rss add <feed_url>",
                                color=discord.Color.orange()
                            )
                    else:
                        return discord.Embed(
                            title="Please set the RSS channel",
                            description="Use _rss set <channel name>",
                            color=discord.Color.orange()
                        )
                else:
                    return discord.Embed(
                        title="The bot is already fetching news",
                        description="You can stop the bot with _rss stop",
                        color=discord.Color.orange()
                    )




    def stop(self, ctx):  # defined in main
        # Connect to PostgreSQL
        with psycopg2.connect(
            dbname="iceberg",
            user="iceberg",
            password=self.db_pw,
            host="postgres",  # This is the name of the PostgreSQL container
            port="5432"  # Default PostgreSQL port
        ) as conn:
            with conn.cursor() as cursor:
                # Check if the bot is currently fetching feeds for the server
                cursor.execute(
                    f"SELECT enabled FROM {self.scheme}.server WHERE guild_id = %s;",
                    (ctx.guild.id,)
                )
                status = cursor.fetchone()

                if status is not None and status[0]:  # Check if the status is not None and is True (running)
                    # Update the "enabled" attribute to FALSE to stop fetching feeds
                    cursor.execute(
                        f"UPDATE {self.scheme}.server SET enabled = FALSE WHERE guild_id = %s;",
                        (ctx.guild.id,)
                    )
                    conn.commit()
                    return discord.Embed(
                        title="The bot has stopped fetching your feeds",
                        color=discord.Color.orange()
                    )
                else:
                    return discord.Embed(
                        title="The bot isn't fetching news",
                        description="You can start the bot with _rss start",
                        color=discord.Color.orange()
                    )



    def status(self, ctx):  # defined in main
        # Connect to PostgreSQL
        with psycopg2.connect(
            dbname="iceberg",
            user="iceberg",
            password=self.db_pw,
            host="postgres",  # This is the name of the PostgreSQL container
            port="5432"  # Default PostgreSQL port
        ) as conn:
            with conn.cursor() as cursor:
                # Retrieve the "enabled" attribute for the current server (guild)
                cursor.execute(
                    f"SELECT enabled FROM {self.scheme}.server WHERE guild_id = %s;",
                    (ctx.guild.id,)
                )
                enabled_status = cursor.fetchone()

                # Retrieve the number of feeds used for the current server (guild)
                cursor.execute(
                    f"SELECT COUNT(*) FROM {self.scheme}.rss WHERE guild_id = %s;",
                    (ctx.guild.id,)
                )
                nb_feed = cursor.fetchone()[0]

                if enabled_status is not None:
                    if enabled_status[0]:
                        return discord.Embed(
                            title="The bot is currently fetching your feeds",
                            description=f"Number of feeds being fetched : {nb_feed}",
                            color=discord.Color.orange()
                        )
                    else:
                        if random.random() < 0.01:
                            return discord.Embed(
                                title="The lazy bot is taking a nap",
                                description=f"Wake him up by doing _rss start",
                                color=discord.Color.orange()
                            )
                        else:
                            return discord.Embed(
                                title="The bot isn't fetching your feeds",
                                color=discord.Color.orange()
                            )
                else:
                    return discord.Embed(
                        title="Server not enrolled yet",
                        description=f"Please use _rss setchannel to add your server to the database",
                        color=discord.Color.orange(),
                    )


    def add_feed(self, ctx, feed_url=""):
        if feed_url:
            # Check if the URL is valid
            parsed_url = urlparse(feed_url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                return discord.Embed(
                    title="You must add a valid URL!",
                    color=discord.Color.orange()
                )


            # Connect to PostgreSQL using a single connector
            with psycopg2.connect(
                dbname="iceberg",
                user="iceberg",
                password=self.db_pw,
                host="postgres",  # This is the name of the PostgreSQL container
                port="5432"  # Default PostgreSQL port
            ) as conn:
                with conn.cursor() as cursor:
                    # Check if the URL is already present in the database for the current server
                    cursor.execute(
                        f"SELECT COUNT(*) FROM {self.scheme}.rss WHERE url = %s AND guild_id = %s;",
                        (feed_url, ctx.guild.id)
                    )
                    if cursor.fetchone()[0]:
                        return discord.Embed(
                            title="This feed URL is already registered!",
                            color=discord.Color.orange()
                        )

                    # Check if there are no more than 25 feeds registered for the server
                    cursor.execute(
                        f"SELECT COUNT(*) FROM {self.scheme}.rss WHERE guild_id = %s;",
                        (ctx.guild.id,)
                    )
                    num_feeds = cursor.fetchone()[0]
                    if num_feeds >= 25:
                        return discord.Embed(
                            title="You can't add more than 25 feeds",
                            description="Bro, that's enough. You're gonna make me lag!",
                            color=discord.Color.orange()
                        )

                    # Fetch feed description using BeautifulSoup
                    try:
                        desc = BeautifulSoup(
                            requests.get("https://" + parsed_url.netloc).text,
                            "html.parser"
                        ).title.string
                    except Exception as e:
                        return discord.Embed(
                            title="Failed to fetch feed description !",
                            description=f"{feed_url} doesn't exist :/",
                            color=discord.Color.orange()
                        )

                    # Insert the new feed into the database
                    cursor.execute(
                        f"INSERT INTO {self.scheme}.rss (url, description, guild_id) VALUES (%s, %s, %s);",
                        (feed_url, desc, ctx.guild.id)
                    )
                    conn.commit()

            return discord.Embed(
                title="You successfully added a new RSS feed!",
                description=feed_url,
                color=discord.Color.orange()
            )
        else:
            return discord.Embed(
                title="You must add a URL!",
                color=discord.Color.orange()
            )


    def list_feed(self, ctx):
        # Connect to PostgreSQL using a context manager
        with psycopg2.connect(
            dbname="iceberg",
            user="iceberg",
            password=self.db_pw,
            host="postgres",  # This is the name of the PostgreSQL container
            port="5432"  # Default PostgreSQL port
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"SELECT url, description FROM {self.scheme}.rss WHERE guild_id = %s;",
                    (ctx.guild.id,)
                )
                feeds = cursor.fetchall()
                
        embed = discord.Embed(
            title="List of your RSS feeds",
            color=discord.Color.orange()
        )

        for feed in feeds:
            embed.add_field(name=feed[1], value=feed[0], inline=False)

        embed.set_footer(
            text=f"You are using {len(feeds)} out of 25 feed slots"
        )

        return embed


    def del_feed(self, ctx, feed_url):
        with psycopg2.connect(
            dbname="iceberg",
            user="iceberg",
            password=self.db_pw,
            host="postgres",  # This is the name of the PostgreSQL container
            port="5432"  # Default PostgreSQL port
        ) as conn:
            with conn.cursor() as cursor:
                # Delete the feed from the database based on its URL and the guild ID of the current server
                cursor.execute(
                    f"DELETE FROM {self.scheme}.rss WHERE url = %s AND guild_id = %s RETURNING *;",
                    (feed_url, ctx.guild.id)
                )
                deleted_feed = cursor.fetchone()
                conn.commit()
                sleep(0.2)
                # Determine the number of feeds used by the current server after deletion
                cursor.execute(
                    f"SELECT COUNT(*) FROM {self.scheme}.rss WHERE guild_id = %s;",
                    (ctx.guild.id,)
                )
                feeds_nb = cursor.fetchone()[0]

                # Check if the feed was successfully deleted
                if deleted_feed is not None:
                    return discord.Embed(
                        title="RSS feed successfully deleted",
                        description=f"You are using {feeds_nb} out of 25 feed slots",
                        color=discord.Color.orange(),
                    )
                else:
                    return discord.Embed(
                        title="Feed URL not found",
                        description="The provided URL does not match any existing feed",
                        color=discord.Color.orange(),
                    )




    def set_channel(self, ctx, channel_name: str):
        # Get the channel object from the channel name
        channel = discord.utils.get(ctx.guild.channels, name=channel_name)
        
        if channel:
            # Connect to PostgreSQL using a context manager
            with psycopg2.connect(
                dbname="iceberg",
                user="iceberg",
                password=self.db_pw,
                host="postgres",  # This is the name of the PostgreSQL container
                port="5432"  # Default PostgreSQL port
            ) as conn:
                with conn.cursor() as cursor:
                    # Update the "rss_channel" attribute with the selected channel's ID for the current server (guild)
                    cursor.execute(
                        f"UPDATE {self.scheme}.server SET rss_channel = %s WHERE guild_id = %s;",
                        (channel.id, ctx.guild.id)
                    )
                    conn.commit()
                    
            return discord.Embed(
                title="RSS channel successfully set up",
                color=discord.Color.orange(),
            )
        else:
            return discord.Embed(
                title="Channel not found",
                description="Please provide the name of a channel in your server",
                color=discord.Color.orange(),
            )
