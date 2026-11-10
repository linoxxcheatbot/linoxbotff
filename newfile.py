# -*- coding: utf-8 -*-
import os
import time
import random
import json
import codecs
import signal
import threading
import requests
import hmac
import hashlib
import sys
import uuid
import struct
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as _pad
from cryptography.hazmat.backends import default_backend
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def pad(data, bs):
    p = _pad.PKCS7(bs * 8).padder()
    return p.update(data) + p.finalize()

class AES:
    MODE_CBC = 2
    block_size = 16
    @staticmethod
    def new(key, mode, iv):
        class C:
            def __init__(self, k, i):
                self.k, self.i = k, i
            def encrypt(self, data):
                c = Cipher(algorithms.AES(self.k), modes.CBC(self.i), backend=default_backend()).encryptor()
                return c.update(data) + c.finalize()
        return C(key, iv)

EXIT = False
SUCCESS_COUNT = 0
LOCK = threading.Lock()
ACCOUNTS_FILE = "ac.json"
API_HEX_KEY = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
API_SECRET_KEY = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
AES_KEY_G = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV_G = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
REGION_LANG = {
    "BD": "bn", "IND": "hi", "PK": "ur", "SG": "en", "ID": "id",
    "ME": "ar", "VN": "vi", "TW": "zh", "CIS": "ru", "TH": "th",
    "EU": "en", "US": "en", "SAC": "es", "LK": "en", "BR": "pt",
}
Garena = "@meropvp"
THREADS = 10
BATCH_FLUSH = 5

def safe_exit(signum=None, frame=None):
    global EXIT
    EXIT = True
    sys.exit(0)

signal.signal(signal.SIGINT, safe_exit)
signal.signal(signal.SIGTERM, safe_exit)

def encode_varint(n):
    if n < 0:
        return b""
    result = []
    while True:
        byte = n & 0x7F
        n >>= 7
        if n:
            byte |= 0x80
        result.append(byte)
        if not n:
            break
    return bytes(result)

def create_proto_field(field_num, value):
    if isinstance(value, int):
        return encode_varint((field_num << 3) | 0) + encode_varint(value)
    elif isinstance(value, (str, bytes)):
        encoded_val = value.encode() if isinstance(value, str) else value
        return encode_varint((field_num << 3) | 2) + encode_varint(len(encoded_val)) + encoded_val
    return b""

def build_proto(fields):
    return b"".join(create_proto_field(k, v) for k, v in fields.items())

def encrypt_api(plain_hex):
    cipher = AES.new(AES_KEY_G, AES.MODE_CBC, AES_IV_G)
    return cipher.encrypt(pad(bytes.fromhex(plain_hex), AES.block_size)).hex()

