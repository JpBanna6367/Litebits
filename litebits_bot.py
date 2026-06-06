#!/usr/bin/env python3
# 🦅 LITEBITS.IO BOT - RENDER READY
# Dev: EAGLE SCRIPT | TG: t.me/eaglescrip

import requests
import time
import random
import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("LiteBits")

BASE_URL = "https://mini.litebits.io"
INIT_DATA = os.environ.get("LITEBITS_INIT", "").strip()

class LiteBits:
    def __init__(self, init_data):
        self.init = init_data
        self.token = None
        self.cookie = ""
        self.headers = {
            "user-agent": "Mozilla/5.0 (Linux; Android 15; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.7778.178 Mobile Safari/537.36 Telegram-Android/12.1.1 (Xiaomi 23076RN4BI; Android 15; SDK 35; AVERAGE)",
            "accept": "application/json, text/plain, */*",
            "accept-language": "en,en-GB;q=0.9,en-US;q=0.8",
            "accept-encoding": "gzip, deflate, br, zstd",
            "sec-ch-ua": '"Chromium";v="148", "Android WebView";v="148", "Not/A)Brand";v="99"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "origin": BASE_URL,
            "x-requested-with": "com.radolyn.ayugram",
            "priority": "u=1, i",
        }

    def new_session(self):
        s = requests.Session()
        return s

    def auth(self):
        session = self.new_session()
        try:
            resp = session.post(
                f"{BASE_URL}/api/auth/telegram/validate",
                json={"initData": self.init},
                headers={
                    **self.headers,
                    "content-type": "application/json",
                    "referer": f"{BASE_URL}/",
                },
                timeout=30
            )
            # Save cookies from auth
            self.cookie = "; ".join([f"{k}={v}" for k, v in session.cookies.items()])

            data = resp.json()
            if data.get("success"):
                self.token = data["token"]
                bal = data.get('user', {}).get('balance', '?')
                log.info(f"✅ Login OK | Balance: {bal} STOSHI")
                return True
            log.warning(f"❌ Login failed: {data}")
            return False
        except Exception as e:
            log.error(f"Auth error: {e}")
            return False

    def claim(self):
        session = self.new_session()
        time.sleep(random.uniform(1, 3))

        try:
            claim_headers = {
                **self.headers,
                "authorization": f"Bearer {self.token}",
                "content-type": "application/json",
                "referer": f"{BASE_URL}/?v5",
            }
            if self.cookie:
                claim_headers["cookie"] = self.cookie

            payload = {
                "h-captcha-response": "",
                "captchaProvider": "hcaptcha",
                "tapTimings": [],
                "fingerprint": ""
            }

            log.info(f"📤 Sending claim payload: {payload}")

            resp = session.post(
                f"{BASE_URL}/api/claim/start",
                json=payload,
                headers=claim_headers,
                timeout=30
            )

            log.info(f"📥 Claim start response: {resp.text[:200]}")
            data = resp.json()

            if not data.get("success") or not data.get("claimId"):
                log.warning(f"⚠️ Claim start failed: {data}")
                return None

            claim_id = data["claimId"]
            wait = random.randint(15, 17)
            log.info(f"📺 Watching ad... {wait}s")
            time.sleep(wait)

            resp = session.post(
                f"{BASE_URL}/api/claim/{claim_id}/complete",
                json={},
                headers={
                    **claim_headers,
                    "content-length": "2",
                },
                timeout=30
            )

            log.info(f"📥 Complete response: {resp.text[:200]}")
            data = resp.json()

            if data.get("success"):
                reward = data.get("reward", 0)
                log.info(f"✨ REWARD: {reward} STOSHI")
                return reward

            log.warning(f"⚠️ Claim complete failed: {data}")
            return None

        except Exception as e:
            log.error(f"Claim error: {e}")
            return None

    def run(self):
        log.info("🦅 LiteBits Bot starting...")

        if not INIT_DATA:
            log.error("❌ LITEBITS_INIT env var not set!")
            sys.exit(1)

        if not self.auth():
            log.error("❌ Auth failed, exiting.")
            sys.exit(1)

        claim_count = 0
        total_earned = 0

        while True:
            claim_count += 1
            log.info(f"--- Claim #{claim_count} ---")
            result = self.claim()

            if result:
                total_earned += result
                log.info(f"💰 Total earned: {total_earned} STOSHI")
            else:
                log.warning("✗ Claim failed, will retry after cooldown")
                log.info("🔄 Re-authenticating...")
                self.auth()

            cd = random.randint(290, 310)
            log.info(f"⏳ Next claim in {cd//60}m {cd%60}s")
            time.sleep(cd)


if __name__ == "__main__":
    bot = LiteBits(INIT_DATA)
    bot.run()
  
