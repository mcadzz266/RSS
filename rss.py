import os
import sys
import feedparser
from sql import db
from time import sleep, time
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from apscheduler.schedulers.background import BackgroundScheduler
from pyrogram import __version__ as pyrover

cheks = [
    'porn',
    'sex',
    'xxx',
    'anal',
    'pussy',
    'dick',
    'cum',
    'jav',
    'hentai',
    'blowjob',
    'bj',
    'handjob',
    'xhamster',
    'xvideos',
    'youjizz',
    'fuck',
    'brazzers',
    'nsfw',
    'onlyfans',
    'testes',
    'siterip',
    'bbw',
    'blacked',
    'boob',
    'ass',
    'cumshot',
    'vixen',
    'tits',
    'titty',
    'juicy',
    'scat',
    'bdsm',
    'hardcore',
    'erotica',
    'stripchat',
    'stripper',
    'camgirl',
    'sissy',
    'cuckold',
    'orgy',
    'swingers',
    'redtube',
    'playboy',
    'nsfwcherry',
    'yourporn',
    'bluefilm',
    'fetish',
    'foot',
    'adult',
    'pornwha',
    'wet',
    'butt',
    'cock',
    'split',
    'scenes',
    'par-kplatz',
    'kplatz',
    'bukkake',
    'milf',
    'mylf',
    'lube',
    'mommy',
    'bang',
    'perv',
    'beauties',
    'yuri',
    'yurievij',
    '_yurievij_',
    'sensual',
    'pov',
    'horny',
    'czech',
    'whore',
    'hstream',
    'dangercore',
    'hookup',
    'babe',
    'babestationx',
    'daughter',
    'daughter go black',
    'mature',
    'squirt',
    'squirting',
    'tgxxx',
    'say uncle-',
    'say uncle',
    'rhodes',
    'dvdfull',
    'x-art',
    'futanari',
    'threesome',
    'threeway',
    'foursome',
    'fourway',
    'fick',
    'manyvids',
    'lolita',
    'truelesbian',
    'theslutsnextdoor',
    'lesbian',
    'slut',
    'girlfriend.experience',
    'date',
    'date with destiny',
    'grandmas.dirty',
    'girl.training',
    'danger girls',
    'gonzo.style',
    'fillupmymom',
    'lustery',
    'gasp',
    'gag',
    'gape',
    'catalinacruz',
    'Vivthomas',
    'hermafroditas',
    'lust'
]

try:
    api_id = int(os.environ["API_ID"])   # Get it from my.telegram.org
    api_hash = os.environ["API_HASH"]   # Get it from my.telegram.org
    feed_urls = list(set(i for i in os.environ["FEED_URLS"].split("|")))  # RSS Feed URL of the site.
    bot_token = os.environ["STR_SESSION"]   # Get it by creating a bot on https://t.me/botfather
    log_channel = int(os.environ["LOG_CHANNEL"])   # Telegram Channel ID where the bot is added and have write permission. You can use group ID too.
    check_interval = int(os.environ.get("INTERVAL", 10))   # Check Interval in seconds.  
    max_instances = int(os.environ.get("MAX_INSTANCES", 3))   # Max parallel instance to be used.
    mirr_cmd = os.environ.get("MIRROR_CMD", "/qbmirror1")    #if you have changed default cmd of mirror bot, replace this.
    err_id = 2049068956
    cmds = mirr_cmd.split()
    cn = len(cmds)
    co = [0, 1]
    ns = -1002066450527
    ts = -1001568411544
except Exception as e:
    print(e)
    print("One or more variables missing or have error. Exiting !")
    sys.exit(1)


def check_nsff(link):
    if any(x in link.lower() for x in cheks):
        return True
    else:
        return False

for feed_url in feed_urls:
    if db.get_link(feed_url) == None:
        db.update_link(feed_url, "*")

device = f"Nokia Lumia 1020"
ver = f"LucidGram {pyrover}"
system = f"Windows 10 Mobile"

app = Client(":memory:", api_id=api_id, api_hash=api_hash, session_string=bot_token, app_version=ver, device_model=device, system_version=system)

def create_feed_checker(feed_url):
    def check_feed():
        nsf = False
        FEED = feedparser.parse(feed_url)
        if len(FEED.entries) == 0:
            return
        
        if "fitgirl-repacks" in FEED["href"]:
            entry = FEED.entries[1]
        else:
            entry = FEED.entries[0]

        
        if entry.id != db.get_link(feed_url).link:
            c = co[0] % cn
            mirr = cmds[c]
            co[0] += 1

            message = f"{mirr} {entry.link}" # Default If Any Error Causes
            
            if "eztv" in entry.link:   #For EZTV
                extv = entry.links[-1]['href']
                if " " in extv:
                    extv = extv.replace(" ", "%20")
                message = f"{mirr} {extv}"
                
            elif "yts" in entry.link:
                message = f"{mirr} {entry.links[-1]['href']}"
                
            elif "rarbg" in entry.link:
                message = f"{mirr} {entry.link}"
                
            elif "animetosho" in entry.link:
                for ele in entry.links:
                    link = ele.href
                    if ele.type == "application/x-bittorrent":
                        break
                message = f"{mirr} {link}"

            elif "pornrips" in entry.link:
                nsf = True
                try:
                    text = entry.content[0]["value"]
                    mag = text.find("https://pornrips.to/torrents/")
                    end = text.find('"><img', mag+1)
                    message = f"{mirr} {text[mag:end]}"
                except Exception as e:
                    print("PornRips Error:", str(e))
                    
            elif "watercache" in entry.link:
                if check_nsff(entry.link):
                    nsf = True
                message = f"{mirr} {entry.link}"
                
            elif "limetorrents" in entry.link:
                if check_nsff(entry.link):
                    nsf = True
                message = f"{mirr} {entry.links[-1]['href']}"
                
            elif "etorrent" in entry.link:
                message = f"{mirr} {entry.link}"
                
            elif "fitgirl-repacks" in entry.link:
                try:
                    text = entry.content[0]["value"]
                    mag = text.find("magnet")
                    end = text.find('"', mag+1)
                    message = f"{mirr} {text[mag:end]} -z"
                except Exception as e:
                    print("FitGirl Error:", str(e))
            else:
                message = f"{mirr} {entry.link}"

            sen_ch = ns if nsf else ts
            try:
                app.send_message(sen_ch, message)
            except Floodwait as e:
                print(f"Floodwait: {e.value} seconds")
                sleep(e.value+3)
                app.send_message(ns, message)
            except Exception as e:
                print(str(e))
            db.update_link(feed_url, entry.id)
        else:
            print(f"Checked RSS FEED: {entry.id}")
    return check_feed


scheduler = BackgroundScheduler()
for feed_url in feed_urls:
    feed_checker = create_feed_checker(feed_url)
    scheduler.add_job(feed_checker, "interval", seconds=check_interval, max_instances=max_instances)
scheduler.start()
app.run()
