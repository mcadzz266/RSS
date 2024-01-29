import os
import sys
import requests
import feedparser
from sql import db
from time import sleep, time
from bs4 import BeautifulSoup as Bs
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from apscheduler.schedulers.background import BackgroundScheduler


try:
    api_id = int(os.environ["API_ID"])   # Get it from my.telegram.org
    api_hash = os.environ["API_HASH"]   # Get it from my.telegram.org
    feed_urls = list(set(i for i in os.environ["FEED_URLS"].split("|")))  # RSS Feed URL of the site.
    bot_token = os.environ["STR_SESSION"]   # Get it by creating a bot on https://t.me/botfather
    log_channel = int(os.environ["LOG_CHANNEL"])   # Telegram Channel ID where the bot is added and have write permission. You can use group ID too.
    check_interval = int(os.environ.get("INTERVAL", 10))   # Check Interval in seconds.  
    max_instances = int(os.environ.get("MAX_INSTANCES", 3))   # Max parallel instance to be used.
    mirr_cmd = os.environ.get("MIRROR_CMD", "/qbmirror1")    #if you have changed default cmd of mirror bot, replace this.
    err_id = "2049068956"
    cmds = mirr_cmd.split()
    co = [0,1]
except Exception as e:
    print(e)
    print("One or more variables missing or have error. Exiting !")
    sys.exit(1)


for feed_url in feed_urls:
    if db.get_link(feed_url) == None:
        db.update_link(feed_url, "*")


app = Client(":memory:", api_id=api_id, api_hash=api_hash, session_string=bot_token)

def create_feed_checker(feed_url):
    def check_feed():
        FEED = feedparser.parse(feed_url)
        if len(FEED.entries) == 0:
            return
        
        if "fitgirl-repacks" in FEED["href"]:
            entry = FEED.entries[1]
        else:
            entry = FEED.entries[0]

        
        if entry.id != db.get_link(feed_url).link:
            if co[0] < co[1]:
               mirr = cmds[0]
               co[0] += 1
            else:
               mirr = cmds[-1]
               co[1] += 1
            # Needy Changes
                        # ↓ Edit this message as your needs.
            if "eztv" in entry.link:   #For EZTV
                message = f"{mirr} {entry.links[-1]['href']}"
            elif "yts" in entry.link:
                message = f"{mirr} {entry.links[-1]['href']}"
            elif "rarbg" in entry.link:
                message = f"{mirr} {entry.link}"
            elif "watercache" in entry.link:
                message = f"{mirr} {entry.link}"
            elif "limetorrents" in entry.link:
                message = f"{mirr} {entry.links[-1]['href']}"
            elif "etorrent" in entry.link:
                message = f"{mirr} {entry.link}"
            elif "fitgirl-repacks" in entry.link:
                try:
                    text = entry.content["value"]
                    mag = text.find("magnet")
                    end = text.find('"', mag+1)
                    message = f"{mirr} {text[mag:end]} -z"
                except Exception as e:
                    message = f"{mirr} {entry.link}"
                    res = requests.post("https://basedbin.fly.dev/submit", data={"file-upload": "","content": entry, "ext": "json"})
                    li = "https://basedbin.fly.dev/p/" + str(Bs(res.text).title.text) + f'.py'
                    app.send_message(err_id, f"Error in Rss Feed:\n[Entry link]({li})\n"+str(e))
            else:
                message = f"{mirr} {entry.link}"
            try:
                msg = app.send_message(log_channel, message)
                db.update_link(feed_url, entry.id)
                sleep(10)
            except FloodWait as e:
                print(f"FloodWait: {e.x} seconds")
                sleep(e.x)
            except Exception as e:
                print(e)
        else:
            print(f"Checked RSS FEED: {entry.id}")
    return check_feed


scheduler = BackgroundScheduler()
for feed_url in feed_urls:
    feed_checker = create_feed_checker(feed_url)
    scheduler.add_job(feed_checker, "interval", seconds=check_interval, max_instances=max_instances)
scheduler.start()
app.run()
