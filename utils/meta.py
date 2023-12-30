import discord
import requests
import re


class Meta:
    def __init__(self) -> None:
        pass

    def help(self, ctx):
        embed = discord.Embed(
            title="Command list",
            # url="https://github.com/OutlawOnGithub",
            color=discord.Color.blue(),
        )
        embed.add_field(
            name="_rss start/stop/add/del/list/channel",
            value="See the options related to RSS feeds",
            inline=False,
        )
        embed.add_field(
            name="_tools osint/bruteforce/deepweb/",
            value="Displays the lists of tools available",
            inline=False,
        )
        embed.add_field(
            name="_ip locate/rep",
            value="Displays the options related to IP adresses",
            inline=False,
        )
        embed.add_field(
            name="_info",
            value="Displays information about the makers of this bot",
            inline=False,
        )
        embed.add_field(name="_help", value="Displays this help message", inline=False)
        embed.set_footer(text="For any requests, DM `ox6cfc1ab7`")

        return embed

    def info(self, ctx):
        embed = discord.Embed(
            title="Informations about IC3BERG",
            url="https://github.com/OutlawOnGithub/IC3BERG/",
            description="""This bot is a personal project by two IT students, Outlaw and Ayerman/Firzam.
                                   It is currently in development and will, in the future, include numerous functionalities related to cybersecurity.
                                   The project will be opensourced on Github once we deploy the v1.0.0""",
            color=discord.Color.blue(),
        )
        return embed
