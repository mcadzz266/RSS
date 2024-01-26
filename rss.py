import os
import sys
import asyncio
import feedparser
from sql import db
from time import sleep, time
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from apscheduler.schedulers.background import BackgroundScheduler


try:
    api_id = int(os.environ["API_ID"])   # Get it from my.telegram.org
    api_hash = os.environ["API_HASH"]   # Get it from my.telegram.org
    feed_urls = list(set(i for i in os.environ["FEED_URLS"].split("|")))  # RSS Feed URL of the site.
    log_channel = int(os.environ["LOG_CHANNEL"])   # Telegram Channel ID where the bot is added and have write permission. You can use group ID too.
    check_interval = int(os.environ.get("INTERVAL", 10))   # Check Interval in seconds.  
    max_instances = int(os.environ.get("MAX_INSTANCES", 3))   # Max parallel instance to be used.
    mirr_cmd = os.environ.get("MIRROR_CMD", "/qbmirror1")    #if you have changed default cmd of mirror bot, replace this.
    sstring = os.environ.get("STR_SESSION", None)
except Exception as e:
    print(e)
    print("One or more variables missing or have error. Exiting !")
    sys.exit(1)


for feed_url in feed_urls:
    if db.get_link(feed_url) == None:
        db.update_link(feed_url, "*")


app = Client("temp", api_id=api_id, api_hash=api_hash, session_string=sstring, in_memory=True)

async def create_feed_checker(feed_url):
    async def check_feed():
        FEED = feedparser.parse(feed_url)
        if len(FEED.entries) == 0:
            return
        entry = FEED.entries[0]
        if entry.id != db.get_link(feed_url).link:
                       # ↓ Edit this message as your needs.
            if "eztv.re" in entry.link:   
                message = f"{mirr_cmd} {entry.torrent_magneturi}"
            elif "yts.mx" in entry.link:
                message = f"{mirr_cmd} {entry.links[1]['href']}"
            elif "rarbg" in entry.link:
                message = f"{mirr_cmd} {entry.link}"
            elif "watercache" in entry.link:
                message = f"{mirr_cmd} {entry.link}"
            elif "limetorrents.pro" in entry.link:
                message = f"{mirr_cmd} {entry.link}"
            elif "etorrent.click" in entry.link:
                message = f"{mirr_cmd} {entry.link}"
            else:
                message = f"{mirr_cmd} {entry.link}"
            try:
                msg = await app.send_message(log_channel, message)
                db.update_link(feed_url, entry.id)
            except FloodWait as e:
                print(f"FloodWait: {e.x} seconds")
                sleep(e.x)
            except Exception as e:
                print(e)
        else:
            print(f"Checked RSS FEED: {entry.id}")
    return check_feed


async def start_feed_checkers():
    tasks = [create_feed_checker(feed_url) for feed_url in feed_urls]
    await asyncio.gather(*tasks)

async def main():
    scheduler = BackgroundScheduler()
    scheduler.add_job(start_feed_checkers, "interval", seconds=check_interval, max_instances=max_instances)
    scheduler.start()
    await start_feed_checkers()  # Run the initial check

    # Run the Pyrogram application
    await app.start()
    while True:
        try:
            sleep(1)  # Sleep to prevent high CPU usage
        except KeyboardInterrupt:
            print("KeyboardInterrupt: Exiting loop")
            break

# Create and run a new event loop
async def run():
    loop = asyncio.get_event_loop()
    await main()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(run())
