import discord
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import psycopg2
import random


class RSS:
    def __init__(self) -> None:
        self.feed_list = [{
                        "url": "https://www.darkreading.com/rss.xml",
                        "description": "Dark Reading | Security | Protect The Business",
                        "latest_fetch": "False",
                    },{
                        "url": "https://www.cert.ssi.gouv.fr/feed/",
                        "description": "CERT-FR / Centre gouvernemental de veille, d'alerte et de réponse aux attaques informatiques",
                        "latest_fetch": "False",
                    }]

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

    def start(self, ctx, SCHEME, DB_PW):
        # Connect to PostgreSQL
        with psycopg2.connect(
            dbname="iceberg",
            user="iceberg",
            password=DB_PW,
            host="postgres",  # This is the name of the PostgreSQL container
            port="5432"  # Default PostgreSQL port
        ) as conn:
            with conn.cursor() as cursor:
                # Check if there is a channel ID associated with the server ID
                cursor.execute(
                    f"SELECT rss_channel FROM {SCHEME}.server WHERE guild_id = %s;",
                    (ctx.guild.id,)
                )
                channel_id = cursor.fetchone()

                # Check if there are any feeds added for this server
                cursor.execute(
                    f"SELECT COUNT(*) FROM {SCHEME}.rss WHERE guild_id = %s;",
                    (ctx.guild.id,)
                )
                nb_feeds = cursor.fetchone()[0]

                if channel_id and channel_id[0] is not None:
                    if nb_feeds > 0:
                        cursor.execute(
                            f"UPDATE {SCHEME}.server SET enabled = TRUE WHERE guild_id = %s;",
                            (ctx.guild.id,)
                        )
                        conn.commit()
                        return discord.Embed(
                            title="The bot has started fetching the added feeds",
                            description=f"Number of feeds used: {nb_feeds}/100",
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



    def stop(self, ctx, SCHEME, DB_PW):  # defined in main
        # Connect to PostgreSQL
        with psycopg2.connect(
            dbname="iceberg",
            user="iceberg",
            password=DB_PW,
            host="postgres",  # This is the name of the PostgreSQL container
            port="5432"  # Default PostgreSQL port
        ) as conn:
            with conn.cursor() as cursor:
                # Check if the bot is currently fetching feeds for the server
                cursor.execute(
                    f"SELECT enabled FROM {SCHEME}.server WHERE guild_id = %s;",
                    (ctx.guild.id,)
                )
                status = cursor.fetchone()

                if status is not None and status[0]:  # Check if the status is not None and is True
                    # Update the "enabled" attribute to FALSE to stop fetching feeds
                    cursor.execute(
                        f"UPDATE {SCHEME}.server SET enabled = FALSE WHERE guild_id = %s;",
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



    def status(self, ctx, SCHEME, DB_PW):  # defined in main
        # Connect to PostgreSQL
        with psycopg2.connect(
            dbname="iceberg",
            user="iceberg",
            password=DB_PW,
            host="postgres",  # This is the name of the PostgreSQL container
            port="5432"  # Default PostgreSQL port
        ) as conn:
            with conn.cursor() as cursor:
                # Retrieve the "enabled" attribute for the current server (guild)
                cursor.execute(
                    f"SELECT enabled FROM {SCHEME}.server WHERE guild_id = %s;",
                    (ctx.guild.id,)
                )
                enabled_status = cursor.fetchone()

                # Retrieve the number of feeds used for the current server (guild)
                cursor.execute(
                    f"SELECT COUNT(*) FROM {SCHEME}.rss WHERE guild_id = %s;",
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


    def add_feed(self, ctx, feed_url=""):  # add url check and rss feed check (if they are)
        if feed_url:
            if len(self.feed_list) <= 100:
                try:
                    desc = (
                        BeautifulSoup(
                            (requests.get("https://" + urlparse(feed_url).netloc).text),
                            "html.parser",
                        )
                    ).title.string  # good luck understanding that
                    new_feed_dict = {
                        "url": feed_url,
                        "description": desc,
                        "latest_fetch": "False",
                    }
                    self.feed_list.append(new_feed_dict)
                except Exception as e:
                    return discord.Embed(
                        title="You must add a valid url !", color=discord.Color.orange()
                    )
                return discord.Embed(
                    title="You successfully added a new RSS feed !",
                    description=feed_url,
                    color=discord.Color.orange(),
                )
            else:
                return discord.Embed(
                    title="You can't add more than 100 feeds",
                    description="Bro that's enough you're gonna make me lag",
                    color=discord.Color.orange(),
                )
        else:
            return discord.Embed(
                title="You must add an url !", color=discord.Color.orange()
            )

    def list_feed(self, ctx, SCHEME, DB_PW):
        # Connect to PostgreSQL using a context manager
        with psycopg2.connect(
            dbname="iceberg",
            user="iceberg",
            password=DB_PW,
            host="postgres",  # This is the name of the PostgreSQL container
            port="5432"  # Default PostgreSQL port
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                f"SELECT url, description FROM {SCHEME}.rss WHERE guild_id = %s;",
                (ctx.guild.id,)
            )
            feeds = cursor.fetchall()
                
            embed = discord.Embed(
            title="List of your RSS feeds", color=discord.Color.orange()
            )

            for feed in feeds:
                embed.add_field(name=feed[2], value=feed[0], inline=False)

            embed.set_footer(
                text=f"You are using {len(self.feed_list)} out of 100 feed slots"
            )

            return embed
        
    
        

    def del_feed(self, ctx, feed_url):
        if any(d["url"] == feed_url for d in self.feed_list):
            self.feed_list = [d for d in self.feed_list if d["url"] != feed_url]
            return discord.Embed(
                    title="Feed successfully removed",
                    description=f"You are using {len(self.feed_list)} out of 100 feed slots",
                    color=discord.Color.orange(),
                )
        else:
            return discord.Embed(
                    title="Feed url not found",
                    description="Please provide the url of the feed you want to remove",
                    color=discord.Color.orange(),
                )


    def set_channel(self, ctx, channel_name: str, SCHEME, DB_PW):
        # Get the channel object from the channel name
        channel = discord.utils.get(ctx.guild.channels, name=channel_name)
        
        if channel:
            # Connect to PostgreSQL using a context manager
            with psycopg2.connect(
                dbname="iceberg",
                user="iceberg",
                password=DB_PW,
                host="postgres",  # This is the name of the PostgreSQL container
                port="5432"  # Default PostgreSQL port
            ) as conn:
                with conn.cursor() as cursor:
                    # Update the "rss_channel" attribute with the selected channel's ID for the current server (guild)
                    cursor.execute(
                        f"UPDATE {SCHEME}.server SET rss_channel = %s WHERE guild_id = %s;",
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
