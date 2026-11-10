# Telegram control bot for Free Fire friend management.
# Configure BOT_TOKEN and ADMIN_TELEGRAM_ID before running.
# Uses the existing bot_core.py functions and persists expiration times in friends_timers.json.

import asyncio
import json
import os
import re
import time
from pathlib import Path

import aiohttp
import bot_core

BOT_TOKEN = "9185257645:AAHhtbuAkleDJXOmwEgU3GyZJ9LGyylY0LY"
ADMIN_TELEGRAM_ID = 6785344207  # Admin Telegram user ID

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"
TIMERS_FILE = Path(__file__).with_name("friends_timers.json")
MIN_UID_LENGTH = 5
MAX_UID_LENGTH = 15
DEFAULT_HOURS = 24
MAX_DURATION_SECONDS = 365 * 24 * 60 * 60

# uid -> {"expires_at": unix timestamp, "requested_by": Telegram user ID}
_timers = {}
_timer_lock = asyncio.Lock()


def _load_timers():
    global _timers
    try:
        raw = json.loads(TIMERS_FILE.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            _timers = {str(uid): data for uid, data in raw.items()
                       if str(uid).isdigit() and isinstance(data, dict)
                       and isinstance(data.get("expires_at"), (int, float))}
    except FileNotFoundError:
        _timers = {}
    except Exception as exc:
        print(f"[Timers] Could not read timer file: {type(exc).__name__}")
        _timers = {}


def _save_timers():
    tmp = TIMERS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(_timers, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(TIMERS_FILE)


def _parse_duration(value):
    """Accept 24h, 3d, 90m, or a bare number interpreted as hours."""
    match = re.fullmatch(r"(\d+)([mhd]?)", value.lower())
    if not match:
        return None
    amount = int(match.group(1))
    unit = match.group(2) or "h"
    multiplier = {"m": 60, "h": 3600, "d": 86400}[unit]
    seconds = amount * multiplier
    if seconds < 60 or seconds > MAX_DURATION_SECONDS:
        return None
    return seconds


def _valid_uid(uid):
    return uid.isdigit() and MIN_UID_LENGTH <= len(uid) <= MAX_UID_LENGTH


async def _telegram_call(session, method, payload=None):
    async with session.post(f"{API_BASE}/{method}", json=payload or {}) as response:
        data = await response.json(content_type=None)
        if response.status != 200 or not data.get("ok"):
            raise RuntimeError(f"Telegram API error ({response.status})")
        return data["result"]


async def _send_text(session, chat_id, text):
    await _telegram_call(session, "sendMessage", {"chat_id": chat_id, "text": text})


async def _game_ready():
    token = getattr(bot_core, "ToKen", None)
    region = getattr(bot_core, "region", None)
    return token, region


async def _schedule_removal(uid, duration_seconds, requested_by):
    async with _timer_lock:
        _timers[str(uid)] = {
            "expires_at": time.time() + duration_seconds,
            "requested_by": int(requested_by),
        }
        _save_timers()


async def _cancel_timer(uid):
    async with _timer_lock:
        existed = _timers.pop(str(uid), None) is not None
        _save_timers()
        return existed


async def _expiry_worker(session):
    """Remove expired players; timers survive process restarts."""
    while True:
        await asyncio.sleep(5)
        now = time.time()
        async with _timer_lock:
            expired = [uid for uid, data in _timers.items()
                       if float(data.get("expires_at", 0)) <= now]
        if not expired:
            continue
        token, region = await _game_ready()
        if not token or not region:
            continue  # Retry after game connection becomes ready.
        for uid in expired:
            try:
                ok, message = await bot_core.remove_friend(uid, token, region)
            except Exception as exc:
                ok, message = False, type(exc).__name__
            if ok:
                async with _timer_lock:
                    _timers.pop(uid, None)
                    _save_timers()
                print(f"[Timers] Expired friend removed: {uid}")
            else:
                # Retry later, and do not silently discard the timer.
                print(f"[Timers] Removal failed for {uid}: {message}")


async def _handle_message(session, message):
    chat = message.get("chat", {})
    sender = message.get("from", {})
    text = (message.get("text") or "").strip()
    if not text.startswith("/") or chat.get("type") != "private":
        return

    chat_id = chat.get("id")
    sender_id = sender.get("id")
    parts = text.split()
    command = parts[0].split("@", 1)[0].lower()
    is_admin = sender_id == ADMIN_TELEGRAM_ID

    
    if command == "/start":
        await _send_text(session, chat_id,
            "⚔️ WELCOME TO GHIDRA HEX BOT ⚔️\n\n🤖 أوامر البوت :\n👾 للمستخدم :\n/request <uid>\n🔴 مثال :\n /request 12345678\n 💬 ملاحظه : سيتم حذف الاعب بعد مرور 24 ساعه من أضافته للبوت\n\n👾 للأدمن :\n/add <uid> <time>\n🔴 مثال :\n/add 12345678 1d\n💬 ملاحظه : سيتم حذف الاعب بعد مرور الوقت المحدد من أضافته للبوت\n\n🤖 مطورين البوت :\nAH HEX BOT ⚔️\nREVIL HEX BOT ⚔️")
        return    

    # Any user may request the standard 24-hour flow; admin can choose a duration.
    if command == "/request":
        if len(parts) != 2 or not _valid_uid(parts[1]):
            await _send_text(session, chat_id, "❌ الاستخدام :\n /request <uid>\n🔴 مثال :\n/request 12345678")
            return
        uid, duration = parts[1], DEFAULT_HOURS * 3600
    elif command == "/add":
        if not is_admin:
            await _send_text(session, chat_id, "⛔ هذا الأمر للأدمن فقط")
            return
        if len(parts) != 3 or not _valid_uid(parts[1]):
            await _send_text(session, chat_id, "❌ الاستخدام :\n/add <uid> 24h أو /add <uid> 3d\n🔴 مثال :\n/add 12345678 24h أو /add 12345678 3d")
            return
        duration = _parse_duration(parts[2])
        if duration is None:
            await _send_text(session, chat_id, "❌ مدة غير صحيحة. استخدم مثلًا 30m أو 24h أو 3d (حد أقصى سنة).")
            return
        uid = parts[1]
    elif command == "/remove":
        if not is_admin:
            await _send_text(session, chat_id, "⛔ هذا الأمر للأدمن فقط.")
            return
        if len(parts) != 2 or not _valid_uid(parts[1]):
            await _send_text(session, chat_id, "❌ الاستخدام :\n/remove UID\n🔴 مثال :\n/remove 12345678")
            return
        token, region = await _game_ready()
        if not token or not region:
            await _send_text(session, chat_id, "⏳ اتصال اللعبة غير جاهز؛ جرّب بعد قليل.")
            return
        try:
            ok, result = await bot_core.remove_friend(parts[1], token, region)
            if ok:
                await _cancel_timer(parts[1])
            await _send_text(session, chat_id, ("✅ " if ok else "❌ ") + str(result))
        except Exception as exc:
            await _send_text(session, chat_id, f"❌ فشلت العملية: {type(exc).__name__}")
        return
    elif command == "/list":
        if not is_admin:
            await _send_text(session, chat_id, "⛔ هذا الأمر للأدمن فقط.")
            return
        async with _timer_lock:
            items = list(_timers.items())
        if not items:
            await _send_text(session, chat_id, "❌ لا يوجد لاعبون بمؤقت حاليًا.")
            return
        lines = ["المؤقتات الحالية:"]
        for uid, data in sorted(items):
            remaining = max(0, int(float(data["expires_at"]) - time.time()))
            hours, rem = divmod(remaining, 3600)
            minutes = rem // 60
            lines.append(f"{uid} — متبقي {hours}س {minutes}د")
        await _send_text(session, chat_id, "\n".join(lines))
        return
    else:
        return

    token, region = await _game_ready()
    if not token or not region:
        await _send_text(session, chat_id, "⏳ اتصال اللعبة غير جاهز؛ جرّب بعد قليل.")
        return

    await _send_text(session, chat_id, "⏳ جارٍ إرسال طلب الصداقة ...")
    try:
        ok, result = await bot_core.send_friend_request(uid, token, region)
        if ok:
            await _schedule_removal(uid, duration, sender_id)
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            duration_text = f"{hours} ساعة" if hours and not minutes else (f"{hours} ساعة و{minutes} دقيقة" if hours else f"{minutes} دقيقة")
            await _send_text(session, chat_id,
                f"✅ تم إرسال طلب الصداقة إلى {uid}.\n"
                f"تم ضبط الحذف التلقائي بعد {duration_text} إذا كان اللاعب ضمن الأصدقاء وقتها")
        else:
            await _send_text(session, chat_id, f"❌ {result}")
    except Exception as exc:
        await _send_text(session, chat_id, f"❌ فشلت العملية: {type(exc).__name__}")


async def run_bot():
    if BOT_TOKEN == "PASTE_YOUR_TELEGRAM_BOT_TOKEN_HERE":
        raise RuntimeError("ضع توكن بوت تيليجرام في BOT_TOKEN داخل telegram_bot.py")
    if not isinstance(ADMIN_TELEGRAM_ID, int) or ADMIN_TELEGRAM_ID <= 0:
        raise RuntimeError("ضع رقم Telegram ID الصحيح في ADMIN_TELEGRAM_ID")

    _load_timers()
    timeout = aiohttp.ClientTimeout(total=40)
    offset = None
    async with aiohttp.ClientSession(timeout=timeout) as session:
        expiry_task = asyncio.create_task(_expiry_worker(session))
        print("[Telegram] Polling started.")
        try:
            while True:
                try:
                    params = {"timeout": 25}
                    if offset is not None:
                        params["offset"] = offset
                    updates = await _telegram_call(session, "getUpdates", params)
                    for update in updates:
                        offset = update["update_id"] + 1
                        message = update.get("message")
                        if message:
                            await _handle_message(session, message)
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    print(f"[Telegram] Error: {type(exc).__name__}; retrying in 5 seconds.")
                    await asyncio.sleep(5)
        finally:
            expiry_task.cancel()
            try:
                await expiry_task
            except asyncio.CancelledError:
                pass


if __name__ == "__main__":
    asyncio.run(run_bot())
