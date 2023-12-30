import discord
import requests
import re


class IP:
    def __init__(self) -> None:
        pass

    def default(self, ctx):
        embed = discord.Embed(
            title="List of available ip commands",
            color=discord.Color.dark_red(),
        )
        embed.add_field(name="locate", value="Get intel on an IP address", inline=False)
        embed.add_field(
            name="rep", value="Get the reputation of the IP address", inline=False
        )
        embed.set_footer(text="To suggest other IP related tools, DM `ox6cfc1ab7`")

        return embed

    def locate(self, ctx, ip_address):
        if (
            self.is_ipv4(ip_address)
            or self.is_ipv6(ip_address)
            or self.is_domain_name(ip_address)
        ):
            api_url = f"http://ip-api.com/json/{ip_address}"
            response = requests.get(api_url)

            if response.status_code == 200:
                data = response.json()

                embed = discord.Embed(
                    title=f"IP Information for {ip_address}",
                    color=discord.Color.dark_red(),
                )
                if data["status"] != "fail":
                    try:
                        embed.add_field(
                            name="Country",
                            value=f"{data['country']} [{data['countryCode']}], {data['regionName']} {data['region']}",
                            inline=False,
                        )
                        embed.add_field(
                            name="City",
                            value=f"{data['city']} - {data['zip']}",
                            inline=False,
                        )
                        embed.add_field(
                            name="Geolocation (Lat, Lon)",
                            value=f"{data['lat']}, {data['lon']}",
                            inline=False,
                        )
                        embed.add_field(
                            name="Timezone", value=f"{data['timezone']}", inline=False
                        )
                        embed.add_field(
                            name="Organisation",
                            value=f"{data['isp']} ({data['org']})",
                            inline=False,
                        )
                        embed.add_field(
                            name="AS Number", value=f"{data['as']}", inline=False
                        )
                        return embed
                    except Exception as e:
                        return discord.Embed(
                            title=f"Failed to fetch information for {ip_address}",
                            description="Please provide a valid IP and try again.",
                            color=discord.Color.dark_red(),
                        )
                elif data["message"] == "reserved range":
                    return discord.Embed(
                        title=f"This IP is either for private networks or reserved",
                        description="Please use a public IP or a domain name",
                        color=discord.Color.dark_red(),
                    )
                else:
                    return discord.Embed(
                        title=f"Failed to fetch information for {ip_address}",
                        description="Please check the IP and try again.",
                        color=discord.Color.dark_red(),
                    )
            else:
                return discord.Embed(
                    title=f"Failed to fetch information for {ip_address}",
                    description="Please check the IP and try again.",
                    color=discord.Color.dark_red(),
                )
        else:
            return discord.Embed(
                title=f"Please provide one of the following",
                description="IPv4 address, IPv6 address or domain name",
                color=discord.Color.dark_red(),
            )

    def reputation(self, ctx):
        pass

    def is_ipv4(self, address):
        # Regex
        ipv4_pattern = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")
        return bool(ipv4_pattern.match(address))

    def is_ipv6(self, address):
        # Regexfor IPv6
        ipv6_pattern = re.compile(r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$")
        return bool(ipv6_pattern.match(address))

    def is_domain_name(self, domain):
        # Regex for domain name
        domain_pattern = re.compile(r"^([a-zA-Z0-9_-]+\.){1,}[a-zA-Z]{2,}$")
        return bool(domain_pattern.match(domain))
