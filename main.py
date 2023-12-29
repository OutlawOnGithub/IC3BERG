import os

import hikari

bot = hikari.GatewayBot(token=os.environ["DISCORD_TOKEN"])


@bot.listen()
async def on_message(event: hikari.MessageCreateEvent) -> None:
    """Listen for messages being created."""
    if not event.is_human:
        # Do not respond to bots or webhooks!
        return

    if event.content == "!ping":
        await event.message.respond(f"Pong! {bot.heartbeat_latency * 1_000:.0f}ms")


bot.run()