def save_account_to_json(account_data):
    try:
        with LOCK:
            accounts = {}
            if os.path.exists(ACCOUNTS_FILE):
                try:
                    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                        if isinstance(existing, dict):
                            accounts = existing
                        elif isinstance(existing, list):
                            for a in existing:
                                uid = str(a.get("uid", ""))
                                pwd = a.get("password", "")
                                if uid and pwd:
                                    accounts[uid] = pwd
                except Exception:
                    accounts = {}
            uid_str = str(account_data["uid"])
            pwd = account_data["password"]
            accounts[uid_str] = pwd
            with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
                json.dump(accounts, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def generate_password():
    return os.urandom(10).hex()

def _pb_varint(n):
    if n < 0:
        n = (1 << 64) + n
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            b |= 0x80
        out.append(b)
        if not n:
            break
    return bytes(out)

def _pb_tag(f, w):
    return _pb_varint((f << 3) | w)

def _pb_field(f, v):
    if isinstance(v, bool):
        v = int(v)
    if isinstance(v, int):
        return _pb_tag(f, 0) + _pb_varint(v)
    if isinstance(v, str):
        d = v.encode('utf-8')
        return _pb_tag(f, 2) + _pb_varint(len(d)) + d
    if isinstance(v, (bytes, bytearray)):
        d = bytes(v)
        return _pb_tag(f, 2) + _pb_varint(len(d)) + d
    return b""

def build_majorlogin_payload(open_id, access_token, lang, client_version="1.132.13"):
    fields = {
        3:  time.strftime("%Y-%m-%d %H:%M:%S"),
        4:  "free fire",
        5:  1,
        7:  str(client_version),
        8:  "Android OS 14 / API-34",
        9:  "Handheld",
        10: "Mobilis",
        11: "WIFI",
        12: 1600,
        13: 900,
        14: "240",
        15: "x86-64 SSE3 SSE4.1 SSE4.2 AVX | 2865 | 6",
        16: 5944,
        17: "Adreno (TM) 750",
        18: "OpenGL ES 3.1 v1",
        19: f"Google|{uuid.uuid4()}",
        20: f"{random.randint(1,223)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        21: lang or "ar",
        22: str(open_id),
        23: "4",
        24: "Handheld",
        25: "samsung SM-N9860",
        26: "ME",
        29: str(access_token),
        30: 1,
        41: "Mobilis",
        42: "WIFI",
        57: "7428b253defc164018c604a1ebbfebdf",
        60: 52691,
        61: 48409,
        62: 2519,
        63: 70,
        64: 23306,
        65: 25131,
        66: 50733,
        67: 52691,
        73: 3,
        74: "/data/app/lib/arm64",
        76: 1,
        77: "b8e0cd5e295eee42f5860d3c86e483dd|/data/app/base.apk",
        78: 3,
        79: 2,
        81: "64",
        83: "2019121229",
        85: 3,
        86: "OpenGLES2",
        87: 8191,
        88: 4,
        89: "KqsHT6dXfrd81vpmdClMMxZM3UCc59ys5/2cX5FVcMpI3tlWy8d0r8ZWGSBj+06/cGbBzY3JULeYT1rb5tBtz7+GCis6kpkGPjl2SSoYhrjsQOvA",
        92: 7303,
        93: "android",
        94: "KqsHT6dXfrd81vpmdClMMxZM3UCc59ys5/2cX5FVcMpI3tlWy8d0r8ZWGSBj+06/cGbBzY3JULeYT1rb5tBtz7+GCis6kpkGPjl2SSoYhrjsQOvA",
        95: 111207,
        96: '{"cur_rate":null,"support_etc2":false}',
        97: 1,
        98: 1,
        99: "4",
        100: "4",
        102: b"",
        104: 62270,
        105: 1,
        106: "https://dl.gmc.freefiremobile.com/live/ABHotUpdates/|https://core-gmc.freefiremobile.com/live/ABHotUpdates/|4a0070ac356973792f002e0b25b96c3b",
        107: "c8e41b7a93f02d56e1a94c7b8203f5d1",
    }

    plain = build_proto(fields)
    cipher = AES.new(AES_KEY_G, AES.MODE_CBC, AES_IV_G)
    return cipher.encrypt(pad(plain, AES.block_size))

def _decode_major_login_response(response_bytes):
    if not response_bytes:
        return None

    def read_varint(buf, off):
        value = 0
        shift = 0
        start = off
        while off < len(buf):
            b = buf[off]
            off += 1
            value |= (b & 0x7f) << shift
            if b < 0x80:
                return value, off - start
            shift += 7
            if shift > 70:
                raise ValueError("varint too long")
        raise ValueError("truncated varint")

    def parse(buf):
        off = 0
        out = {}
        while off < len(buf):
            tag, n = read_varint(buf, off)
            off += n
            field_no, wire = tag >> 3, tag & 7
            if wire == 0:
                value, n = read_varint(buf, off)
                off += n
            elif wire == 2:
                ln, n = read_varint(buf, off)
                off += n
                if off + ln > len(buf):
                    raise ValueError("bad length")
                value = buf[off:off + ln]
                off += ln
            elif wire == 5:
                if off + 4 > len(buf):
                    raise ValueError("bad fixed32")
                value = struct.unpack_from("<I", buf, off)[0]
                off += 4
            elif wire == 1:
                if off + 8 > len(buf):
                    raise ValueError("bad fixed64")
                value = struct.unpack_from("<Q", buf, off)[0]
                off += 8
            else:
                raise ValueError("unsupported wire type")
            out[field_no] = value
        return out

    candidates = [response_bytes]
    candidates.extend(response_bytes[o:] for o in range(1, min(80, len(response_bytes))))

    for candidate in candidates:
        try:
            d = parse(candidate)
            if isinstance(d.get(1), int) and d[1] > 100000:
                def as_text(v):
                    if isinstance(v, bytes):
                        try:
                            return v.decode("utf-8")
                        except Exception:
                            return v.decode("latin1", "ignore")
                    return str(v) if v is not None else ""

                return {
                    "account_uid": int(d.get(1, 0)),
                    "region": as_text(d.get(2, "")),
                    "token": as_text(d.get(8, "")),
                    "url": as_text(d.get(10, "")),
                    "timestamp": int(d.get(21, 0)),
                    "key": d.get(22, b"") if isinstance(d.get(22, b""), bytes) else bytes.fromhex(str(d.get(22, ""))),
                    "iv": d.get(23, b"") if isinstance(d.get(23, b""), bytes) else bytes.fromhex(str(d.get(23, ""))),
                }
        except Exception:
            continue
    return None

def login_generated_account(open_id, access_token, lang):
    try:
        payload = build_majorlogin_payload(open_id, access_token, lang)
        headers = {
            "X-Unity-Version": "2018.4.11f1",
            "ReleaseVersion": "OB55",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-GA": "v1 1",
            "X-GA-SV": "1790794556",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)",
            "Host": "loginbp.ppmainecoonghj.com",
        }
        r = requests.post(
            "https://loginbp.ppmainecoonghj.com/MajorLogin",
            headers=headers, data=payload, verify=False, timeout=15
        )
        if r.status_code != 200:
            return None

        auth = _decode_major_login_response(r.content)
        if not auth or not auth["token"]:
            return None

        base_url = auth["url"] or "https://clientbp.ppmainecoonghj.com"
        if not base_url.startswith("http"):
            base_url = "https://" + base_url
        base_url = base_url.rstrip("/")

        login_data = None
        candidates = [base_url, "https://clientbp.ppmainecoonghj.com"]
        seen = set()
        for host in candidates:
            if host in seen:
                continue
            seen.add(host)
            try:
                rr = requests.post(
                    host + "/GetLoginData",
                    headers={**headers, "Authorization": f"Bearer {auth['token']}"},
                    data=payload, verify=False, timeout=15,
                )
                if rr.status_code == 200 and rr.content:
                    login_data = rr.content
                    base_url = host
                    break
            except Exception:
                continue

        if not login_data:
            return None

        return {
            **auth,
            "url": base_url,
            "login_data": login_data,
            "account_id": str(auth["account_uid"]),
        }
    except Exception:
        return None

