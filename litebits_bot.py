#!/usr/bin/env python3
# 🦅 FISHVERSE AUTO BOT - RENDER READY
# Dev: EAGLE SCRIPT | TG: t.me/eaglescrip

import requests
import uuid
import hashlib
import time
import random
import json
import os
import sys
import logging
from urllib.parse import unquote

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("Fishverse")

INIT_DATA = os.environ.get("FISH_INIT", "").strip()

class Fishverse:
    def __init__(self, init_data):
        self.base = "https://api.fishverse.site/api"
        self.init = init_data
        self.device_id = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:64].upper()

        decoded = unquote(init_data)
        try:
            s = decoded.find('{"id"')
            e = decoded.find('}', decoded.find('photo_url')) + 1
            self.user = json.loads(decoded[s:e])
        except:
            self.user = {}

        self.headers = {
            "Content-Type": "application/json",
            "Origin": "https://fishverse.site",
            "Referer": "https://fishverse.site/",
            "User-Agent": "Mozilla/5.0 (Linux; Android 15; K) Telegram-Android/12.2.11 (Xiaomi 23076RN4BI; Android 15; SDK 35; AVERAGE)",
            "Authorization": f"Bearer {init_data}",
            "X-Requested-With": "org.telegram.messenger.web"
        }

    def auth(self):
        r = requests.post(f"{self.base}/auth",
                         json={"initData": self.init, "start_param": None, "device_id": self.device_id},
                         headers=self.headers)
        return r.json()

    def get_tasks(self):
        return requests.get(f"{self.base}/tasks", headers=self.headers).json()

    def complete_task(self, task_id):
        return requests.post(f"{self.base}/tasks/complete",
                            json={"task_id": task_id}, headers=self.headers).json()

    def ad_notify(self, block_id):
        requests.post("https://fishverse.site/api/user/ad-click-notify",
                     json={"userId": int(self.user.get("id", 0)),
                           "username": self.user.get("username", ""),
                           "firstName": self.user.get("first_name", ""),
                           "blockId": block_id,
                           "timezone": "Asia/Calcutta"},
                     headers={**self.headers, "X-Requested-With": "org.telegram.messenger.web"})

    def watch_adsgram(self, block_id, slot_index):
        log.info("📺 Watching AdsGram Ad...")
        session = requests.post(f"{self.base}/ads/issue-session",
                               json={"context": "task_watch"}, headers=self.headers).json()
        if not session.get("ok"):
            return None
        st = int(time.time() * 1000)
        wait = random.randint(12, 15)
        log.info(f"⏳ Watching... {wait}s")
        time.sleep(wait)
        self.ad_notify(block_id)
        return requests.post(f"{self.base}/tasks/claim-ad", json={
            "type": "adsgram", "clicked": True, "watch_start_ms": st,
            "slot_index": slot_index, "session_token": session["session_token"],
            "category": "task_watch", "block_id": block_id
        }, headers=self.headers).json()

    def watch_monetag(self, slot_index):
        log.info("📺 Watching Monetag Ad...")
        session = requests.post(f"{self.base}/ads/issue-session",
                               json={"context": "task_watch"}, headers=self.headers).json()
        if not session.get("ok"):
            return None
        st = int(time.time() * 1000)
        wait = random.randint(12, 15)
        log.info(f"⏳ Watching... {wait}s")
        time.sleep(wait)
        self.ad_notify("31041")
        return requests.post(f"{self.base}/tasks/claim-ad", json={
            "type": "monetag", "clicked": True, "watch_start_ms": st,
            "slot_index": slot_index, "category": "task_watch"
        }, headers=self.headers).json()

    def watch_monetix(self, slot_index):
        log.info("📺 Watching Monetix Ad...")
        watch_time = random.randint(15, 17)
        log.info(f"⏳ Watching... {watch_time}s")
        time.sleep(watch_time)
        st = int(time.time() * 1000) - (watch_time * 1000)
        return requests.post(f"{self.base}/tasks/claim-monetix", json={
            "task_id": "task_1780057810372",
            "watch_start_ms": st,
            "slot_index": slot_index
        }, headers=self.headers).json()

    def run(self):
        log.info("🦅 Fishverse Bot starting...")

        if not INIT_DATA:
            log.error("❌ FISH_INIT env var not set!")
            sys.exit(1)

        auth = self.auth()
        if not auth.get("ok"):
            log.error(f"❌ Login Failed: {auth}")
            sys.exit(1)

        user = auth['user']
        log.info(f"✅ Login OK | Balance: {user['balance']} eggs")

        # Partner tasks
        tasks = self.get_tasks()
        partner_tasks = [t for t in tasks.get("tasks", []) if t["type"] == "partner" and not t.get("done")]
        for task in partner_tasks:
            log.info(f"📋 Partner Task: {task.get('title', task['id'])}")
            result = self.complete_task(task["id"])
            if result.get("ok"):
                log.info(f"✨ +{result.get('reward_eggs', 0)} FISH | Partner task done")
            time.sleep(random.randint(5, 8))

        ad_count = 0

        while True:
            tasks = self.get_tasks()
            if not tasks.get("ok"):
                log.error("Failed to get tasks, retrying in 60s...")
                time.sleep(60)
                continue

            # AdsGram
            for t in tasks["tasks"]:
                if t["id"] == "task_ad_adsgram_interstitial" and t.get("remaining", 0) > 0:
                    slot = t["ad_limit"] - t["remaining"]
                    r = self.watch_adsgram(t.get("ad_block_id", ""), slot)
                    if r and r.get("ok"):
                        ad_count += 1
                        log.info(f"✨ +{r.get('reward_eggs', 5)} FISH | AdsGram #{ad_count}")
                    time.sleep(random.randint(3, 6))

            # Monetag
            for t in tasks["tasks"]:
                if t["id"] == "task_ad_monetag" and t.get("remaining", 0) > 0:
                    slot = t["ad_limit"] - t["remaining"]
                    r = self.watch_monetag(slot)
                    if r and r.get("ok"):
                        ad_count += 1
                        log.info(f"✨ +{r.get('reward_eggs', 5)} FISH | Monetag #{ad_count}")
                    time.sleep(random.randint(3, 6))

            # Monetix
            for t in tasks["tasks"]:
                if t["id"] == "task_1780057810372" and t.get("remaining", 0) > 0:
                    slot = t.get("ad_limit", 20) - t.get("remaining", 0)
                    r = self.watch_monetix(slot)
                    if r and r.get("ok"):
                        ad_count += 1
                        reward = r.get('reward', r.get('reward_eggs', 8))
                        log.info(f"✨ +{reward} FISH | Monetix #{ad_count}")
                    time.sleep(random.randint(3, 6))

            # Cooldown every 5 ads
            if ad_count % 5 == 0 and ad_count > 0:
                cd = random.randint(180, 300)
                log.info(f"⏳ Cooldown {cd}s...")
                time.sleep(cd)
                log.info("✅ Cooldown done! Resuming...")

            remaining_all = sum(
                t.get("remaining", 0) for t in tasks["tasks"]
                if t["id"] in ["task_ad_adsgram_interstitial", "task_ad_monetag", "task_1780057810372"]
            )
            if remaining_all == 0:
                log.info("🛑 All Ads Watched! Waiting 1 hour...")
                time.sleep(3600)
                ad_count = 0


if __name__ == "__main__":
    bot = Fishverse(INIT_DATA)
    bot.run()
  
