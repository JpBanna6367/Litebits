#!/usr/bin/env python3
# 🦅 LITEBITS.IO BOT - RENDER READY
# Dev: EAGLE SCRIPT | TG: t.me/eaglescrip

import requests
import json
import time
import random
import os
import sys
import logging

# ===== LOGGING SETUP =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("LiteBits")

BASE_URL = "https://mini.litebits.io"

# ===== CONFIG FROM ENV =====
INIT_DATA = os.environ.get("LITEBITS_INIT", "").strip()
PROXY_STR  = os.environ.get("PROXY", "http://kcartik:kcartik@chill-ki-mutt.kcartik-vps.tech:22425").strip()

def get_proxy():
    if not PROXY_STR:
        return None
    return {
        "http":  PROXY_STR,
        "https": PROXY_STR,
    }

class LiteBits:
    def __init__(self, init_data):
        self.init = init_data
        self.token = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 15; K) AppleWebKit/537.36 Chrome/148.0.7778.178 Mobile Safari/537.36 Telegram-Android/12.1.1",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Origin": BASE_URL,
            "X-Requested-With": "com.radolyn.ayugram",
        }

    def new_session(self):
        s = requests.Session()
        proxy = get_proxy()
        if proxy:
            s.proxies.update(proxy)
        return s

    def auth(self):
        session = self.new_session()
        try:
            resp = session.post(
                f"{BASE_URL}/api/auth/telegram/validate",
                json={"initData": self.init},
                headers={**self.headers, "Content-Type": "application/json", "Referer": f"{BASE_URL}/"},
                timeout=30
            )
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

        x = random.randint(250, 320)
        y = random.randint(420, 480)

        try:
            resp = session.post(
                f"{BASE_URL}/api/claim/start",
                json={
                    "h-captcha-response": "",
                    "captchaProvider": "hcaptcha",
                    "tapTimings": [{"delay": 0, "x": x, "y": y}],
                    "fingerprint": ""
                },
                headers={
                    **self.headers,
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                    "Referer": f"{BASE_URL}/"
                },
                timeout=30
            )

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
                    **self.headers,
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                    "Referer": f"{BASE_URL}/"
                },
                timeout=30
            )

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
        log.info(f"🔌 Proxy: {PROXY_STR[:30]}..." if PROXY_STR else "🔌 Proxy: None")

        if not INIT_DATA:
            log.error("❌ LITEBITS_INIT env var not set! Set it in Render environment variables.")
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
                # Re-auth on failure
                log.info("🔄 Re-authenticating...")
                self.auth()

            cd = random.randint(290, 310)
            log.info(f"⏳ Next claim in {cd//60}m {cd%60}s")
            time.sleep(cd)


if __name__ == "__main__":
    bot = LiteBits(INIT_DATA)
    bot.run()
          
