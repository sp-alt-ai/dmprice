from __future__ import annotations

import json
import os
import sys
import time

import requests
import websocket

from keep_alive import keep_alive

status = "online" #online/dnd/idle

GUILD_ID = os.getenv("GUILD_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")

def _env_bool(name: str, default: bool = False) -> bool:
  raw = os.getenv(name)
  if raw is None:
    return default
  return raw.strip().lower() in {"1", "true", "yes", "y", "on"}

SELF_MUTE = _env_bool("SELF_MUTE", False)
SELF_DEAF = _env_bool("SELF_DEAF", False)

usertoken = os.getenv("TOKEN")
if not usertoken:
  print("[ERROR] Please add a token inside Secrets.")
  sys.exit()

headers = {"Authorization": usertoken, "Content-Type": "application/json"}

validate = requests.get("https://discord.com/api/v10/users/@me", headers=headers, timeout=20)
if validate.status_code != 200:
  print("[ERROR] Your token might be invalid. Please check it again.")
  sys.exit()

userinfo = validate.json()
username = userinfo["username"]
discriminator = userinfo["discriminator"]
userid = userinfo["id"]

def joiner(token, status):
    ws = websocket.WebSocket()
    ws.connect("wss://gateway.discord.gg/?v=10&encoding=json", timeout=20)
    start = json.loads(ws.recv())  # HELLO
    heartbeat_ms = start["d"]["heartbeat_interval"]

    auth = {
      "op": 2,
      "d": {
        "token": token,
        "properties": {"$os": "Windows", "$browser": "Chrome", "$device": "Windows"},
        "presence": {"status": status, "afk": False},
      },
    }
    vc = {
      "op": 4,
      "d": {
        "guild_id": GUILD_ID,
        "channel_id": CHANNEL_ID,
        "self_mute": SELF_MUTE,
        "self_deaf": SELF_DEAF,
      },
    }

    ws.send(json.dumps(auth))
    ws.send(json.dumps(vc))

    # Keep the connection alive for a bit, then allow reconnect loop.
    heartbeat_s = max(1.0, heartbeat_ms / 1000.0)
    end_time = time.time() + 60
    while time.time() < end_time:
      ws.send(json.dumps({"op": 1, "d": None}))
      time.sleep(heartbeat_s)
    ws.close()

def run_joiner():
  os.system("cls" if os.name == "nt" else "clear")
  print(f"Logged in as {username}#{discriminator} ({userid}).")
  while True:
    joiner(usertoken, status)
    time.sleep(30)

keep_alive()
run_joiner()