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
        if self.is_ip(ip_address) or self.is_domain_name(ip_address):
            api_url = f"http://ip-api.com/json/{ip_address}"
            response = requests.get(api_url)

            if response.status_code == 200:
                data = response.json()

                if data["status"] != "fail":
                    try:
                        embed = discord.Embed(
                            title=f"IP Information for {data['query']}",
                            color=discord.Color.dark_magenta(),
                        )
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
                        embed.set_footer(
                            text="These results are provided by http://ip-api.com/"
                        )
                        return embed
                    except Exception as e:
                        return discord.Embed(
                            title=f"Failed to fetch information for {ip_address}",
                            description="Please provide a valid IP and try again.",
                            color=discord.Color.dark_magenta(),
                        )
                elif data["message"] == "reserved range":
                    return discord.Embed(
                        title=f"This IP is either for private networks or reserved",
                        description="Please use a public IP or a domain name",
                        color=discord.Color.dark_magenta(),
                    )
                else:
                    return discord.Embed(
                        title=f"Failed to fetch information for {ip_address}",
                        description="Please check the IP and try again.",
                        color=discord.Color.dark_magenta(),
                    )
            else:
                return discord.Embed(
                    title=f"Failed to fetch information for {ip_address}",
                    description="Please check the IP and try again.",
                    color=discord.Color.dark_magenta(),
                )
        else:
            return discord.Embed(
                title=f"Please provide one of the following",
                description="IPv4 address, IPv6 address or domain name",
                color=discord.Color.dark_magenta(),
            )

    def reputation(self, ctx, ip_address):
        if self.is_ip(ip_address):
            # API endpoint
            api_url = "https://api.abuseipdb.com/api/v2/check"

            # API parameters
            params = {
                "ipAddress": ip_address,
                "maxAgeInDays": 90,
                "verbose": True,
            }

            # API headers
            headers = {
                "Key": "9c2a39e12e6b8864ab3f75be3f6b0ed399e229dda96d81c9202e1d8500706c71bbdcc8eb63074cf3",
                "Accept": "application/json",
            }

            # Make API request
            response = requests.get(api_url, params=params, headers=headers)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                data = response.json()
                if data['data']['isPublic']:
                    abuseScore = data["data"]["abuseConfidenceScore"]
                    filled_blocks = int(abuseScore / 3)
                    empty_blocks = 33 - filled_blocks
                    loading_bar_str = "█" * filled_blocks + "░" * empty_blocks
                    if not data["data"]["isTor"]:
                        # Create an embed with information from the API response
                        match abuseScore:
                            case value if value < 50:
                                embed = discord.Embed(
                                    title=f"This IP is safe",
                                    description=f"AbuseIPDB Report for {ip_address}",
                                    color=discord.Color.green(),
                                )
                            case value if value > 50 and value < 80:
                                embed = discord.Embed(
                                    title=f"This IP is probably malicious",
                                    description=f"AbuseIPDB Report for {ip_address}",
                                    color=discord.Color.yellow(),
                                )
                            case value if value > 80:
                                embed = discord.Embed(
                                    title=f"This IP is know as malicious",
                                    description=f"AbuseIPDB Report for {ip_address}",
                                    color=discord.Color.red(),
                                )
                                embed.add_field(
                                    name="Number of total reports",
                                    value=data["data"]["totalReports"],
                                    inline=False,
                                )
                        embed.add_field(
                            name=f"IP location",
                            value=f"{data['data']['countryCode']}",
                            inline=False,
                        )
                        embed.add_field(
                            name=f"ISP", value=data["data"]["isp"], inline=False
                        )
                        embed.add_field(
                            name=f"Abuse confidence score : {abuseScore}",
                            value=f" `{loading_bar_str}`",
                            inline=False,
                        )
                        embed.set_footer(text="Do _ip locate <ip> for more details")
                        return embed
                    else:
                        embed = discord.Embed(
                            title=f"This IP is a known TOR node",
                            description=f"AbuseIPDB Report for {ip_address}",
                            color=discord.Color.purple(),
                        )
                        embed.add_field(
                            name="Number of total reports",
                            value=data["data"]["totalReports"],
                            inline=False,
                        )
                        embed.add_field(
                            name=f"IP location",
                            value=f"{data['data']['countryCode']}",
                            inline=False,
                        )
                        embed.add_field(
                            name=f"ISP", value=data["data"]["isp"], inline=False
                        )
                        embed.add_field(
                            name=f"Abuse confidence score : {abuseScore}",
                            value=f" `{loading_bar_str}`",
                            inline=False,
                        )
                        return embed
                else:
                    return discord.Embed(
                        title=f"This IP is either for private networks or reserved",
                        description="Please use a public IP",
                        color=discord.Color.dark_magenta(),
                    )
            else:
                return discord.Embed(
                    title=f"Error fetching data from AbuseIPDB",
                    description=f"Status Code: {response.status_code}",
                    color=discord.Color.dark_magenta(),
                )
        else:
            return discord.Embed(
                    title=f"Please provide a valid IPv4/6 adress",  
                    color=discord.Color.dark_magenta(),
                )

    def is_ip(self, address):
        # Regex for IPv4 and IPv6
        ip_pattern = re.compile(
            r"""
            ^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))|
            ((([0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}:[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){5}:([0-9A-Fa-f]{1,4}:)?[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){4}:([0-9A-Fa-f]{1,4}:){0,2}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){3}:([0-9A-Fa-f]{1,4}:){0,3}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){2}:([0-9A-Fa-f]{1,4}:){0,4}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}((b((25[0-5])|(1d{2})|(2[0-4]d)|(d{1,2}))b).){3}(b((25[0-5])|(1d{2})|(2[0-4]d)|(d{1,2}))b))|(([0-9A-Fa-f]{1,4}:){0,5}:((b((25[0-5])|(1d{2})|(2[0-4]d)|(d{1,2}))b).){3}(b((25[0-5])|(1d{2})|(2[0-4]d)|(d{1,2}))b))|(::([0-9A-Fa-f]{1,4}:){0,5}((b((25[0-5])|(1d{2})|(2[0-4]d)|(d{1,2}))b).){3}(b((25[0-5])|(1d{2})|(2[0-4]d)|(d{1,2}))b))|([0-9A-Fa-f]{1,4}::([0-9A-Fa-f]{1,4}:){0,5}[0-9A-Fa-f]{1,4})|(::([0-9A-Fa-f]{1,4}:){0,6}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){1,7}:))$
        """,
            re.VERBOSE,
        )

        return bool(ip_pattern.match(address))

    def is_domain_name(self, domain):
        # Regex for domain name
        domain_pattern = re.compile(r"^([a-zA-Z0-9_-]+\.){1,}[a-zA-Z]{2,}$")
        return bool(domain_pattern.match(domain))
