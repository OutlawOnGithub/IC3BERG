import discord
import feedparser
import datetime
import json
import requests
import os


class RSS():

    def __init__(self) -> None:
        self.latest_id = ''
  
    def fetch_a_feed(self, news_feed):       
        for i in range(0, len(news_feed.entries)):
            if i == (len(news_feed.entries)-1):
                if self.latest_id != news_feed.entries[0]['id']: #test si c'est nouveau
                    print(f"Auteur: {news_feed.entries[0]['author']} \n Titre: {news_feed.entries[0]['title']}\nRésumé : {news_feed.entries[0]['summary']}")
                    embed = discord.Embed(
                        title=news_feed.entries[0]['title'],
                        url=news_feed.entries[0]['link'],
                        description=news_feed.entries[0]['summary'],
                        color=discord.Color.blue()
                    )
                    embed.set_author(name=news_feed.entries[0]['author'])
                    embed.set_footer(text=f"{datetime.datetime.utcnow()}")
                    self.latest_id = news_feed.entries[0]['id']
                    return embed
                else:
                    return None

    