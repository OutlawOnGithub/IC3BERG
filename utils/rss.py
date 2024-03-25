import discord
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup


class RSS:
    def __init__(self) -> None:
        self.feed_list = [{
                        "url": "https://www.darkreading.com/rss.xml",
                        "description": "Dark Reading | Security | Protect The Business",
                        "already_fetched": False,
                    },{
                        "url": "https://www.cert.ssi.gouv.fr/feed/",
                        "description": "CERT-FR / Centre gouvernemental de veille, d'alerte et de réponse aux attaques informatiques",
                        "already_fetched": False,
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

    def start(self, ctx):  # defined in main
        pass

    def stop(self, ctx):  # defined in main
        pass

    def status(self, ctx):  # defined in main
        pass

    def add_feed(
        self, ctx, feed_url=""
    ):  # add url check and rss feed check (if they are)
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
                        "already_fetched": False,
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

    def list_feed(self, ctx):
        embed = discord.Embed(
            title="List of your RSS feeds", color=discord.Color.orange()
        )

        for feed in self.feed_list:
            embed.add_field(name=feed["description"], value=feed["url"], inline=False)

        embed.set_footer(
            text=f"You are using {len(self.feed_list)} out of 100 feed slots"
        )

        return embed

    def del_feed(self, ctx):
        pass

    def set_channel(self, ctx):
        pass
