# ═══════════════════════════════════════════════════════════════
# bot_core.py — LINOX BOT X LINOX BOT (LINOX)
# ═══════════════════════════════════════════════════════════════

import asyncio, random, json, os, time
import aiohttp
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from xC4 import *
from xP import JoinSq, OpenCh, MsqSq, ExitSq
from byte import Encrypt_ID, encrypt_api
from Pb2 import DEcwHisPErMsG_pb2, sQ_pb2
import urllib.parse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════

SPAM_TARGETS_FILE = "spam_targets.json"
online_writer = None
whisper_writer = None
spam_running = False
SPAM_INTERVAL = 0.5
bot_uid = None
ToKen = None
region = None
#أيدي أدمن البوت
admin_uid = "18897923037"
pending_ghost_future = None
ghost_team_id = None
ghost_squad_code = None
spm_tasks = {}
ban_task = None
ban_running = False
ban_targets = set()
evo_cycle_running = False
evo_cycle_task = None
freeze_running = False
freeze_task = None
fast_spam_running = False
fast_spam_task = None
custom_spam_running = False
custom_spam_task = None
msg_spam_running = False
msg_spam_task = None
mg_spam_task = None
lag_running = False
lag_task = None
reject_spam_running = False
reject_spam_task = None
emote_hijack = False
bot_enabled = True
# ═══════════════════════════════════════════════════════════════
# ايدي أسلحة الأيفو
# ═══════════════════════════════════════════════════════════════
EVO_IDS = [
    909000063, 909000075, 909040010, 909000081, 909039011,
    909045001, 909038012, 909042008, 909051003, 909035012,
    909000098, 909033002, 909037011, 909049010, 909041005,
    909038010, 909033001, 909035007, 909000090, 909000085,
    909000068
]
# ═══════════════════════════════════════════════════════════════
# NEW EMOTE SYSTEMS (رقصات جديدة)
# ═══════════════════════════════════════════════════════════════

# ─── Load emotes.json ───
try:
    with open("emotes.json", "r", encoding="utf-8") as _f:
        _emote_list = json.load(_f)
    GENERAL_EMOTES_MAP = {item["Number"]: int(item["Id"]) for item in _emote_list}
    EMOTE_MAP = {int(item["Number"]): int(item["Id"]) for item in _emote_list}
    print(f"✅ Loaded {len(GENERAL_EMOTES_MAP)} emotes from emotes.json")
except Exception as _e:
    GENERAL_EMOTES_MAP = {}
    EMOTE_MAP = {}
    print(f"❌ emotes.json load error: {_e}")

# ─── Load emote_menu.json ───
try:
    with open("emote_menu.json", "r", encoding="utf-8") as _f:
        EMOTE_MENU = json.load(_f)
except Exception:
    EMOTE_MENU = {}

# ─── Name-based emote map ─── اسامي الرقصات
NAME_EMOTES = {
    "ak": 909000063, "scar": 909000068, "mp40": 909000075,
    "m1014": 909000081, "xm8": 909000085, "famas": 909000090,
    "ump": 909000098, "m1887": 909035007, "woodpecker": 909042008,
    "groza": 909041005, "m4a1": 909033001, "thompson": 909038010,
    "g18": 909038012, "parafal": 909045001, "p90": 909049010,
    "m60": 909051003, "fist": 909037011, "ring": 909050009,
    "heart": 909038004, "love": 909000010, "dance": 909000027,
    "hello": 909000001, "hi": 909000001, "money": 909000129,
    "lol": 909000002, "sad": 909038005, "angry": 909000014,
    "chicken": 909000006, "dab": 909000005, "selfie": 909000040,
    "shower": 909051004, "flower": 909051002, "petals": 909051013,
}
#رقم الرقصات
NUMBER_EMOTES = GENERAL_EMOTES_MAP

# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def load_spam_targets():
    if os.path.exists(SPAM_TARGETS_FILE):
        with open(SPAM_TARGETS_FILE, "r") as f:
            return set(json.load(f))
    return set()
#حفظ أيدي السبام في ملف spam_targets.json
def save_spam_targets():
    with open(SPAM_TARGETS_FILE, "w") as f:
        json.dump(list(spam_targets), f)

spam_targets = load_spam_targets()

#اختيار الألوان لرسالة اللعبه عشوائي
def get_random_color():
    colors = [
        "[FF0000]", "[00FF00]", "[0000FF]", "[FFFF00]", "[FF00FF]", "[00FFFF]", "[FFFFFF]", "[FFA500]",
        "[A52A2A]", "[800080]", "[000000]", "[808080]", "[C0C0C0]", "[FFC0CB]", "[FFD700]", "[ADD8E6]",
        "[90EE90]", "[D2691E]", "[DC143C]", "[00CED1]", "[9400D3]", "[F08080]", "[20B2AA]", "[FF1493]",
        "[7CFC00]", "[B22222]", "[FF4500]", "[DAA520]", "[00BFFF]", "[00FF7F]", "[4682B4]", "[6495ED]",
        "[5F9EA0]", "[DDA0DD]", "[E6E6FA]", "[B0C4DE]", "[556B2F]", "[8FBC8F]", "[2E8B57]", "[3CB371]",
        "[6B8E23]", "[808000]", "[B8860B]", "[CD5C5C]", "[8B0000]", "[FF6347]", "[FF8C00]", "[BDB76B]"
    ]
    return random.choice(colors)
#ايدي الأفتار
def get_random_avatar():
    avatar_list = [
        902050001, 902050002, 902050003, 902039016, 902050004,
        902047011, 902047010, 902049015, 902050006, 902049020
    ]
    return random.choice(avatar_list)
#أيدي الستيكر
def get_random_sticker():
    sticker_packs = [
        ("1200000001", 1, 24),
        ("1200000004", 1, 15),
        ("1200000002", 1, 13),
    ]
    pack_id, start, end = random.choice(sticker_packs)
    sticker_no = random.randint(start, end)
    return f"[1={pack_id}-{sticker_no}]"
#--------------------------------------------
def xMsGFixinG(n):
    return '🗿'.join(str(n)[i:i + 3] for i in range(0, len(str(n)), 3))

def fix_num(number):
    fixed = ""
    count = 0
    num_str = str(number)
    for char in num_str:
        if char.isdigit():
            count += 1
        fixed += char
        if count == 3:
            fixed += "[c]"
            count = 0
    return fixed


def dec_to_hex(decimal):
    hex_str = hex(decimal)[2:]
    return hex_str.upper() if len(hex_str) % 2 == 0 else '0' + hex_str.upper()
    