def create_account(region, prefix, thread_id):
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            session = requests.Session()
            password = generate_password()
            payload_register = json.dumps(
                {"app_id": 100067, "client_type": 2, "password": password, "source": 2},
                separators=(",", ":"),
            )
            signature = hmac.new(API_SECRET_KEY.encode(), payload_register.encode(), hashlib.sha256).hexdigest()
            headers_reg = {
                "User-Agent": "GarenaMSDK/4.0.44(ASUS ;Android 13;en;%s;app 1.132.1 2019121229;)" % region,
                "Accept": "application/json",
                "Authorization": "Signature %s" % signature,
                "Content-Type": "application/json; charset=utf-8",
                "Host": "100067.connect.garena.com",
            }
            resp_reg = session.post(
                "https://100067.connect.garena.com/api/v2/oauth/guest:register",
                headers=headers_reg, data=payload_register, timeout=12, verify=False,
            )
            if resp_reg.status_code != 200:
                if resp_reg.status_code == 429:
                    time.sleep(2 ** attempt)
                continue
            reg_json = resp_reg.json()
            if reg_json.get("code") != 0:
                continue
            uid = reg_json["data"]["uid"]
            payload_token = json.dumps(
                {
                    "client_id": 100067,
                    "client_secret": API_HEX_KEY,
                    "client_type": 2,
                    "device_id": "02-%s" % hashlib.md5(str(uid).encode()).hexdigest()[:36],
                    "password": password,
                    "response_type": "token",
                    "uid": uid,
                },
                separators=(",", ":"),
            )
            headers_tok = {
                "User-Agent": "GarenaMSDK/4.0.44(ASUS ;Android 13;en;%s;app 1.132.1 2019121229;)" % region,
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
                "Host": "100067.connect.garena.com",
            }
            resp_tok = session.post(
                "https://100067.connect.garena.com/api/v2/oauth/guest/token:grant",
                headers=headers_tok, data=payload_token, timeout=12, verify=False,
            )
            if resp_tok.status_code != 200:
                continue
            tok_json = resp_tok.json()
            if tok_json.get("code") != 0:
                continue
            access_token = tok_json["data"]["access_token"]
            open_id = tok_json["data"]["open_id"]
            keystream = [
                0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x32, 0x30, 0x31, 0x37, 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30, 0x31,
                0x37, 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30,
            ]
            field = codecs.decode(
                "".join(chr(ord(open_id[i]) ^ keystream[i % len(keystream)]) for i in range(len(open_id)))
                .encode("unicode_escape").decode("utf-8"),
                "unicode_escape",
            ).encode("latin1")
            name = "%s%d" % (prefix, random.randint(1, 1000))
            lang = REGION_LANG.get(region.upper(), "en")
            proto_data = build_proto(
                {
                    1: name,
                    2: access_token,
                    3: open_id,
                    5: 102000007,
                    6: 4,
                    7: 1,
                    13: 1,
                    14: field,
                    15: lang,
                    16: 1,
                    20: "1.132.13",
                    21: 1,
                    22: bytes.fromhex('47475245010101005a020000ec9cca11ccc7b243e22f701fe388001d22366c7e307f43b0677c90707263de4d295b423e78bf7951100c0791cfd8c6f3519a12cbcb320f337dcaddd3ecd2d56663bacc72a5c3ba46b055f434bfc9d0d29aaf184cd76b6f1dbe0de1005e672fb5454f7c84fda754fcf55ab8a0e45965cfb352bcca7b3954484ee9b7a917015c44bcbf728881f88ea631f40be96e9e45152941f31c69a2983b69681aabb965070003ae31d5873dec2c9a98ad35f4f0136b76f618e7da1c66c28983458f127863eb7526af26c19e672e7876f9fb6b28b4832a81eeaf1402e97ca5052c4b5ac59a76cd49b52c0fecaa89623260166300555c8cc01f3dd20f4816f9daea279a65d138d5137ec9d62427201c71990ea5b4c17c8bf383e6ba3a6dc40a98ec91501478c77f52c18d24f18c2f260edc0ec665e95ee187f7bb9f0388c9960668b1e501291f0ccaff0347241a91774c77f1013e1dfb6817e028271829078d02191dca66b5f02fcf4b0ec7caa17b23177f8c56c2d773f6162551762cd5cce9249d5a668ec9d2fb47073834d1ef8b0846be5b8782f7ef0309f6a6306e86762b09700e64dea84c3ef9ba34dec48516719b0ef9f85ca81a507e2286699d2abe223a2162464d0c039b987d68cff135d40798e33baf579a773e4fa3f31532f4ea3f886a2cb1873e8fca8f3d91347a5baffabee7aa19fe915192ab95d80b84b41195b1637a05713c7f445aafb7861333d1ca8276d012be3c75b55108bb9814f333df670d0f0628595b59ffbb8732e514572635189dae2ee1e19027695b39fafe83d7b91ea9ea1f95be96df6fbd46b52b0a7a7861a10ef098e51b28327266848eb5234d9c77239b928c3125a44b7452b28905d0d1ac2e0d3029abfd257c3cf5f3dd574091690a49f0ad3f2e')
                }
            )
            encrypted_payload = bytes.fromhex(encrypt_api(proto_data.hex()))
            headers_major = {
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)",
                "X-Unity-Version": "2018.4.11f1",
                "ReleaseVersion": "OB55",
                "Content-Type": "application/x-www-form-urlencoded",
                "X-GA": "v1 1",
                "X-GA-SV": str(int(time.time())),
                "Host": "loginbp.ppmainecoonghj.com",
            }
            session.post(
                "https://loginbp.ppmainecoonghj.com/MajorRegister",
                headers=headers_major, data=encrypted_payload, verify=False, timeout=12,
            )
            login_res = login_generated_account(open_id, access_token, lang)
            if login_res:
                account_id = login_res.get("account_id") or str(login_res.get("account_uid") or "")
                if not account_id:
                    continue
                account_data = {
                    "uid": int(uid),
                    "password": password,
                    "account_id": account_id,
                    "name": name,
                    "region": region,
                    "Telegram": Garena,
                    "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                save_account_to_json(account_data)
                return account_data
        except Exception:
            pass
        time.sleep(0.1)
    return None

def worker(region, prefix, target, thread_id):
    global SUCCESS_COUNT
    while not EXIT:
        with LOCK:
            if SUCCESS_COUNT >= target:
                break
        acc = create_account(region, prefix, thread_id)
        if acc:
            with LOCK:
                if SUCCESS_COUNT >= target:
                    break
                SUCCESS_COUNT += 1
                current = SUCCESS_COUNT
            print(
                "[%d/%d] id=%s | uid=%s | password=%s | name=%s"
                % (current, target, acc["account_id"], acc["uid"], acc["password"], acc["name"])
            )
        else:
            time.sleep(0.1)

def main():
    valid_regions = ["BD", "IND", "PK", "SG", "ID", "ME", "VN", "TW", "CIS", "TH", "EU", "US", "SAC", "LK", "BR"]
    print("TG %s" % Garena)
    print("AVAILABLE: %s" % ", ".join(valid_regions))
    choice = input("SERVER : ").strip().upper()
    if choice not in valid_regions:
        print("Err - invalid server. Choose from: %s" % ", ".join(valid_regions))
        return
    region = choice
    prefix = input("NAME : ").strip()
    try:
        target = int(input("COUNT : "))
    except Exception:
        return

    global THREADS
    try:
        threads_input = input("THREADS [default 10]: ").strip()
        if threads_input:
            THREADS = int(threads_input)
    except Exception:
        THREADS = 10

    print("[i] Region: %s | Prefix: %s | Count: %d | Threads: %d" % (region, prefix, target, THREADS))
    print("[i] Output: %s" % ACCOUNTS_FILE)
    print()

    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=worker, args=(region, prefix, target, i + 1))
        t.daemon = True
        t.start()
        threads.append(t)

    try:
        while any(t.is_alive() for t in threads):
            time.sleep(0.3)
            with LOCK:
                if SUCCESS_COUNT >= target:
                    break
    except KeyboardInterrupt:
        safe_exit()

    print()
    print("[+] DONE — Generated %d accounts" % SUCCESS_COUNT)
    print("[+] Saved to: %s" % ACCOUNTS_FILE)

if __name__ == "__main__":
    main()