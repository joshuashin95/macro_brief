# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

"""
main.py

Entry point. Generates the macro briefing and sends it to Discord.

Usage:
    python main.py                  # run once immediately
    python main.py --schedule 07:00 # run daily at 07:00 KST
"""

import asyncio
import argparse
import schedule
import time
from agent.briefing import generate
from bot.discord_bot import post_briefing
from utils.config import DISCORD_CHANNEL_ID


def run():
    print("Generating macro briefing...")
    briefing = generate()
    print("\n--- BRIEFING ---")
    print(briefing)
    print("--- SENDING TO DISCORD ---")
    asyncio.run(post_briefing(int(DISCORD_CHANNEL_ID), briefing))
    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", type=str, help="Daily run time e.g. 07:00")
    args = parser.parse_args()

    if args.schedule:
        print(f"Scheduled to run daily at {args.schedule}")
        schedule.every().day.at(args.schedule).do(run)
        while True:
            schedule.run_pending()
            time.sleep(30)
    else:
        run()