async def encrypt_packet(packet_hex, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    packet_bytes = bytes.fromhex(packet_hex)
    padded_packet = pad(packet_bytes, AES.block_size)
    return cipher.encrypt(padded_packet).hex()

async def nmnmmmmn(packet_hex, key, iv):
    return await encrypt_packet(packet_hex, key, iv)

# ═══════════════════════════════════════════════════════════════
# AUTH TOKEN BUILDERS
# ═══════════════════════════════════════════════════════════════
def build_ob55_online_auth(account_uid, token, kts, key, iv):
    token_bytes = token.encode("utf-8")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    enc_token = cipher.encrypt(pad(token_bytes, 16))
    opcode = bytes.fromhex("830c")
    uid_bytes = int(account_uid).to_bytes(8, byteorder="big")
    kts_bytes = int(kts).to_bytes(4, byteorder="big")
    len_bytes = len(enc_token).to_bytes(8, byteorder="big")
    return opcode + uid_bytes + kts_bytes + len_bytes + enc_token, enc_token

def create_auth_token_chat(account_id, jwt_token, timestamp, key, iv):
    try:
        K = bytes.fromhex(key) if isinstance(key, str) else key
        V = bytes.fromhex(iv) if isinstance(iv, str) else iv
        jwt_bytes = jwt_token.encode('utf-8')
        ct = AES.new(K, AES.MODE_CBC, V).encrypt(pad(jwt_bytes, AES.block_size))
        uid_b = int(account_id).to_bytes(8, 'big')
        ts_b = int(timestamp).to_bytes(4, 'big')
        len_b = len(ct).to_bytes(4, 'big')
        header = bytes.fromhex('6d19') + uid_b + ts_b + len_b
        return (header + ct).hex()
    except Exception as e:
        print(f"[AUTH TOKEN ERROR] {e}")
        return None

async def cHTypE(H):
    if not H:
        return 'Squid'
    elif H == 1:
        return 'CLan'
    elif H == 2:
        return 'PrivaTe'

async def DecodeWhisperMessage(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto = DEcwHisPErMsG_pb2.DecodeWhisper()
    proto.ParseFromString(packet)
    return proto

async def GeTSQDaTa(D):
    try:
        return D['5']['data']['1']['data'], D['5']['data']['17']['data'], D['5']['data']['31']['data']
    except KeyError:
        return None, None, None

#اكواد الألوان للرسائل في اللعبه
async def get_colorful_message(message_text, message_number):
    color_palette = ["FF0000", "FFFF00", "0000FF", "FF00FF", "00FFFF", "FFA500",
                     "FF1493", "00FF7F", "7B68EE", "FF66CC", "00CED1", "FF69B4",
                     "32CD32", "9370DB", "FF4500", "1E90FF", "ADFF2F", "FF6347"]
    color_index = (message_number - 1) % len(color_palette)
    return f"[C][B][{color_palette[color_index]}]{message_text}"
# ═══════════════════════════════════════════════════════════════
# PACKET BUILDERS
# ═══════════════════════════════════════════════════════════════

async def NewClanChatPacket(message_text, key, iv, clan_id=3102281341):
    fields = {1: 16801068917, 2: 18, 4: 1, 5: {1: 16801068917, 2: clan_id, 3: 1, 4: 'LINOXKING',
        5: 1785944381, 7: 6, 9: {1: message_text, 4: 301, 8: '♧LinoxㅤDrag♧', 13: '',
        14: {1: 16801068917}, 18: {1: 16801068917, 3: 1, 4: ''}},
        10: 'ar', 13: {2: 1, 3: 1}, 14: '', 16: int(time.time() * 1000)}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', key, iv)


async def SEndMsG(H, message, Uid, chat_id, key, iv):
    TypE = await cHTypE(H)
    if TypE == 'Squid':
        return await xSEndMsgsQ(message, chat_id, key, iv)
    elif TypE == 'CLan':
        return await NewClanChatPacket(message, key, iv, chat_id)
    elif TypE == 'PrivaTe':
        return await xSEndMsg(message, 2, Uid, Uid, key, iv)


async def SEndPacKeT(OnLinE, ChaT, TypE, PacKeT):
    if TypE == 'ChaT' and ChaT:
        whisper_writer.write(PacKeT); await whisper_writer.drain()
    elif TypE == 'OnLine':
        online_writer.write(PacKeT); await online_writer.drain()

#دالة أرسال الرسائل
async def safe_send_message(chat_type, message, uid, chat_id, key, iv, max_retries=3):
    for attempt in range(max_retries):
        try:
            packet = await SEndMsG(chat_type, message, uid, chat_id, key, iv)
            if packet:
                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', packet)
                return True
        except Exception as e:
            print(f"❌ Send fail (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5)
    return False

async def JoinSq_original(code, K, V):
    skinz = {1: 4, 2: {4: "\u0001\u0007\t\n\u000b\u0012\u0019 '", 5: str(code), 6: 6, 8: 1,
        9: {1: "08FFF3BE903F27DF0203110111110000006B0003006800169194106F13CF106E4676251411010404dfe9e8b5ca3ca4f96a3119c00000004f03060301cacfa16d",
            2: 130, 3: "tY_S\u0013\b\u0001M\u0002\u0000T\u0000\u0005\u000e\b\t\u0002\u0000\u0003U\u0003\u0001V\u000fR\u000e\tRQ\u0002\u0004\u0005US\u0003XS\u0005\u0001\u0002\u0011\u0001\u0002JuTAEN\u001e\u0002\u001c\u0002\u001f\u0013\b\u0003M\u001cDbz_Q@}p_QOgsC\u001dYVI\u0004UAAj_ga\u0004\u0012\u0000K\u001d\u0007_t\u0019b\bCx\u0002UeGat\u001fTTCBLER`\u0006\u0001\r\f\u0012\u0006\u0005N^^\u0002acH~r\u0004_\u0003RO|\u000bcd_@~`Rnqrgh\n\u0015\nL\\Nh\u0000~G\u000et\u0000eb]VQ\u0006t^F[ZIGxCdZD\u000b\u0011\u0002OA~LP@\u000fcSDyATQApaT^{|wa]\\\u0001E\u000f\u0013\nJfxve}\u0004J\u0003c{YL\u0007^^yDYQf\bhe\u0005_wg\r\u0010\u0007\bEHpX@||\u0002Z\\uTGyA\u0001JP\u0005t~VkTE\u0000J\\\u000b\u0013\nMr\u0018zTzK}qE]vnvwROuheYvwduvQ\r\u001a\u0005M\u0006z\u001dfXfzvHFc~dXUz}O\u001aB\u0005t\u0002i\u001co_\u0004\u0012\u0003\u0007J\u0006b\u0003\u000eqlfvbEstgu~wB\u0001v@`yI\u0002ZPx\f\u0014\u0003NR\u0002yBZvuD_cd\u0004q]lH]\u0007bD}pCe\t\u0004t\n",
            4: "w^_R", 6: 11, 7: "\u0014\u0004aqrg\u0015\u0013", 8: "1.132.1", 9: 3, 10: 2,
            11: "\u0003bbSQ6wxegh9qAdV2KyoVleA17yPmYF+yTnOrl+JMknmppeUBe5ZsiHueP2mZZ4KOs6b2Ail1S9z3qIeU9hGFZ2M6PP39/zjIc/RFVPAkgDagySswMVmYaPhkzU5IqNPow2843fyQUz9xI10NdMhl1WiI4Y6wCXBotiUS9wSgujQ4j0fWXUyklCxBWo8r27hyoGSVrPdTPXFMnJJpPRRFFmWqc3fWvMg+BNfxSRJOZRSrkzG0nNvSIJ4uZB2pqAlHIPEYx7bI6zsgwUVDiLZJKTUTyuCGbOd1DegDUFfazFesTG1LJknT5WhgzCsrBIy+f2l+LeJe5DW7wEwNaHambM7ECXcJcLIhB9kJJsW0tFvXkk3HSdcQ8N1K6wjSKWhpkW0kV8Zrjj0jkhS/7AZ6T9GJRIA827YDtTorBvbx1UkXjYrqYI1nSa2GaMexGnqlurc5DE3v1R+mUBI9GqmjEPgTSYVBxyeCdQMHaMXGtspAhvkiO84ToU87sP45pylDEfFOVoc/rcmdzWeqlYPsv6txKRtIHcb0cO+MoVShoU8ZUVRDF3znbqzVrscPIfplBaa79lwvQqzRubLl9XY="},
        11: {1: "IDC4", 2: 281, 3: "ME"}, 13: "fr", 16: "7OR\u0019", 20: "\b\u0015", 27: "\bH\u0010\u0003"}}
    return await GeneRaTePk((await CrEaTe_ProTo(skinz)).hex(), '0515', K, V)

async def MahirAccepted(uid, code, K, V, region):
    fields = {1: 4, 2: {1: int(uid), 3: int(uid), 4: "rYUW\u0017\t\u0007NR\u000f\u0005\u0004\\W\u0002\u000fV\u0004TPQ\u0003\u000f\u0005\u0004]\u0005\u000b\u0000\u0002W\u0005\r\nVY\u0004\u0007\u0007\u0007\u0017\u0001\bNQ\fS\u0005\u000e\u0006\f\u0005\rT\u0002\r\u0000TS\u0007U\u0004X\u0006RY\u0005\u0003\u0003SW\u0000\u000eQ\u0000^\u0014\u0003\u0004JXS\u000f\u0000g{gqfePblEZJp{_xU\bmQW\f\u0007\u000f\u0015\u0007H\\U^CHXh@Ax`\u000f~\rPN~Nz\\\u001fr_ckPU\u000b\u0015\u0005\u0003Ekfp\u007fcY\u0001nWV\u0002\u0005azE~N\u0007HTg\u0007w}@\u0002{\t\u0013\u0001NeNP]DUf|]ugINs{\u0001\\rAgB_\u0004fA]\u0004\r\u001a\u0000HpOv\\\u0005|gS\u0019\\A\u007fWW\u0003\u007fTqFGi\u0004Qr\u0019dW\u0004\u0011\rD\u0002yeZ]A\u0016a\u0007Ungeg\u0007E\\P\u001b\u000b\u0004\u0005dd\ff\r\u000f\u0017\t\u000fNRyZd\u0012tZ\fe\u0007AGv\u007fw]{P\u001c\u007f\u000ff\u0005ZJK\u0004\u0005\u0014\u0001Jgq\u001frymsB\u0001\u000fd`\u001bj~[}\u0004SDZ|IxKB\u0000\n\u0011\u0002J^`tjYN\u0007WQdE[PQ\u0002_{VP`S\t\u007f\u001dP\n\u000f\u000f\u0015\u0004\u0004L{V\u0003@yP[rgJ{Hpk\u0001\u000bw\u0001Agt_\u0003HxPc\u000b\u0017\u0005E`y\ngWoy\u0006S{A\u001b``Y\u0002Xzw}dDWOKsg\t\u0013\u000eNf\u000e\\`\u0005AwJc\u0003BM\u0001^\u0000R\u0002Qoh]tbS~`G\r\u001a\u0004HibAQ\u000f^XNt~kDUWaeaNqcLQ]Py[G\u0004",
            8: 1, 9: {1: "08FBA33CFF105FDD02030A01111100000003000100020000B687046B0D6D2083467625141101030175a63c900e748c3f6a311e04000000ff00040202cacfa16d",
            2: 197, 3: "735154531406054a035305025a0e50560f5100040250020f5e0401520653000303505e0d520302501500064d705548424e1f051a001e12040a441d45677f5a56477574565e4f6274451d585849005a4f456d5b64670c1400496d017842740c670100040069536e72586c02016e657e566b524403081500044d0d515b637f757c19095c7c510b00417f565e5e066f5b584d6e02400a160e4d58496d0177400e750763605c575d0f7d5f475e5f4c407f4b60534b0b140549751e66407a4860726e44400e6103557e515c646f43577106077b60051b0f4b4e474e58457e4f615c01406000051e0361516e7b67614e040102540c1609004a0e40730f62517f446a135179507e706850547f7e7a67795553597c0a1206445b456640046265725c4d505d446d50737b7c42035970486370645e0b12034d506f5c7a1c554f574b0e765a0f0a7364505203477569456c6c420f0a1604014b647149136c186f795f5d78755e550e7842545e53747b08705f7f5d0a14004a08666b5a5b5f00045c7f5e584d72584262705f56055c61475564790515004b76514178587f52797a0f077a070953507d7f4d784f794f667b4256081b0e4a75627d4778417a06717574747c4c78557b4b7a0a697f0e714573600a",
            4: "{Y_R", 6: 13, 7: "1c6f017306741513", 8: "2.126.22", 9: 2, 10: 1,
            11: "036262535136784d584e38742b416456324b796f566c6537392f763672324d4773683377706379634f6b6b6f7447397934523930517432797246474c464c624c777a7747344d4d5257623146756d2b6556777a62597736743973492b787059612f55596e43465a59485235713348705830306c485a6f3632565145574e7145705866414c38734a754646575247386d376f5444566a4c484c576e714c52576f4e653236437a734c346a4144482b71694b55384d71476c5936546669544863716c487a345568463869396a365233366d49774b71746c36714f797568513854367945714b69742f45466d2b3636634b787649304f384d6c41385166454b6253467366477a2f30684e6a543873305369722f3962635a2f4679376c752f61632f366765704d415734566b442b36374f535756473665377a775a79312b797a42334b70632b7571782b577437414d39727761644439575765704570567849526d66654f5847627775787a68574b5664344c49586f415a364b387063647450627953575857455135706a542b653669365a2f6177444a3179356f774d5a534f64487262392b7877424a4d444f7848565a7a483372547a30314a316738517675466b656c3042433746473630683456427041494457487956684e794b4f5145507139467a4a6272686b316146306768766578512f6a2f484767426a5268675134645243372b477a5a687a2b77505967376454746f2b494d56363774642b54435653314234346b4148395a6d415872763758615941626477644e664f533170484875736b7336346f72463452534d3772656345417661484e61484854314c5545686e786a5a616d4d4f303d"},
            10: str(code), 11: {1: "IDC3", 2: 84, 3: "BD"}, 13: "en", 16: "374f5219",
            20: {1: 21}, 23: "a_1477547277882450725", 27: {1: 2, 2: 8}}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)

#قبول دعوة السكواد
async def accept_squad_invite(group_id, joiner_account_id, invitee_type, key, iv, region="bd"):
    fields = {1: 38, 2: {1: int(group_id), 2: int(joiner_account_id), 8: int(invitee_type)}}
    pkt_type = '0514' if region.lower() == "ind" else ('0519' if region.lower() == "bd" else '0515')
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), pkt_type, key, iv)

async def leave_channel_req(channel_id, channel_type, key, iv):
    fields = {1: 4, 2: {1: int(channel_id), 2: int(channel_type), 3: "en"}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1215', key, iv)

async def SPamSqForSpm(Uid, K, V):
    same_value = random.choice([4096, 16384, 8192])
    fields = {1: 33, 2: {1: int(Uid), 2: "ME", 3: 1, 4: 1,
        5: bytes([1, 7, 9, 10, 11, 18, 25, 26, 32]), 6: "iG:[C][B][FF0000] @CH9AYFAX1",
        7: 330, 8: 1000, 10: "ME",
        11: bytes([49,97,99,52,98,56,48,101,99,102,48,52,55,56,97,52,52,50,48,51,98,102,56,102,97,99,54,49,50,48,102,53]),
        12: 1, 13: int(Uid),
        14: {1: 2203434355, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"},
        16: 1, 17: 1, 18: 312, 19: 46, 23: bytes([16, 1, 24, 1]),
        24: await xBunnEr(), 26: "", 28: "",
        31: {1: 1, 2: same_value}, 32: same_value,
        34: {1: int(Uid), 2: 8, 3: bytes([15,6,21,8,10,11,19,12,17,4,14,20,7,2,1,5,16,3,13,18])}},
        10: "en", 13: {2: 1, 3: 1}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)

async def GhostPakcet(player_id, nm, secret_code, key, iv):
    fields = {1: 61, 2: {1: int(player_id), 2: {1: int(player_id), 2: 1159,
        3: f"[b][c]{get_random_color()}{nm}", 5: 12, 6: 999, 7: 1,
        8: {2: 1, 3: 1}, 9: 3}, 3: secret_code}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', key, iv)

async def xSKINZxLag(K, I):
    return await GeneRaTePk((await CrEaTe_ProTo({1: 15, 2: {1: 804266360, 2: 1}})).hex(), '0515', K, I)

async def xBaNchaTxSkInZ(uidd, K, V):
    return await GeneRaTePk((await CrEaTe_ProTo({1: 3, 2: {1: int(uidd), 3: "fr", 4: "1750728024661459697_3qind8eeqs"}})).hex(), '1215', K, V)

async def create_lw5_packet1(key, iv):
    fields = {1: 1, 2: {2: "0b", 3: 43, 4: 1, 5: "en", 8: {1: "IDC3", 2: 109, 3: "BD"},
        9: 1, 10: "01090a0b12192027", 11: 1, 13: 1,
        14: {1: "08FBA33CFF11B915020FEB099999000002BF000C02B3024798E574700E9B7471467625142200004375a63c900e748c3f6a311e04000000ff42002b09cacfa16d",
            2: 1023, 3: "715c5f561b06054a03530500570555590f5100040250000255010e520653000303525306570c02501500064d72584347411f051a001e1206074f184a677f5a564775765b554a6d74451d58584902574440625b64670c14004b600a7d4d740c670100040264586b7d586c02016e657c5b60574b03081500044d60795258726206047f04600f405b18710347746242085f055442530a160e4d58496f0c7c4501750763605c575f02765a485e5f4c407f4b625e400e1b054973535b40655e5151566e6507797e6b47727a1c6e455762637d650708100a447e704c1e530200437a604b66065d595f58444c5a06095a6c44677a0c14040b4f705b7d75624374067840416d60067353017f5972506356014354680a12044950406940046265725c4f5d56416250737b7c42035b7d43667f645e0b12034d5262577f13554f574b0e76580201766b50520347756947616747000a1604014b6473441869176f795f5d78755c58057d4d545e53747b08725274580514004a08666b585654050b5c7f5e584d725a4f69755056055c61475566740e100f4b76514178587d5f727f00077a070953507f72467d40794f667b42560a16054f7a627d4778417a047c7e717b7c4c78557b4b7807627a01714573600a",
            4: "{Y_R", 6: 13, 7: "136601706b6f54001513", 8: "2.126.20", 9: 2, 10: 1,
            11: "0362625351367a6e2f56386835416456324b796f566c576a3265735033734558335070623443526c656c47355732327673496e477a425a49677375684a664336766942532f4277526d3632374a624a724c562b586b664c516c6749424634615664544e34473869494c456e4c7643347754354670754e66444b7746367765466d675a2b2b36704d57694549677343415756457144554a454d737271515a306b544266635a45334959485661774d5332622b4f6b5a477a755171576e3645624c6a3932646c31307754614d55714e355556796742506f454572376651673249754332545a773333796c71493838627562512f6e425072353577785436617955544d63624d2b756d4542345a736c5165504d58725365737864622f30577967786849384a352f73484f685730494a49643450534b6d6a41734b315251495257634c35646355554b457a6d33334475735877384a5267483364412b66414b336433726a4241317954327451326c2f73584c6d4b4b6456707062624b4f3272694c384947382b634a3863506533314241456d517876744f495631323658394c4b35414c6a38533631526d6159617077676e4579724a5a7a624d4c596c3542554b6d7934473546334c6152454c4e6d726a684f557065462f39686f64356c526378623250777244566d455665715355764a456548644e375279344c707035563466392f6f6d3837426b5a6c6159364c5439396b5579554266434c5538647a4a2b43655a35784a44585064654a51686e46496945506e7a506d32334b637a2b512b384a51307a522b5a5a41762b694873454748516a536e61467862356a517a526c374f5a793241385731437263513d"},
        19: 329, 21: "374f5219", 24: {1: 21}, 27: "a_1477547277882450725"}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', key, iv)

async def create_lw5_packet2(key, iv):
    return await GeneRaTePk((await CrEaTe_ProTo({1: 17, 2: {1: 17165783357, 2: 1, 3: 4, 4: 6100, 5: b'\x1a', 8: 5, 13: 329}})).hex(), '0515', key, iv)


# ═══════════════════════════════════════════════════════════════
# NEW PACKET BUILDERS
# ═══════════════════════════════════════════════════════════════
#دالة أرسال الستيكر
async def send_sticker_packet(target_uid, chat_id, key, iv, nickname="BLACK"):
    try:
        sticker_value = get_random_sticker()
        fields = {1: 1, 2: {1: int(target_uid), 2: int(chat_id),
            5: int(time.time()), 8: f'{{"StickerStr" : "{sticker_value}", "type":"Sticker"}}',
            9: {1: f"[C][B][FF0000]{nickname}", 2: get_random_avatar(), 4: 330, 5: 827001007,
                8: "LINOX TEAM", 10: 1, 11: 66, 12: 66, 13: {1: 2},
                14: {1: 1158053040, 2: 8, 3: b"\x10\x15\x08\x0a\x0b\x15\x0c\x0f\x11\x04\x07\x02\x03\x0d\x0e\x12\x01\x05\x06"}},
            10: "en", 13: {2: 2, 3: 1}, 14: {}}}
        packet_hex = (await CrEaTe_ProTo(fields)).hex()
        encrypted = await encrypt_packet(packet_hex, key, iv)
        pl = len(encrypted) // 2
        hl = f"{pl:04x}"
        prefix = "121500" + ("0" * (6 - len(hl)))
        return bytes.fromhex(prefix + hl + encrypted)
    except Exception as e:
        print(f"❌ Sticker error: {e}")
        return None

async def animation_packet(animation_id, key, iv):
    fields = {1: 88, 2: {1: {1: int(animation_id)}}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    encrypted = await encrypt_packet(packet_hex, key, iv)
    pl = len(encrypted) // 2
    hl = format(pl, 'x')
    final = "051500" + "0" * (6 - len(hl)) + hl + encrypted
    return bytes.fromhex(final)

async def Look_Changer(bundle_id, key, iv, look_type=1, region="bd"):
    fields = {1: 88, 2: {1: {1: bundle_id, 2: look_type}, 2: 2}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    encrypted = await encrypt_packet(packet_hex, key, iv)
    hl = await DecodE_HeX(len(encrypted) // 2)
    if region.lower() == "ind":
        pt = "0514"
    elif region.lower() == "bd":
        pt = "0519"
    else:
        pt = "0515"
    if len(hl) == 2:
        h = f"{pt}000000"
    elif len(hl) == 3:
        h = f"{pt}00000"
    elif len(hl) == 4:
        h = f"{pt}0000"
    elif len(hl) == 5:
        h = f"{pt}000"
    else:
        h = f"{pt}000000"
    return bytes.fromhex(h + hl + encrypted)

#لا تعمل
async def Room_Spam(Uid, Rm, Nm, K, V):
    fields = {1: 78, 2: {1: int(Rm), 2: "iG:[C][B][FF0000]...", 3: {2: 1, 3: 1},
        4: 330, 5: 6000, 6: 201, 10: get_random_avatar(), 11: int(Uid), 12: 1,
        15: {1: 1, 2: 32768}, 16: 32768,
        18: {1: 11481904755, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"},
        31: {1: 1, 2: 32768}, 32: 32768,
        34: {1: int(Uid), 2: 8, 3: bytes([15,6,21,8,10,11,19,12,17,4,14,20,7,2,1,5,16,3,13,18])}}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0e15', K, V)

async def banecipher(target_uid, key, iv):
    banner_text = ".\n.\n.\n[b][FF0000]LINOX BOT[00FF00] ⚡\n.\n.\n."
    fields = {1: 5, 2: {1: int(target_uid), 2: 1, 3: int(target_uid), 4: banner_text}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    encrypted = await encrypt_packet(packet_hex, key, iv)
    hl = await DecodE_HeX(len(encrypted) // 2)
    if len(hl) == 2:
        f = "0515000000"
    elif len(hl) == 3:
        f = "051500000"
    elif len(hl) == 4:
        f = "05150000"
    elif len(hl) == 5:
        f = "0515000"
    else:
        f = "0515000000"
    return bytes.fromhex(f + hl + encrypted)


async def banecipher1(target_uid, key, iv):
    gay_text = ".\n.\n.\n[b][FF0000]LINOX BOT ⚡[00FF00]\n.\n.\n."
    fields = {1: int(target_uid), 2: 5, 4: 50, 5: {1: int(target_uid), 2: gay_text}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    encrypted = await encrypt_packet(packet_hex, key, iv)
    hl = await DecodE_HeX(len(encrypted) // 2)
    if len(hl) == 2:
        f = "0515000000"
    elif len(hl) == 3:
        f = "051500000"
    elif len(hl) == 4:
        f = "05150000"
    elif len(hl) == 5:
        f = "0515000"
    else:
        f = "0515000000"
    return bytes.fromhex(f + hl + encrypted)

#دالة أرسال شارات الأنجازات
async def convert_kyro_to_your_system(target_uid, chat_id, key, iv, nickname="LINOX", title_id=None):
    try:
        if title_id is None:
            available_titles = [905090075, 904990072, 904990069, 905190079, 904090014, 904090015,
                                904090024, 904090025, 904090026, 904090027, 904990070, 904990071]
            title_id = random.choice(available_titles)
        fields = {1: 1, 2: {1: int(target_uid), 2: int(chat_id),
            5: int(time.time()),
            8: f'{{"TitleID":{title_id},"type":"Title"}}',
            9: {1: f"[C][B][FF0000]{nickname}", 2: get_random_avatar(), 4: 330, 5: 827001007,
                8: "LINOX TEAM", 10: 1, 11: 1, 13: {1: 2},
                14: {1: 1158053040, 2: 8, 3: b"\x10\x15\x08\x0a\x0b\x15\x0c\x0f\x11\x04\x07\x02\x03\x0d\x0e\x12\x01\x05\x06"}},
            10: "en", 13: {2: 2, 3: 1}, 14: {}}}
        packet_hex = (await CrEaTe_ProTo(fields)).hex()
        encrypted = await encrypt_packet(packet_hex, key, iv)
        pl = len(encrypted) // 2
        hl = f"{pl:04x}"
        prefix = "121500" + ("0" * (6 - len(hl)))
        return bytes.fromhex(prefix + hl + encrypted)
    except Exception as e:
        print(f"❌ Title error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
# LOOPS
# ═══════════════════════════════════════════════════════════════
async def spm_loop(uid, key, iv, interval=0.5):
    while True:
        try:
            if online_writer is not None:
                packet = await SPamSqForSpm(uid, key, iv)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', packet)
            else:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"spm_loop error for {uid}: {e}")
        await asyncio.sleep(interval)

async def ban_loop(key, iv, interval=0.5):
    global ban_running, ban_targets
    ban_running = True
    while ban_running:
        if online_writer is not None and ban_targets:
            for uid in list(ban_targets):
                try:
                    ban_pkt = await xBaNchaTxSkInZ(uid, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', ban_pkt)
                except Exception as e:
                    print(f"Ban error: {e}")
        await asyncio.sleep(interval)

async def evo_gun_cycle(uids, evo_ids_list, key, iv, region):
    global evo_cycle_running
    cc = 0
    while evo_cycle_running:
        cc += 1
        for emote_id in evo_ids_list:
            if not evo_cycle_running:
                break
            for uid_str in uids:
                try:
                    H = await Emote_k(int(uid_str), int(emote_id), key, iv, region)
                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                except Exception as e:
                    print(f"Emote error: {e}")
            if evo_cycle_running:
                for i in range(5):
                    if not evo_cycle_running:
                        break
                    await asyncio.sleep(1)
        if evo_cycle_running:
            await asyncio.sleep(2)

#fast emote spam
async def fast_emote_spam(uids, emote_id, key, iv, region):
    global fast_spam_running
    count = 0
    while fast_spam_running and count < 25:
        for uid in uids:
            try:
                H = await Emote_k(int(uid), int(emote_id), key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            except Exception:
                pass
        count += 1
        await asyncio.sleep(0.1)

async def custom_emote_spam(uid, emote_id, times, key, iv, region):
    global custom_spam_running
    count = 0
    while custom_spam_running and count < times:
        try:
            H = await Emote_k(int(uid), int(emote_id), key, iv, region)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            count += 1
            await asyncio.sleep(0.1)
        except Exception:
            break

async def reject_spam_loop(target_uid, key, iv):
    global reject_spam_running
    count = 0
    while reject_spam_running and count < 150:
        try:
            p1 = await banecipher1(target_uid, key, iv)
            p2 = await banecipher(target_uid, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', p1)
            await asyncio.sleep(1)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', p2)
            count += 1
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Reject error: {e}")
            break
    return count

#دالة سبام الرسائل
async def msg_spam_loop(message_text, times, chat_id, key, iv, region):
    global msg_spam_running
    count = 0
    while msg_spam_running and count < times:
        try:
            colorful = await get_colorful_message(message_text, count + 1)
            msg_packet = await xSEndMsgsQQ(colorful, int(chat_id), key, iv)
            if msg_packet and whisper_writer:
                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', msg_packet)
                count += 1
                await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Msg error: {e}")
            break
    return count

async def xSEndMsgsQQ(Msg, id, K, V):
    fields = {1: id, 2: id, 4: Msg, 5: 1756580149, 7: 2, 8: 904990072,
        9: {1: "xBe4!sTo - C4", 2: get_random_avatar(), 4: 330, 5: 1001000001,
            8: "xBe4!sTo - C4", 10: 1, 11: 1, 13: {1: 2},
            14: {1: 1158053040, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0015\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}},
        10: "en", 13: {2: 2, 3: 1}}
    Pk = (await CrEaTe_ProTo(fields)).hex()
    Pk = "080112" + await EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return await GeneRaTePk(Pk, '1201', K, V)

async def send_wave_messages(message_text, repeats, chat_id, key, iv, region):
    global msg_spam_running
    count = 0
    total_cycles = 0
    while msg_spam_running and total_cycles < repeats:
        try:
            for i in range(1, len(message_text) + 1):
                if not msg_spam_running:
                    break
                partial = message_text[:i]
                colorful = await get_colorful_message(partial, i)
                msg_packet = await xSEndMsgsQ(colorful, int(chat_id), key, iv)
                if msg_packet and whisper_writer:
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', msg_packet)
                    count += 1
                    await asyncio.sleep(0.1)
            for i in range(len(message_text) - 1, 0, -1):
                if not msg_spam_running:
                    break
                partial = message_text[:i]
                colorful = await get_colorful_message(partial, i)
                msg_packet = await xSEndMsgsQQ(colorful, int(chat_id), key, iv)
                if msg_packet and whisper_writer:
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', msg_packet)
                    count += 1
                    await asyncio.sleep(0.1)
            total_cycles += 1
        except Exception as e:
            print(f"Wave error: {e}")
            break
    return count, total_cycles

async def freeze_emote_spam(uid, key, iv, region, chat_type, chat_id, sender_uid):
    global freeze_running
    FREEZE_EMOTES = [909052010, 909052010, 909052010]
    cycles = 0
    while freeze_running and cycles < 10:
        for emote_id in FREEZE_EMOTES:
            if not freeze_running:
                break
            try:
                emote_packet = await Emote_k(int(uid), emote_id, key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', emote_packet)
                await asyncio.sleep(0.1)
            except Exception:
                pass
        cycles += 1
        await asyncio.sleep(1)
    return cycles
# ═══════════════════════════════════════════════════════════════
# API CALLS
# ═══════════════════════════════════════════════════════════════

#إرسال طلب الصداقة للاعب
async def send_friend_request(target_uid, token, region):
    try:
        encrypted_id = Encrypt_ID(target_uid)
        payload = f"08a7c4839f1e10{encrypted_id}1801"
        kb = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
        ib = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
        cipher = AES.new(kb, AES.MODE_CBC, ib)
        ep = cipher.encrypt(pad(bytes.fromhex(payload), AES.block_size)).hex()
        url = "https://clientbp.ppmainecoonghj.com/RequestAddingFriend"
        headers = {"Authorization": f"Bearer {token}", "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1", "ReleaseVersion": "OB55",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=bytes.fromhex(ep), ssl=False) as r:
                return (True, "✅ تم إرسال طلب الصداقة للاعب") if r.status == 200 else (False, f"❌ Status: {r.status}")
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

##################################

#حذف الاعب
async def remove_friend(target_uid, token, region):
    try:
        import RemoveFriend_Req_pb2
        msg = RemoveFriend_Req_pb2.RemoveFriend()
        msg.AuthorUid = int(admin_uid); msg.TargetUid = int(target_uid)
        kb = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
        ib = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
        cipher = AES.new(kb, AES.MODE_CBC, ib)
        eb = cipher.encrypt(pad(msg.SerializeToString(), AES.block_size))
        url = "https://clientbp.ppmainecoonghj.com/RemoveFriend"
        headers = {'Authorization': f"Bearer {token}", 'User-Agent': "Dalvik/2.1.0 (Linux; Android 9)",
            'Content-Type': "application/x-www-form-urlencoded", 'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1", 'ReleaseVersion': "OB55"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=eb, headers=headers, ssl=False) as r:
                return (True, "✅ تم حذف الاعب") if r.status == 200 else (False, f"❌ Status: {r.status}")
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

##################################

#إرسال اشباح للفريق
async def ghost(teamcode, ban_key=None):
    try:
        if ban_key is None:
            ban_key = os.getenv('BAN_KEY', 'saeed')
        #api
        url = f"http://de20.spaceify.eu:26310//ghost?teamcode={teamcode}&names=AH_BOT"
        headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10)", "Accept": "application/json",
            "referer": "https://ff.garena.com/en/support/",
            "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, ssl=False) as r:
                if r.status == 200:
                    return True, await r.json()
                return False, f"Failed: {r.status}"
    except Exception as e:
        return False, f"Error: {str(e)}"

##################################
        
#إرسال الايكات للاعب
async def like_bot(player_id, ban_key=None):
    try:
        if ban_key is None:
            ban_key = os.getenv('BAN_KEY', 'saeed')

        url = f"https://liketi-iota.vercel.app/like?uid={player_id}"
        headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10)", "Accept": "application/json",
            "referer": "https://ff.garena.com/en/support/",
            "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, ssl=False) as r:
                if r.status == 200:
                    return True, await r.json()
                return False, f"Failed: {r.status}"
    except Exception as e:
        return False, f"Error: {str(e)}"
              
##################################

#فحص الحظر
async def check_banned(player_id, ban_key=None):
    try:
        if ban_key is None:
            ban_key = os.getenv('BAN_KEY', 'saeed')

        url = f"https://xct-xteam-status.vercel.app/check?uid={player_id}"
        headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10)", "Accept": "application/json",
            "referer": "https://ff.garena.com/en/support/",
            "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, ssl=False) as r:
                if r.status == 200:
                    return True, await r.json()
                return False, f"Failed: {r.status}"
    except Exception as e:
        return False, f"Error: {str(e)}"

##################################

#api info جلب معلومات الاعب
async def get_player_info(player_id):
    try:
        url = f"https://nirob-x-info.vercel.app/info?uid={player_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=False) as r:
                if r.status == 200:
                    return True, await r.json()
                return False, f"Failed: {r.status}"
    except Exception as e:
        return False, f"Error: {str(e)}"
 
##################################
 
#دالة جلب معلومات الاعب    
def format_player_info(data):
    basic = data.get("basicInfo", {}); clan = data.get("clanBasicInfo", {})
    captain = data.get("captainBasicInfo", {}); pet = data.get("petInfo", {})
    social = data.get("socialInfo", {}); credit = data.get("creditScoreInfo", {})
    diamond = data.get("diamondCostRes", {})
    def x(v): return str(v) if v else "0"
    m0 = f"[b][c][0000FF]معلومات الاعب:\n\n[b][c][90EE90]أسم الاعب : {basic.get('nickname', basic.get('nickname', 'Unknown'))}\n[90EE90]لايكات الاعب : {x(basic.get('liked', basic.get('liked', '0')))}\n[b][c][90EE90]مستوى الاعب : {basic.get('level', basic.get('level', '0'))}\n[b][c][90EE90]المنطقة : {basic.get('region', basic.get('region', 'Unknown'))}\n[b][c][90EE90]نقاط الرانكد : {basic.get('rankingPoints', basic.get('rankingPoints', 'Unknown'))}\n[b][c][90EE90]نقاط مستوى الاعب : {basic.get('exp', captain.get('exp', 'Unknown'))}\n[b][c][90EE90]جنس الاعب  : {social.get('gender', social.get('gender', 'Unknown'))}\n[b][c][90EE90]لغة الاعب : {social.get('language', social.get('language', 'Unknown'))}\n[b][c][b][c][90EE90]الحيوان : {pet.get('name', 'N/A')}\nمستوى الحيوان : {pet.get('level', 'N/A')}\nنقاط مستوى الحيوان : {pet.get('exp', 'N/A')}\nبايو الاعب :\n {social.get('signature', 'N/A')}"
    m1 = f"[b][c][ff0000]معلومات رابطة الاعب :\n\n[b][c][FFFF00]أسم الرابطة : {clan.get('clanName', 'N/A')}\nمستوى الرابطة : {clan.get('clanLevel', 'N/A')}\nسعة الرابطة : {clan.get('capacity', 'N/A')}\nعدد لاعبين الرابطة : {clan.get('memberNum', 'N/A')}"
    m2 = f"[b][c][808080]معلومات قائد الرابطة :\n\n[b][c][00FFFF]أسم الاعب : {captain.get('nickname', 'Unknown')}\nلايكات الاعب : {captain.get('liked', 'Unknown')}\nمستوى الاعب : {captain.get('level', 'Unknown')}\nالمنطقة : {captain.get('region', 'Unknown')}\nنقاط الرانكد : {captain.get('rankingPoints', 'Unknown')}\nنقاط مستوى الاعب : {captain.get('exp', 'Unknown')}"

    return m0, m1, m2
    
##################################

#فحص حاله الحظر
def format_check_result(data):
    try:
        return f"[b][c]{get_random_color()}حالة الاعب :\n\n[b][c][FFFFFF]{data.get('account_status', 'Unknown')}\n\n[b][c][00FFFF]DEV BY : LINOX BOT"
    except Exception as e:
        return f"[b][c]Error: {str(e)}"

#like bot
def format_like_bott(data):
    try:
        return f"[b][c]{get_random_color()}تم إرسال الايكات للاعب !\n\n[b][c][00FFFF]أسم الاعب :\n[FFFFFF]{data.get('PlayerNickname', 'Unknown')}\n\n[00FFFF]الايكات قبل :\n[FFFFFF]{data.get('LikesbeforeCommand', 'Unknown')}\n\n[00FFFF]الايكات بعد :\n[FFFFFF]{data.get('LikesafterCommand', 'Unknown')}\n\n[00FFFF]الايكات المضافة :\n[FFFFFF]{data.get('LikesGivenByAPI', 'Unknown')}\n\n[b][c][00FFFF]DEV BY : LINOX BOT"
    except Exception as e:
        return f"[b][c]Error: {str(e)}"

#ghost
def format_ghostt(data):
    try:
        return f"[b][c]{get_random_color()}تم إرسال الأشباح للفريق !"
    except Exception as e:
        return f"[b][c]Error: {str(e)}"
                
# ═══════════════════════════════════════════════════════════════
# TCP ONLINE HANDLER
# ═══════════════════════════════════════════════════════════════

async def TcPOnLine(ip, port, key, iv, AutHToKen, reconnect_delay=0.5):
    global online_writer, whisper_writer, region, pending_ghost_future, ghost_team_id, ghost_squad_code, emote_hijack, bot_uid
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            online_writer = writer
            token_bytes = bytes.fromhex(AutHToKen) if isinstance(AutHToKen, str) else AutHToKen
            writer.write(token_bytes); await writer.drain()
            print(f"✅ ONLINE connected to {ip}:{port}")
            while True:
                data = await reader.read(9999)
                if not data:
                    break
                hex_data = data.hex()
                if not hex_data.startswith("0500"):
                    continue
                try:
                    packet_json = json.loads(await DeCode_PackEt(hex_data[10:]))
                except Exception:
                    continue

                #القبول التلقائي لدعوة الفريق
                try:
                    if ('5' in packet_json and 'data' in packet_json['5'] and
                        '1' in packet_json['5']['data'] and '8' in packet_json['5']['data']):
                        owner = packet_json['5']['data']['1']['data']
                        code = packet_json['5']['data']['8']['data']
                        print(f"📩 Squad invite from {owner}")
                        join_pkt = await MahirAccepted(owner, code, key, iv, region)
                        if join_pkt and online_writer:
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_pkt)
                except Exception:
                    pass

                #الدخول التلقائي ل شات الفريق
                try:
                    uid_g, chat_code, squad_code = await GeTSQDaTa(packet_json)
                    if uid_g is not None:
                        INV_JOIN = await AutH_Chat(3, uid_g, chat_code, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', INV_JOIN)
                except Exception:
                    pass

                # Ghost future resolve
                try:
                    if pending_ghost_future and not pending_ghost_future.done():
                        f5 = packet_json.get('5', {}).get('data', {})
                        if '31' in f5:
                            ghost_squad_code = f5['31'].get('data')
                        if '1' in f5:
                            ghost_team_id = f5['1'].get('data')
                        if ghost_team_id and ghost_squad_code:
                            pending_ghost_future.set_result(True)
                except Exception:
                    pass

                # Kick detect
                try:
                    if packet_json.get('4', {}).get('data') == 8:
                        f5 = packet_json.get('5', {}).get('data', {})
                        if f5.get('2', {}).get('data') == 5:
                            chat_code = f5.get('17', {}).get('data')
                            if chat_code is not None:
                                LeAvE = await leave_channel_req(chat_code, 3, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', LeAvE)
                                print("🚪 Kicked! Left channel")
                except Exception:
                    pass

            writer.close(); await writer.wait_closed(); online_writer = None
        except Exception as e:
            print(f"Online error: {ip}:{port} - {e}")
            online_writer = None
        await asyncio.sleep(reconnect_delay)


# ═══════════════════════════════════════════════════════════════
# TCP CHAT HANDLER — सारे commands
# ═══════════════════════════════════════════════════════════════

async def TcPChaT(ip, port, AutHToKen, key, iv, ready_event, region, reconnect_delay=0.5):
    global whisper_writer, online_writer, spm_tasks, ToKen, bot_uid, bot_enabled, emote_hijack
    global spam_targets, evo_cycle_running, evo_cycle_task, ban_task, ban_running, ban_targets
    global fast_spam_running, fast_spam_task, custom_spam_running, custom_spam_task
    global msg_spam_running, msg_spam_task, mg_spam_task, lag_running, lag_task
    global reject_spam_running, reject_spam_task, freeze_running, freeze_task

    print(f"📡 {region} → TCP CHAT connecting...")
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            whisper_writer = writer
            bytes_payload = bytes.fromhex(AutHToKen) if isinstance(AutHToKen, str) else AutHToKen
            whisper_writer.write(bytes_payload); await whisper_writer.drain()
            ready_event.set()
            print(f"✅ CHAT connected to {ip}:{port}")

            for tgt in spam_targets:
                if tgt not in spm_tasks or spm_tasks[tgt].done():
                    spm_tasks[tgt] = asyncio.create_task(spm_loop(tgt, key, iv))

            while True:
                data = await reader.read(9999)
                if not data:
                    break
                if not data.hex().startswith("120000"):
                    continue
                try:
                    response = await DecodeWhisperMessage(data.hex()[10:])
                    uid = response.Data.uid
                    chat_id = response.Data.Chat_ID
                    XX = response.Data.chat_type
                    inPuTMsG = response.Data.msg.lower()
                    msg_raw = response.Data.msg
                except Exception:
                    continue


                #تشغيل البوت من أمر من الأدمن
                # Ignore commands if bot off (except /on)
                if not bot_enabled and not inPuTMsG.strip().startswith('/on'):
                    if inPuTMsG.strip() != '/on':
                        continue
                        
                # ═══════════════════════════════════════════════
                #أظهار الأوامر للاعب
                # ═══════════════════════════════════════════════
                if inPuTMsG.strip() in ("/help", "help", "bot help"):
                    h0 = f"""[b][c]{get_random_color()}
WELCOME TO
[b][c][1F51FF] LINOX BOT PRO !

[b][c][FF3131]أنواع البوتات المتوفره لدينا :

[b][c][FFD700]SPAM BOT
[b][c][FFD700]GUILD GLORY
[b][c][FFD700]TCP BOT
[b][c][FFD700]GAME STUTTERING
[b][c][FFD700]PANEL FREE FIRE FOR PC
[b][c][FFD700]PANEL FREE FIRE FORE PHONE

[b][c][006400]يوجد المزيد من البوتات للتواصل :

[b][c][40E0D0]TELEGRAM : @linoxxcheat777
[b][c][40E0D0]INSTAGRAM : y9yasserx

[b][c][7B3F00]               ميزات البوت :
"""
                    h1 = f"""
[b][c][002366]السكواد :

[b][c][DFFF00]/5 
[b][c][E0FFFF]→ 5 في الفريق

[b][c][DFFF00]/join <code>
[b][c][E0FFFF]→ الدخول للسكواد

[b][c][DFFF00]/exit
[b][c][E0FFFF]→ الخروج من السكواد

[b][c][002366]الهجوم :

[b][c][DFFF00]/spam <uid> 
[b][c][E0FFFF]→ سبام دعوات

[b][c][DFFF00]/stp <uid> 
[E0FFFF]→ ايقاف السبام

[b][c][DFFF00]/room <id_room> <uid> 
[E0FFFF]→ إرسال أكثر من 3000 دعوة انضمام للروم

[b][c][DFFF00]/msg <code> <msg> 
[E0FFFF]→ سبام رسائل
"""
                    h2 = f"""
[b][c][002366]الرقصات :

[b][c][008000]/e <uid> <name emote> 
[b][c][00FFFF]→ أرسال الرقصه

[b][c][008000]/evo <uid> <1-21> 
[b][c][00FFFF]→ رقصات الأسلحه المطوره

[b][c][008000]/evos <uid>
[b][c][00FFFF]→ الرقص التلقائي

[b][c][008000]/sevos 
[b][c][00FFFF]→ ايقاف الرقص التلقائي

[b][c][008000]/sticker 
[b][c][00FFFF]→ أرسال ستيكر

[b][c][002366]الباقة :

[b][c][008000]/b <1-12> 
[b][c][00FFFF]→ تغيير باقة اللبس

[b][c][008000]/title
[b][c][00FFFF]→ أرسال شارات الأنجازات
"""



                    h3 = f"""
[b][c][FF0000]متعة :

[b][c][FF69B4]/love <name> 
[b][c][00FF00]→ رسالة حب

[b][c][FF69B4]/hair <name> 
[b][c][00FF00]→ بيت شعر

[b][c][FF69B4]/mth <2+2> 
[b][c][00FF00]→ الالة الحاسبة
"""
                    h4 = f"""
[b][c][FFFF00]معلومات :

[b][c][FFFFFF]/info <uid> 
[b][c][00FF00]→ معلومات الاعب

[b][c][FFFFFF]/check <uid> 
[b][c][00FF00]→ فحص حالة الاعب

[b][c][FFFFFF]/ai <question> 
[b][c][00FF00]→ التحدث مع الذكاء الأصطناعي

[b][c][FFFFFF]/like <uid> 
[b][c][00FF00]→ زيادة لايكات

[b][c][FFFFFF]/ghost <code> 
[b][c][00FF00]→ إرسال أشباح للفريق
"""
                    h5 = f"""
[b][c][FFA500]فقط للأدمن :

[b][c][0000FF]/add <uid> 
[b][c][FF0000]→ ارسال طلب صداقة

[b][c][0000FF]/remove <uid>
[b][c][FF0000]→ حذف من الاصدقاء

[b][c][0000FF]/on , /off 
[b][c][FF0000]→ تشغيل / ايقاف البوت

[b][c][0000FF]/admin 
[b][c][FF0000]→ معلومات المطورين
"""
                    for m in (h0, h1, h2, h3, h4, h5):
                        try:
                            P = await SEndMsG(XX, m, uid, chat_id, key, iv)
                            if P:
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            await asyncio.sleep(0.4)
                        except Exception:
                            pass

                # ═══════════════════════════════════════════════
                # ADMIN
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip() == "/admin":
                    msg = f"""[b][c]{get_random_color()} مطورين البوت :\n\n[00FFFF]LINOX BOT\nLINOX BOT\n\n[FFFF00]للتواصل مع المطورين :\n\n[b][c][00FFFF]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx"""
                    P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                # ═══════════════════════════════════════════════
                # ON/OFF
                # ═══════════════════════════════════════════════
                #تشغيل البوت أمر من الأدمن
                elif inPuTMsG.strip() == '/on':
                    if str(uid) != admin_uid:
                        await safe_send_message(XX, f"[B][C][FF0000]❌ هذا الأمر فقط للأدمن\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                    else:
                        bot_enabled = True
                        await safe_send_message(XX, f"[B][C][00FF00]✅ تم بدء البوت\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)

                #إيقاف البوت بأمر من الأدمن
                elif inPuTMsG.strip() == '/off':
                    if str(uid) != admin_uid:
                        await safe_send_message(XX, f"[B][C][FF0000]❌ هذا الأمر فقط للأدمن\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                    else:
                        bot_enabled = False
                        await safe_send_message(XX, f"[B][C][FF0000]⛔ تم إيقاف البوت\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # SQUAD
                # ═══════════════════════════════════════════════
                #دخول البوت للسكواد
                elif inPuTMsG.startswith('/join '):
                    try:
                        code = inPuTMsG.split('/join ')[1].strip()
                        EM = await JoinSq_original(code, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', EM)
                        await safe_send_message(XX, f"[B][C]{get_random_color()}\n✅ تم الدخول للسكواد\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                    except Exception as e:
                        print(f"Join error: {e}")

                #الخروج من السكواد
                elif inPuTMsG.startswith('/exit') or inPuTMsG.startswith('/leave'):
                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(uid, key, iv))
                    await safe_send_message(XX, f"[B][C]{get_random_color()}\n✅ تم الخروج من السكواد\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)

                #خمسة في السكواد
                elif inPuTMsG.startswith('/5') and not inPuTMsG.startswith('/50'):
                    try:
                        await safe_send_message(XX, f"[B][C]{get_random_color()}\n\nجار انشاء سكواد من 5 أشخاص ...\n", uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(uid, key, iv))
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await OpEnSq(key, iv, region))
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await cHSq(5, uid, key, iv, region))
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await SEnd_InV(5, uid, key, iv, region))
                        await asyncio.sleep(3.5)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(None, key, iv))
                        await safe_send_message(XX, f"[B][C][00FF00]✅ تم إرسال دعوة لفريق مكون من 5 أشخاص\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                    except Exception as e:
                        print(f"Team5 error: {e}")

                # ═══════════════════════════════════════════════
                # SPAM
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/spam '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        tgt = parts[1]
                        if tgt in spm_tasks:
                            spm_tasks[tgt].cancel()
                        spam_targets.add(tgt)
                        save_spam_targets()
                        spm_tasks[tgt] = asyncio.create_task(spm_loop(tgt, key, iv))
                        await safe_send_message(XX, f"[B][C]{get_random_color()}✅ تم بدء السبام\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                    else:
                        await safe_send_message(XX, f"[B][C][FF0000]أكتب : /spam <uid>\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)

                elif inPuTMsG.startswith('/stp '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1] in spm_tasks:
                        spm_tasks[parts[1]].cancel()
                        del spm_tasks[parts[1]]
                        if parts[1] in spam_targets:
                            spam_targets.remove(parts[1])
                            save_spam_targets()
                        await safe_send_message(XX, f"[B][C]{get_random_color()}✅ تم ايقاف السبام\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                    else:
                        await safe_send_message(XX, f"[B][C][FF0000]❌ لا يوجد سبام نشط لهذا الأيدي\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # GHOST
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/gh '):
                    parts = inPuTMsG.split(' ', 2)
                    if len(parts) >= 3 and bot_uid is not None:
                        teamcode = parts[1].strip()
                        name = parts[2].strip()
                        try:
                            pending_ghost_future = asyncio.Future()
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await JoinSq_original(teamcode, key, iv))
                            try:
                                await asyncio.wait_for(pending_ghost_future, timeout=8.0)
                            except asyncio.TimeoutError:
                                await safe_send_message(XX, f"[B][C][FF0000]❌ No response", uid, chat_id, key, iv)
                                pending_ghost_future = None
                                continue
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(None, key, iv))
                            await asyncio.sleep(0.2)
                            for _ in range(4):
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await GhostPakcet(ghost_team_id, name, ghost_squad_code, key, iv))
                                await asyncio.sleep(0.1)
                            await safe_send_message(XX, f"[B][C][00FF00]✅ Ghost joined as ", uid, chat_id, key, iv)
                            pending_ghost_future = None
                        except Exception as e:
                            await safe_send_message(XX, f"[B][C][FF0000]❌ {e}", uid, chat_id, key, iv)
                            pending_ghost_future = None

 
                # ═══════════════════════════════════════════════
                # MSG SPAM
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/msg '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) < 3:
                        await safe_send_message(XX, f"[B][C][FF0000]أكتب : /msg <text> <number>\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                    else:
                        try:
                            times = int(parts[-1])
                            message = ' '.join(parts[1:-1])
                            if msg_spam_task and not msg_spam_task.done():
                                msg_spam_running = False
                                msg_spam_task.cancel()
                                await asyncio.sleep(0.1)
                            msg_spam_running = True
                            msg_spam_task = asyncio.create_task(msg_spam_loop(message, times, chat_id, key, iv, region))
                            await safe_send_message(XX, f"[B][C]{get_random_color()}✅ Sending {times}x: {message}\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                        except ValueError:
                            await safe_send_message(XX, f"[B][C][FF0000]أكتب : /msg <text> <number>\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)

                elif inPuTMsG.strip() == '/stm':
                    if msg_spam_task and not msg_spam_task.done():
                        msg_spam_running = False
                        msg_spam_task.cancel()
                        await safe_send_message(XX, f"[B][C][00FF00]✅ تم إيقاف سبام الرسائل\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # EVO
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/evos'):
                    parts = inPuTMsG.strip().split()
                    uids = [str(uid)]
                    for p in parts[1:]:
                        if p.isdigit() and len(p) >= 7:
                            uids.append(p)
                    if evo_cycle_task and not evo_cycle_task.done():
                        evo_cycle_running = False
                        evo_cycle_task.cancel()
                        await asyncio.sleep(0.3)
                    evo_cycle_running = True
                    evo_cycle_task = asyncio.create_task(evo_gun_cycle(uids, EVO_IDS, key, iv, region))
                    await safe_send_message(XX, f"[B][C][00FF00]✅ تم بدء الرقص التلقائي\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)

                elif inPuTMsG.strip() == '/sevos':
                    if evo_cycle_task and not evo_cycle_task.done():
                        evo_cycle_running = False
                        evo_cycle_task.cancel()
                        await safe_send_message(XX, f"[B][C][00FF00]✅ تم إيقاف الرقص التلقائي\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # /e EMOTE COMMAND
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/e '):
                    parts = inPuTMsG.strip().split()
                    try:
                        if len(parts) < 2:
                            await safe_send_message(XX, f"[B][C][FF0000]أكتب : /e <uid> <name>\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                            continue
                        last = parts[-1].lower()
                        is_num = last.isdigit() and last in NUMBER_EMOTES
                        is_name = last in NAME_EMOTES
                        if not (is_num or is_name):
                            await safe_send_message(XX, f"[B][C][FF0000]❌ الرقصة '{last}' لا تعمل\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                            continue
                        tgt_uids = []
                        if len(parts) == 2:
                            tgt_uids.append(int(uid))
                        else:
                            for p in parts[1:-1]:
                                if p.isdigit():
                                    tgt_uids.append(int(p))
                        emote_id = NUMBER_EMOTES.get(last) if is_num else NAME_EMOTES.get(last)
                        sc = 0
                        for t in tgt_uids:
                            try:
                                H = await Emote_k(t, int(emote_id), key, iv, region)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                sc += 1
                                await asyncio.sleep(0.1)
                            except Exception:
                                pass
                        if sc > 0:
                            await safe_send_message(XX, f"[B][C][00FF00]✅ تم إرسال الرقصه {sc}\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                    except Exception as e:
                        print(f"E cmd error: {e}")

                # ═══════════════════════════════════════════════
                # /evo COMMAND
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/evo ') and not inPuTMsG.startswith('/evos'):
                    parts = inPuTMsG.strip().split()
                    try:
                        num = None
                        uids_l = []
                        for p in parts[1:]:
                            if p.isdigit():
                                if len(p) <= 2 and num is None:
                                    num = p
                                else:
                                    uids_l.append(p)
                        if not num or not uids_l:
                            await safe_send_message(XX, f"[B][C][FF0000]أكتب : /evo <uid> <1-21>\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                            continue
                        num_i = int(num)
                        if num_i not in EMOTE_MAP:
                            await safe_send_message(XX, f"[B][C][FF0000]❌ رقم الرقصة غير موجود 1-21\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                            continue
                        emote_id = EMOTE_MAP[num_i]
                        for t in uids_l:
                            try:
                                H = await Emote_k(int(t), int(emote_id), key, iv, region)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                await asyncio.sleep(0.1)
                            except Exception:
                                pass
                        await safe_send_message(XX, f"[B][C][00FF00]✅ الرقصة {num_i} تم إرسالها للاعب\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                    except Exception as e:
                        print(f"Evo error: {e}")

                # ═══════════════════════════════════════════════
                # TITLE
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/title'):
                    titles_list = [905090075, 904990072, 904990069, 905190079, 904090014,
                                   904090015, 904090024, 904090025, 904090026, 904090027,
                                   904990070, 904990071]
                    await safe_send_message(XX, f"[B][C][FFFF00]جار إرسال شارات الأنجازات {len(titles_list)} ...\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                    for tid in titles_list:
                        try:
                            pkt = await convert_kyro_to_your_system(int(uid), chat_id, key, iv, nickname="LINOX BOT", title_id=tid)
                            if pkt and whisper_writer:
                                whisper_writer.write(pkt)
                                await whisper_writer.drain()
                            await asyncio.sleep(2)
                        except Exception as e:
                            print(f"Title error: {e}")
                    await safe_send_message(XX, f"[B][C][00FF00]✅ تم إرسال شارات الأنجازات\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # BUNDLE
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/b '):
                    parts = inPuTMsG.strip().split()
                    bundle_ids = {"1": 914000002, "2": 914000003, "3": 914038001, "4": 914039001,
                                  "5": 914042001, "6": 914044001, "7": 914047001, "8": 914047002,
                                  "9": 914048001, "10": 914050001, "11": 914051001, "12": 914053001}
                    if len(parts) < 2:
                        await safe_send_message(XX, f"[B][C][FFFF00]إكتب : /b <1-12>\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                    elif parts[1] in bundle_ids:
                        bid = bundle_ids[parts[1]]
                        try:
                            anim_pkt = await animation_packet(bid, key, iv)
                            if anim_pkt and online_writer:
                                online_writer.write(anim_pkt); await online_writer.drain()
                            await asyncio.sleep(3)
                            b_pkt = await Look_Changer(bid, key, iv, look_type=1, region=region)
                            if b_pkt and online_writer:
                                online_writer.write(b_pkt); await online_writer.drain()
                            await safe_send_message(XX, f"[B][C][00FF00]✅ تم إرسال باقة اللبس رقم {parts[1]}\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                        except Exception as e:
                            print(f"Bundle error: {e}")
                    else:
                        await safe_send_message(XX, f"[B][C][FF0000]❌ رقم البطاقة غير صالح أو غير موجود\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # STICKER
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/sticker'):
                    try:
                        pkt = await send_sticker_packet(uid, chat_id, key, iv)
                        if pkt and whisper_writer:
                            whisper_writer.write(pkt); await whisper_writer.drain()
                    except Exception as e:
                        print(f"Sticker error: {e}")

                # ═══════════════════════════════════════════════
                # LATER (Love letter)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/hair '):
                    try:
                        name = inPuTMsG.strip()[7:].strip()
                        msg = f"[B][C][FF1493]{name}\n\nعَلَّقَ روحي روحَها قبلَ خَلقِنا\nومِن بعدِ ما كنّا نِطافًا وفي المَهدِ\nفزادَ كما زِدنا فأصبحَ ناميًا\nوليسَ إذا مِتنا بمُنْتَقِصِ العهدِ 💕\n"
                        P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                    except Exception as e:
                        print(f"Later error: {e}")

                # ═══════════════════════════════════════════════
                # INFO
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/info '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        await safe_send_message(XX, f"[B][C][FFFF00]جار البحث عن معلومات الاعب ...", uid, chat_id, key, iv)
                        await asyncio.sleep(3)
                        try:
                            ok, data = await get_player_info(parts[1])
                            if ok:
                                m0, m1, m2 = format_player_info(data)
                                for m in (m0, m1, m2):
                                    P = await SEndMsG(XX, m, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    await asyncio.sleep(0.5)
                            else:
                                await safe_send_message(XX, f"[B][C][FF0000]❌ {data}", uid, chat_id, key, iv)
                        except Exception as e:
                            await safe_send_message(XX, f"[B][C][FF0000]❌ Error: {e}", uid, chat_id, key, iv)
                    else:
                        await safe_send_message(XX, f"[B][C][FF0000]أكتب : /info <uid>\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # AI
                # ═══════════════════════════════════════════════
                
              

                elif inPuTMsG.strip().startswith('/ai '):
                    question = inPuTMsG.strip()[4:].strip()
                    if question:
                        await safe_send_message(XX, f"[B][C][FFFF00]🤖 الذكاء الاصطناعي يفكر ...", uid, chat_id, key, iv)
                        try:
                            # ترميز السؤال
                            encoded_question = urllib.parse.quote(question)
                            ai_url = f"https://text.pollinations.ai/{encoded_question}"
            
                            async with aiohttp.ClientSession() as session:
                                async with session.get(ai_url, timeout=aiohttp.ClientTimeout(total=20)) as r:
                                    if r.status == 200:
                                        answer = (await r.text()).strip()
                        
                                        # تقسيم النص إلى أجزاء
                                        chunk_size = 400
                                        chunks = [answer[i:i+chunk_size] for i in range(0, len(answer), chunk_size)]
                                        max_messages = 10
                                        chunks = chunks[:max_messages]
                        
                                        total_parts = len(chunks)
                                        for index, chunk in enumerate(chunks, 1):
                                            msg = f"[B][C][FFFF00] ({index}/{total_parts}):\n\n[FFFFFF]{chunk}"
                                            P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            
                                            # ⏱️ مهلة زمنية بين كل رسالة والأخرى (هنا 1.5 ثانية)
                                            if index < total_parts:  # لا داعي للانتظار بعد آخر رسالة
                                                await asyncio.sleep(1)
                            
                                    else:
                                        msg = f"[B][C][FF0000]❌ AI error: {r.status}"
                                        P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                        
                        except Exception as e:
                            msg = f"[B][C][FF0000]❌ Error: {e}"
                            P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                        
                # ═══════════════════════════════════════════════
                # MATH
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/mth'):
                    parts = inPuTMsG.strip().split(maxsplit=1)
                    if len(parts) < 2:
                        await safe_send_message(XX, f"[B][C][FFFF00]أكتب : /mth 2+2  or  5*3  or  10/2\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                    else:
                        expr = parts[1].strip().replace("×", "*").replace("÷", "/").replace("x", "*")
                        try:
                            import re as _re
                            if not _re.match(r'^[\d\s\+\-\*\/\.\(\)\%]+$', expr):
                                raise ValueError("Invalid expression")
                            result = eval(expr)
                            if isinstance(result, float) and result == int(result):
                                result = int(result)
                            P = await SEndMsG(XX, f"[B][C][00FFFF] الحاسبة\n\n[FFFFFF]{expr}\n\n[00FF00]الناتج : [FFFFFF]{result}", uid, chat_id, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                        except ZeroDivisionError:
                            await safe_send_message(XX, f"[B][C][FF0000]❌ لا يمكن القسمة على صفر\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                        except Exception:
                            await safe_send_message(XX, f"[B][C][FF0000]❌ تعبير غير صالح\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)


                # ═══════════════════════════════════════════════
                # ADD FRIEND (admin only)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith("/add ") and str(uid) == admin_uid:
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        try:
                            ok, msg = await send_friend_request(parts[1], ToKen, region)
                            reply = f"[B][C]{get_random_color()} {msg}"
                        except Exception as e:
                            reply = f"[B][C][FF0000]Error: {e}"
                    else:
                        reply = f"[B][C][FF0000]أكتب : /add <uid>\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx"
                    P = await SEndMsG(XX, reply, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                # ═══════════════════════════════════════════════
                # REMOVE FRIEND (admin only)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith("/remove ") and str(uid) == admin_uid:
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        try:
                            ok, msg = await remove_friend(parts[1], ToKen, region)
                            reply = f"[B][C]{get_random_color()} {msg}"
                        except Exception as e:
                            reply = f"[B][C][FF0000]Error: {e}"
                    else:
                        reply = f"[B][C][FF0000]أكتب : /remove <uid>\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx"
                    P = await SEndMsG(XX, reply, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                # ═══════════════════════════════════════════════
                # love
                # ═══════════════════════════════════════════════
                
                elif inPuTMsG.strip().startswith('/love '):
                    try:
                        name = inPuTMsG.strip()[6:].strip()
                        msgs = [
                            f"[B][C][FF1493]❤️ {name} أنت روحي! ❤️",
f"[B][C][FF66CC]💕 أنا لا شيء بدونك {name} ! 💕",
f"[B][C][FF00FF]💖 أنت كل شيء بالنسبة لي {name} ! 💖",
f"[B][C][FF69B4]💗 أنت عالمي {name} ! 💗",
f"[B][C][FF1493]💘 أحبك كثيرًا {name} ! 💘",
f"[B][C][FF66CC]💝 أنت حياتي {name} ! 💝",
f"[B][C][FF00FF]❤️‍🔥 أنت نبض قلبي {name} ! ❤️‍🔥",
f"[B][C][FF69B4]💞 سأبقى لك وحدك دائما {name}! 💞",
                        ]
                        for m in msgs:
                            P = await SEndMsG(XX, m, uid, chat_id, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            await asyncio.sleep(1.5)
                    except Exception as e:
                        print(f"Love error: {e}")
                
                # ═══════════════════════════════════════════════
                # hair
                # ═══════════════════════════════════════════════
                                
                elif inPuTMsG.strip().startswith('/hair '):
                    try:
                        name = inPuTMsG.strip()[7:].strip()
                        msg = f"[B][C][FF1493]{name}\n\nألا يا صبا نجدٍ متى هجتَ من نجد\nلقد زادني مسراكَ وجداً على وجد"
                        P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                    except Exception as e:
                        print(f"Later error: {e}")                                                                             
                        
  
                             
                 # ═══════════════════════════════════════════════
                # CHECK
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/check '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        try:
                            ok, result = await check_banned(parts[1])
                            reply = format_check_result(result) if ok else f"[B][C][FF0000]❌ {result}"
                        except Exception as e:
                            reply = f"[B][C][FF0000]❌ Error: {e}"
                        P = await SEndMsG(XX, reply, uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                    else:
                        await safe_send_message(XX, f"[B][C][FF0000]أكتب : /check <uid>", uid, chat_id, key, iv)                                                                                                  
                 # ═══════════════════════════════════════════════
                #ghost
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/ghost '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        try:
                            ok, result = await ghost(parts[1])
                            reply = format_ghostt(result) if ok else f"[B][C][FF0000]❌ {result}"
                        except Exception as e:
                            reply = f"[B][C][FF0000]❌ Error: {e}"
                        P = await SEndMsG(XX, reply, uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                    else:
                        await safe_send_message(XX, f"[B][C][FF0000]أكتب : /ghost <uid>", uid, chat_id, key, iv)                                                 
                                            
                 # ═══════════════════════════════════════════════
                #like bot
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/like '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        try:
                            ok, result = await like_bot(parts[1])
                            reply = format_like_bott(result) if ok else f"[B][C][FF0000]❌ {result}"
                        except Exception as e:
                            reply = f"[B][C][FF0000]❌ Error: {e}"
                        P = await SEndMsG(XX, reply, uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                    else:
                        await safe_send_message(XX, f"[B][C][FF0000]أكتب : /like <uid>", uid, chat_id, key, iv)               
                
                
                # ═══════════════════════════════════════════════
                # ROOM
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/room '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 3:
                        tgt = parts[1]
                        rid = parts[2]
                        try:
                            for i in range(3000):
                                spam_p = await Room_Spam(tgt, rid, "LINOX BOT", key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', spam_p)
                                if (i + 1) % 50 == 0:
                                    print(f"Room spam progress: {i+1}/3000")
                                await asyncio.sleep(0.05)
                            await safe_send_message(XX, f"[B][C][00FF00]✅ تم بدء السلام على الاعب في الغرفة\n—————————————\n[b][c][00ffff]للتواصل مع المطورين :\n\n[b][c][40E0D0]TELEGRAM : @linoxxcheat777\n[b][c][40E0D0]INSTAGRAM : y9yasserx", uid, chat_id, key, iv)
                        except Exception as e:
                            print(f"Room spam error: {e}")

                # Unknown command fallback
                else:
                    if inPuTMsG.strip().startswith('/') and len(inPuTMsG.strip()) > 2:
                        # Unknown command - ignore quietly
                        pass

            writer.close(); await writer.wait_closed(); whisper_writer = None
        except Exception as e:
            print(f"Chat error: {ip}:{port} - {e}")
            whisper_writer = None
        await asyncio.sleep(reconnect_delay)