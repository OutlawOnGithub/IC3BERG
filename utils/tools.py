import discord


class Tools:
    def __init__(self) -> None:
        pass

    def default(ctx):
        embed = discord.Embed(
            title="List of available tools lists",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="OSINT", value="Open SOurce INTelligence", inline=False)
        embed.add_field(
            name="Bruteforce", value="To crack passwords/hashes", inline=False
        )
        embed.add_field(name="Deepweb", value="Deepweb related tools", inline=False)
        embed.add_field(
            name="Training",
            value="Several places to train your skills",
            inline=False,
        )
        embed.set_footer(text="To access the list, _tools <field>")

        return embed

    def osint(self, ctx):
        embed = discord.Embed(
            title="List of useful OSINT tools",
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="List of OSINT tools",
            value="[OSINT Framework](https://osintframework.com/)",
            inline=False,
        )
        embed.add_field(
            name="Email or phone number checker",
            value="[Epieos](https://epieos.com/)",
            inline=False,
        )
        embed.add_field(
            name="Email to registered accounts",
            value="[Holehe (CLI)](https://github.com/megadose/holehe)",
            inline=False,
        )
        embed.set_footer(text="To help extend the list, DM `ox6cfc1ab7`")

        return embed

    def deepweb(self, ctx):
        embed = discord.Embed(
            title="List of useful deepweb tools",
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="Deepweb Search Engine",
            value="[Torch](http://xmh57jrknzkhv6y3ls3ubitzfqnkrwxhopf5aygthi7d6rplyvk3noyd.onion/)",
            inline=False,
        )
        embed.add_field(
            name="DeepWeb Scraper",
            value="[OnionSearch](https://github.com/megadose/OnionSearch)",
            inline=False,
        )
        embed.set_footer(text="To help extend the list, DM `ox6cfc1ab7`")

        return embed

    def bruteforce(self, ctx):
        embed = discord.Embed(
            title="List of bruteforce tools",
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="Service bruteforcer (http.s/ssh/ftp/...)",
            value="[Hydra](https://www.kali.org/tools/hydra/)",
            inline=False,
        )
        embed.add_field(
            name="Hash bruteforce tool",
            value="[Hashcat](https://hashcat.net/hashcat/)",
            inline=False,
        )
        embed.set_footer(text="To help extend the list, DM `ox6cfc1ab7`")

        return embed

    def training(self, ctx):
        embed = discord.Embed(
            title="The best websites to become a H4ck3Я",
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="For newbies",
            value="[TryHackMe](https://tryhackme.com/)",
            inline=False,
        )
        embed.add_field(
            name="For script kiddies to advanced",
            value="[RootMe](https://www.root-me.org/)",
            inline=False,
        )
        embed.add_field(
            name="For advanced to real haxxors",
            value="[HackTheBox](https://app.hackthebox.com/)",
            inline=False,
        )
        embed.set_footer(text="To help extend the list, DM `ox6cfc1ab7`")

        return embed
