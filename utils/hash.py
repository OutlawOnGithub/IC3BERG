import discord
import hashlib


class Hash:
    def __init__(self) -> None:
        pass

    def default(self, ctx):
        embed = discord.Embed(
            title="Hash command list",
            # url="https://github.com/OutlawOnGithub",

            color=discord.Color.blue(),
        )
        embed.add_field(
            name="_hash md5 <string>",
            value="Generates the MD5 Hash of the given string",
            inline=False,
        )
        embed.add_field(
            name="_hash sha1 string>",
            value="Generates the SHA1 Hash of the given string",
            inline=False,
        )
        return embed

    def help(self, ctx):
        embed = discord.Embed(
            title="Hash help",
            description="You can generate several different hashes of a given string",
            color=discord.Color.red(),
        )
        return embed
    
    def md5(self, ctx, string):
        embed = discord.Embed(
            title=f"MD5 Hash of {string}",
            description=hashlib.md5(string.encode()).hexdigest(),
            color=discord.Color.red(),
        )
        return embed
    
    def sha1(self, ctx, string):
        embed = discord.Embed(
            title=f"SHA1 Hash of {string}",
            description=hashlib.sha1(string.encode()).hexdigest(),
            color=discord.Color.red(),
        )
        return embed
    
    def sha256(self, ctx, string):
        embed = discord.Embed(
            title=f"SHA-256 Hash of {string}",
            description=hashlib.sha256(string.encode()).hexdigest(),
            color=discord.Color.red(),
        )
        return embed
