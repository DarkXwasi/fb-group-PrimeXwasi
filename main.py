#!/usr/bin/env python3
import logging
import time
from modules.utils import load_config
from modules.fb_client import FBClient
from modules.group_actions import engage_group

# load config once to get log file name
cfg = load_config()
logfile = cfg.get("settings", {}).get("log_file", "fb-bot.log")

# Logging: console + file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),                    # prints to console
        logging.FileHandler(logfile, encoding="utf-8")  # writes to file
    ]
)
logger = logging.getLogger("fb-reach-bot")

def run():
    cfg = load_config()  # reload in case user edited while running
    accounts = cfg.get("accounts", [])
    groups = cfg.get("groups", [])
    settings = cfg.get("settings", {})

    if not accounts:
        logger.error("No accounts found in config.json")
        return

    for acc in accounts:
        if not acc.get("active", True):
            logger.info(f"Skipping inactive account {acc.get('uid')}")
            continue
        uid = acc.get("uid")
        cookie = acc.get("cookie")
        if not cookie:
            logger.warning(f"No cookie for account {uid}, skipping")
            continue

        logger.info(f"=== Using account {uid} ===")
        client = FBClient(cookie, user_agent=settings.get("user_agent"))
        for g in groups:
            gid = g.get("id")
            comments = g.get("comment_texts", [])
            reactions = g.get("reactions", [])
            logger.info(f"[Group {gid}] Engaging...")
            try:
                engage_group(client, gid, comments, reactions, settings, logger)
            except Exception as e:
                logger.exception(f"Exception while engaging group {gid}: {e}")
            # small pause between groups
            time.sleep(2)

if __name__ == "__main__":
    run()