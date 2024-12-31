import logging
import os
import re
import io
import math
import json
import platform
import asyncio
from datetime import datetime

import aiohttp
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError

from telegram import (
    Update,
    BotCommand,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    filters,
    CallbackQueryHandler
)
from telegram import InputMediaPhoto


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


os.system("title Code Created By Kayy / discord.gg/KayyShop")

pending_link_changes = set()

Image.MAX_IMAGE_PIXELS = None

pending_logo_changes = set()

VERIFICATION_COUNT_FILE = "verification_countstele.json"


USER_CONFIG_FOLDER = "user_config"

def get_user_config_path(telegram_user_id: int) -> str:
    user_dir = os.path.join(USER_CONFIG_FOLDER, str(telegram_user_id))
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, "config.json")

def load_user_config(telegram_user_id: int) -> dict:
    config_path = get_user_config_path(telegram_user_id)
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {"rarity_version": "v1"}

def save_user_config(telegram_user_id: int, config: dict):
    config_path = get_user_config_path(telegram_user_id)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


def load_verification_counts():
    if os.path.exists(VERIFICATION_COUNT_FILE):
        with open(VERIFICATION_COUNT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_verification_counts(counts):
    with open(VERIFICATION_COUNT_FILE, "w") as f:
        json.dump(counts, f)

async def send_webhook_message(webhook_url: str, message: str):
    async with aiohttp.ClientSession() as session:
        webhook_data = {"content": message}
        async with session.post(webhook_url, json=webhook_data) as resp:
            if resp.status != 204:
                print(f"Error sending message to webhook: {resp.status}")

def bool_to_emoji(value):
    return "✅" if value else "❌"

def country_to_flag(country_code):
    if len(country_code) != 2:
        return country_code
    return chr(ord(country_code[0]) + 127397) + chr(ord(country_code[1]) + 127397)

def mask_email(email):
    if "@" in email:
        local_part, domain = email.split("@")
        if len(local_part) > 2:
            masked_local_part = local_part[0] + "*" * (len(local_part) - 2) + local_part[-1]
        elif len(local_part) == 2:
            masked_local_part = local_part[0] + "*"
        else:
            masked_local_part = local_part
        return f"{masked_local_part}@{domain}"
    return email

def mask_account_id(account_id):
    if len(account_id) > 4:
        return account_id[:2] + "*" * (len(account_id) - 4) + account_id[-2:]
    return account_id

SWITCH_TOKEN = "OThmN2U0MmMyZTNhNGY4NmE3NGViNDNmYmI0MWVkMzk6MGEyNDQ5YTItMDAxYS00NTFlLWFmZWMtM2U4MTI5MDFjNGQ3"
IOS_TOKEN = "M2Y2OWU1NmM3NjQ5NDkyYzhjYzI5ZjFhZjA4YThhMTI6YjUxZWU5Y2IxMjIzNGY1MGE2OWVmYTY3ZWY1MzgxMmU="
idpattern = re.compile(r"athena(.*?):(.*?)_(.*?)")

current_dir = os.path.dirname(__file__)

rarity_backgroundsV1 = {
    "Common": os.path.join(current_dir, "Cuadrados", "CuadradosV1", "commun.png"),
    "Uncommon": os.path.join(current_dir, "Cuadrados", "CuadradosV1", "uncommun.png"),
    "Rare": os.path.join(current_dir, "Cuadrados", "CuadradosV1", "rare.png"),
    "Epic": os.path.join(current_dir, "Cuadrados", "CuadradosV1", "epico.png"),
    "Legendary": os.path.join(current_dir, "Cuadrados", "CuadradosV1", "legendary.png"),
    "Mythic": os.path.join(current_dir, "Cuadrados", "CuadradosV1", "mitico.png"),
    "Icon Series": os.path.join(current_dir, "Cuadrados", "CuadradosV1", "idolo.png"),
    "DARK SERIES": os.path.join(current_dir, "Cuadrados", "CuadradosV1", "dark.png"),
    "Star Wars Series": os.path.join(current_dir, "Cuadrados", "CuadradosV1", "starwars.png"),
    "MARVEL SERIES": os.path.join(current_dir, "Cuadrados", "CuadradosV1", "marvel.png"),
    "DC SERIES": os.path.join(current_dir, "Cuadrados", "CuadradosV1", "dc.png"),
    "Gaming Legends Series": os.path.join(current_dir, "Cuadrados", "CuadradosV1", "serie.png"),
    "Shadow Series": os.path.join(current_dir, "Cuadrados", "CuadradosV1", "shadow.png"),
    "Slurp Series": os.path.join(current_dir, "Cuadrados", "CuadradosV1", "slurp.png"),
    "Lava Series": os.path.join(current_dir, "Cuadrados", "CuadradosV1", "lava.png"),
    "Frozen Series": os.path.join(current_dir, "Cuadrados", "CuadradosV1", "hielo.png")
}

rarity_backgroundsV2 = {
    "Common": os.path.join(current_dir, "Cuadrados", "CuadradosV2", "commun.png"),
    "Uncommon": os.path.join(current_dir, "Cuadrados", "CuadradosV2", "uncommun.png"),
    "Rare": os.path.join(current_dir, "Cuadrados", "CuadradosV2", "rare.png"),
    "Epic": os.path.join(current_dir, "Cuadrados", "CuadradosV2", "epico.png"),
    "Legendary": os.path.join(current_dir, "Cuadrados", "CuadradosV2", "legendary.png"),
    "Mythic": os.path.join(current_dir, "Cuadrados", "CuadradosV2", "mitico.png"),
    "Icon Series": os.path.join(current_dir, "Cuadrados", "CuadradosV2", "idolo.png"),
    "DARK SERIES": os.path.join(current_dir, "Cuadrados", "CuadradosV2", "dark.png"),
    "Star Wars Series": os.path.join(current_dir, "Cuadrados", "CuadradosV2", "starwars.png"),
    "MARVEL SERIES": os.path.join(current_dir, "Cuadrados", "CuadradosV2", "marvel.png"),
    "DC SERIES": os.path.join(current_dir, "Cuadrados", "CuadradosV2", "dc.png"),
    "Gaming Legends Series": os.path.join(current_dir, "Cuadrados", "CuadradosV2", "serie.png"),
    "Shadow Series": os.path.join(current_dir, "Cuadrados", "CuadradosV2", "shadow.png"),
    "Slurp Series": os.path.join(current_dir, "Cuadrados", "CuadradosV2", "slurp.png"),
    "Lava Series": os.path.join(current_dir, "Cuadrados", "CuadradosV2", "lava.png"),
    "Frozen Series": os.path.join(current_dir, "Cuadrados", "CuadradosV2", "hielo.png")
}

rarity_priority = {
    "Mythic": 1,
    "Legendary": 2,
    "DARK SERIES": 3,
    "Slurp Series": 4,
    "Star Wars Series": 5,
    "MARVEL SERIES": 6,
    "Lava Series": 7,
    "Frozen Series": 8,
    "Gaming Legends Series": 9,
    "Shadow Series": 10,
    "Icon Series": 11,
    "DC SERIES": 12,
    "Epic": 13,
    "Rare": 14,
    "Uncommon": 15,
    "Common": 16
}

sub_order = {
    "cid_017_athena_commando_m": 1,
    "cid_028_athena_commando_f": 2,
    "cid_029_athena_commando_f_halloween": 3,
    "cid_030_athena_commando_m_halloween": 4,
    "cid_035_athena_commando_m_medieval": 5,
    "cid_039_athena_commando_f_disco": 6,
    "cid_033_athena_commando_f_medieval": 7,
    "cid_032_athena_commando_m_medieval": 8,
    "cid_084_athena_commando_m_assassin": 9,
    "cid_095_athena_commando_m_founder": 10,
    "cid_096_athena_commando_f_founder": 11,
    "cid_113_athena_commando_m_blueace": 12,
    "cid_116_athena_commando_m_carbideblack": 13,
    "cid_175_athena_commando_m_celestial": 14,
    "cid_183_athena_commando_m_modernmilitaryred": 15,
    "cid_313_athena_commando_m_kpopfashion": 16,
    "cid_342_athena_commando_m_streetracermetallic": 17,
    "cid_371_athena_commando_m_speedymidnight": 18,
    "cid_434_athena_commando_f_stealthhonor": 19,
    "cid_441_athena_commando_f_cyberscavengerblue": 20,
    "cid_479_athena_commando_f_davinci": 21,
    "cid_515_athena_commando_m_barbequelarry": 22,
    "cid_516_athena_commando_m_blackwidowrogue": 23,
    "cid_703_athena_commando_m_cyclone": 24,
    "cid_npc_athena_commando_m_masterkey": 25,
}

mythic_ids = [
    "cid_017_athena_commando_m", "cid_028_athena_commando_f", "eid_tidy",
    "cid_032_athena_commando_m_medieval", "cid_033_athena_commando_f_medieval", "cid_035_athena_commando_m_medieval",
    "cid_a_256_athena_commando_f_uproarbraids_8iozw", "cid_030_athena_commando_m_halloween", "cid_029_athena_commando_f_halloween",
    "cid_052_athena_commando_f_psblue", "cid_095_athena_commando_m_founder", "cid_096_athena_commando_f_founder", "cid_138_athena_commando_m_psburnou", 
    "cid_260_athena_commando_f_streetops", "cid_315_athena_commando_m_teriyakifish", "cid_399_athena_commando_f_ashtonboardwalk", "cid_619_athena_commando_f_techllama",
    "cid_a_024_athena_commando_f_skirmish_qw2bq", "cid_a_101_athena_commando_m_tacticalwoodlandblue", "cid_a_215_athena_commando_f_sunrisecastle_48tiz",
    "cid_a_216_athena_commando_m_sunrisepalace_bbqy0", "pickaxe_id_stw004_tier_5", "pickaxe_id_stw005_tier_6", "cid_925_athena_commando_f_tapdance",
    "bid_072_vikingmale", "cid_138_athena_commando_m_psburnout", "pickaxe_id_stw001_tier_1", "pickaxe_id_stw002_tier_3", "pickaxe_id_stw003_tier_4",
    "pickaxe_id_stw007_basic", "pickaxe_id_153_roseleader", "pickaxe_id_461_skullbritecube", "glider_id_211_wildcatblue", "glider_id_206_donut"
    "cid_113_athena_commando_m_blueace", "cid_114_athena_commando_f_tacticalwoodland", "cid_175_athena_commando_m_celestial", "cid_089_athena_commando_m_retrogrey",
    "cid_174_athena_commando_f_carbidewhite", "cid_183_athena_commando_m_modernmilitaryred", "cid_207_athena_commando_m_footballdudea", "eid_worm",
    "cid_208_athena_commando_m_footballdudeb", "cid_209_athena_commando_m_footballdudec", "cid_210_athena_commando_f_footballgirla",
    "cid_211_athena_commando_f_footballgirlb", "cid_212_athena_commando_f_footballgirlc", "cid_238_athena_commando_f_footballgirld", 
    "cid_239_athena_commando_m_footballduded", "cid_240_athena_commando_f_plague", "cid_313_athena_commando_m_kpopfashion", "cid_082_athena_commando_m_scavenger",
     "cid_090_athena_commando_m_tactical", "cid_657_athena_commando_f_techopsblue", "cid_371_athena_commando_m_speedymidnight", "cid_085_athena_commando_m_twitch",
    "cid_342_athena_commando_m_streetracermetallic", "cid_434_athena_commando_f_stealthhonor", "cid_441_athena_commando_f_cyberscavengerblue", "cid_479_athena_commando_f_davinci",
    "cid_478_athena_commando_f_worldcup", "cid_515_athena_commando_m_barbequelarry", "cid_516_athena_commando_m_blackwidowrogue", "cid_657_athena_commando_f_techOpsBlue",
    "cid_619_athena_commando_f_techllama", "cid_660_athena_commando_f_bandageninjablue", "cid_703_athena_commando_m_cyclone", "cid_084_athena_commando_m_assassin", "cid_083_athena_commando_f_tactical",
    "cid_761_athena_commando_m_cyclonespace", "cid_783_athena_commando_m_aquajacket", "cid_964_athena_commando_m_historian_869bc", "cid_084_athena_commando_m_assassin", "cid_039_athena_commando_f_disco",
    "eid_ashtonboardwalk", "eid_ashtonsaltlake", "eid_bendy", "eid_bollywood", "eid_chicken", "cid_757_athena_commando_f_wildcat",  "cid_080_athena_commando_m_space",
    "eid_crackshotclock", "eid_dab", "eid_fireworksspin", "eid_fresh", "eid_griddles", "eid_hiphop01", "eid_iceking", "eid_kpopdance03",
    "eid_macaroon_45lhe", "eid_ridethepony_athena", "eid_robot", "eid_rockguitar", "eid_solartheory", "eid_taketheL", "eid_tapshuffle", "cid_386_athena_commando_m_streetopsstealth",
    "eid_torchsnuffer", "eid_trophycelebrationfncs", "eid_trophycelebration", "eid_twistdaytona", "eid_zest_q1k5v", "founderumbrella",
    "founderglider", "glider_id_001", "glider_id_002_medieval", "glider_id_003_district", "glider_id_004_disco", "glider_id_014_dragon",
    "glider_id_090_celestial", "glider_id_176_blackmondaycape_4p79k", "glider_id_206_donut", "umbrella_snowflake", "glider_warthog",
    "glider_voyager", "bid_001_bluesquire", "bid_002_royaleknight", "bid_004_blackknight", "bid_005_raptor", "bid_025_tactical", "eid_electroshuffle", "cid_850_athena_commando_f_skullbritecube",
    "bid_024_space", "bid_027_scavenger", "bid_029_retrogrey", "bid_030_tacticalrogue", "bid_055_psburnout", "bid_072_vikingmale",
    "bid_103_clawed", "bid_102_buckles", "bid_138_celestial", "bid_468_cyclone", "bid_520_cycloneuniverse", "halloweenscythe", "eid_floss",
    "pickaxe_id_013_teslacoil", "pickaxe_id_015_holidaycandycane", "pickaxe_id_021_megalodon", "pickaxe_id_019_heart", "cid_116_athena_commando_m_carbideblack",
    "pickaxe_id_029_assassin", "pickaxe_id_077_carbidewhite", "pickaxe_id_088_psburnout", "pickaxe_id_116_celestial", "pickaxe_id_011_medieval", "eid_takethel",
    "pickaxe_id_294_candycane", "pickaxe_id_359_cyclonemale", "pickaxe_id_376_fncs", "pickaxe_id_508_historianmale_6bqsw",
    "pickaxe_id_804_fncss20male", "pickaxe_id_stw007_basic","cid_259_athena_commando_m_streetops", "pickaxe_lockjaw"
]

converted_mythic_ids = []

class EpicUser:
    def __init__(self, data: dict = {}):
        self.raw = data
        self.access_token = data.get("access_token", "")
        self.expires_in = data.get("expires_in", 0)
        self.expires_at = data.get("expires_at", "")
        self.token_type = data.get("token_type", "")
        self.refresh_token = data.get("refresh_token", "")
        self.refresh_expires = data.get("refresh_expires", "")
        self.refresh_expires_at = data.get("refresh_expires_at", "")
        self.account_id = data.get("account_id", "")
        self.client_id = data.get("client_id", "")
        self.internal_client = data.get("internal_client", False)
        self.client_service = data.get("client_service", "")
        self.display_name = data.get("displayName", "")
        self.app = data.get("app", "")
        self.in_app_id = data.get("in_app_id", "")

class EpicGenerator:
    def __init__(self) -> None:
        self.http: aiohttp.ClientSession
        self.user_agent = f"DeviceAuthGenerator/{platform.system()}/{platform.version()}"
        self.access_token = ""

    async def start(self) -> None:
        self.http = aiohttp.ClientSession(headers={"User-Agent": self.user_agent})
        self.access_token = await self.get_access_token()

    async def get_access_token(self) -> str:
        async with self.http.request(
            method="POST",
            url="https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"basic {SWITCH_TOKEN}",
            },
            data={
                "grant_type": "client_credentials",
            },
        ) as response:
            data = await response.json()
            return data["access_token"]

    async def create_device_code(self) -> tuple:
        async with self.http.request(
            method="POST",
            url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/deviceAuthorization",
            headers={
                "Authorization": f"bearer {self.access_token}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        ) as response:
            data = await response.json()
            return data["verification_uri_complete"], data["device_code"]

    async def create_exchange_code(self, user: 'EpicUser') -> str:
        async with self.http.request(
            method="GET",
            url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/exchange",
            headers={"Authorization": f"bearer {user.access_token}"},
        ) as response:
            data = await response.json()
            return data["code"]

    async def wait_for_device_code_completion(self, code: str) -> 'EpicUser':
        while True:
            async with self.http.request(
                method="POST",
                url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token",
                headers={
                    "Authorization": f"basic {SWITCH_TOKEN}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={"grant_type": "device_code", "device_code": code},
            ) as request:
                token = await request.json()

                if request.status == 200:
                    break
                await asyncio.sleep(5)

        async with self.http.request(
            method="GET",
            url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/exchange",
            headers={"Authorization": f"bearer {token['access_token']}"},
        ) as request:
            exchange = await request.json()

        async with self.http.request(
            method="POST",
            url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token",
            headers={
                "Authorization": f"basic {IOS_TOKEN}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "exchange_code",
                "exchange_code": exchange["code"],
            },
        ) as request:
            auth_information = await request.json()
            return EpicUser(data=auth_information)

    async def create_device_auths(self, user: 'EpicUser') -> dict:
        async with self.http.request(
            method="POST",
            url="https://account-public-service-prod.ol.epicgames.com/"
                f"account/api/public/account/{user.account_id}/deviceAuth",
            headers={
                "Authorization": f"bearer {user.access_token}",
                "Content-Type": "application/json",
            },
        ) as request:
            data = await request.json()

        return {
            "device_id": data["deviceId"],
            "account_id": data["accountId"],
            "secret": data["secret"],
            "user_agent": data["userAgent"],
            "created": {
                "location": data["created"]["location"],
                "ip_address": data["created"]["ipAddress"],
                "datetime": data["created"]["dateTime"],
            },
        }

async def get_cosmetic_info(cosmetic_id: str, session: aiohttp.ClientSession) -> dict:
    async with session.get(f"https://fortnite-api.com/v2/cosmetics/br/{cosmetic_id}") as resp:
        if resp.status != 200:
            return {"id": cosmetic_id, "rarity": "Common", "name":[]}
        data = await resp.json()
        rarity = data.get("data", {}).get("rarity", {}).get("displayValue", "Common")
        name = data.get("data", {}).get("name", "Unknown")
        if cosmetic_id.lower() in mythic_ids:
            rarity = "Mythic"
        if name == "Unknown":
            name = cosmetic_id
        
        return {"id": cosmetic_id, "rarity": rarity, "name": name}

async def download_cosmetic_images(ids: list, session: aiohttp.ClientSession):
    async def _dl(id: str):
        imgpath = f"./cache/{id}.png"
        if not os.path.exists(imgpath) or not os.path.isfile(imgpath) or os.path.getsize(imgpath) == 0:
            urls = [
                f"https://fortnite-api.com/images/cosmetics/br/{id}/icon.png",
                f"https://fortnite-api.com/images/cosmetics/br/{id}/smallicon.png"
            ]
            for url in urls:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        with open(imgpath, "wb") as f:
                            f.write(content)
                        logger.info(f"Downloaded image for {id} from {url}")
                        return
                logger.warning(f"Failed to download {id} from {url}")
            else:
                with open(imgpath, "wb") as f:
                    f.write(open("./tbd.png", "rb").read())
                logger.warning(f"Image not found for {id}, using placeholder")

    await asyncio.gather(*[_dl(id) for id in ids])

async def set_affiliate(session: aiohttp.ClientSession, account_id: str, access_token: str, affiliate_name: str = "Kaayyy") -> dict:
    async with session.post(
        f"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{account_id}/client/SetAffiliateName?profileId=common_core",
        headers={
            "Authorization": f"Bearer {access_token}",
            "content-type": "application/json"
        },
        json={"affiliateName": affiliate_name}
    ) as resp:
        if resp.status != 200:
            return f"Error setting affiliate name ({resp.status})"
        else:
            return await resp.json()

async def grabprofile(session: aiohttp.ClientSession, info: dict, profileid: str = "athena") -> dict:
    async with session.post(
        f"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{info['account_id']}/client/QueryProfile?profileId={profileid}",
        headers={
            "Authorization": f"bearer {info['access_token']}",
            "content-type": "application/json"
        },
        json={}
    ) as resp:
        if resp.status != 200:
            return f"Error ({resp.status})"
        else:
            profile_data = await resp.json()
            return profile_data

def get_cosmetic_type(cosmetic_id):
    if "character_" in cosmetic_id or "cid" in cosmetic_id:
        return "Skins"
    elif "bid_" in cosmetic_id or "backpack" in cosmetic_id:
        return "Mochilas"
    elif (
        "pickaxe_" in cosmetic_id or "pickaxe_id_" in cosmetic_id or 
        "DefaultPickaxe" in cosmetic_id or "HalloweenScythe" in cosmetic_id or
        "HappyPickaxe" in cosmetic_id or "SickleBatPickaxe" in cosmetic_id or
        "SkiIcePickaxe" in cosmetic_id or "SpikyPickaxe" in cosmetic_id
    ):
        return "Picos"
    elif "eid" in cosmetic_id or "emote" in cosmetic_id:
        return "Gestos"
    elif (
        "glider" in cosmetic_id or
        "founderumbrella" in cosmetic_id or
        "founderglider" in cosmetic_id or
        "solo_umbrella" in cosmetic_id
    ):
        return "Planeadores"
    elif "wrap" in cosmetic_id:
        return "Envolturas"
    elif "spray" in cosmetic_id:
        return "Sprays"
    else:
        return "Others"

async def sort_ids_by_rarity(ids: list, session: aiohttp.ClientSession, item_order: list) -> list:
    cosmetic_info_tasks = [get_cosmetic_info(id, session) for id in ids]
    info_list = await asyncio.gather(*cosmetic_info_tasks)
    
    def get_sort_key(info):
        rarity = info.get("rarity", "Common")
        cosmetic_id = info.get("id", "")
        t = get_cosmetic_type(cosmetic_id)
        item_order_rank = item_order.index(t) if t in item_order else len(item_order)
        rarity_rank = rarity_priority.get(rarity, 999)
        sub_rank = sub_order.get(cosmetic_id, 9999)
        
        logger.debug(f"ID: {cosmetic_id} - Rareza: {rarity} - Sub Rank: {sub_rank}")
        return (item_order_rank, rarity_rank, sub_rank)
    
    sorted_info_list = sorted(info_list, key=get_sort_key)
    return [info["id"] for info in sorted_info_list]

def filter_mythic_ids_func(items, converted_mythic_ids):
    mythic_items = []
    for item_type, ids_list in items.items():
        for cid in ids_list:
            if cid.lower() in mythic_ids or cid in converted_mythic_ids:
                mythic_items.append(cid)
    return mythic_items

directorio_actual = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(directorio_actual, "fonts", "font.ttf")

def calculate_font_size(name: str, base_size: int = 40, special: bool = False) -> int:
    if special:
        length = len(name)
        if length <= 5:
            return int(base_size * 0.5)
        elif length <= 10:
            return int(base_size * 0.5)
        elif length <= 4:
            return int(base_size * 0.7)
        elif length <= 15:
            return int(base_size * 1.2)
        else:
            return int(base_size * 1.5)
    else:
        return base_size

def combine_with_background(foreground: Image.Image, background: Image.Image, name: str, rarity: str) -> Image.Image:
    logger.info(f"Combining image {name} with background")
    bg = background.convert("RGBA")
    fg = foreground.convert("RGBA")
    fg = fg.resize(bg.size, Image.Resampling.LANCZOS)

    bg.paste(fg, (0, 0), fg)
    draw = ImageDraw.Draw(bg)

    special_rarities = {
        "ICON SERIES", "DARK SERIES", "STAR WARS SERIES","GAMING LEGENDS SERIES", "MARVEL SERIES", "DC SERIES",
        "SHADOW SERIES", "SLURP SERIES", "LAVA SERIES", "FROZEN SERIES"
    }

    base_max_font_size = 40
    if rarity.upper() in special_rarities:
        max_font_size = calculate_font_size(name, base_size=base_max_font_size, special=True)
    else:
        max_font_size = base_max_font_size

    min_font_size = 10
    max_text_width = bg.width - 20
    font_size = max_font_size

    name = name.upper()
    while font_size > min_font_size:
        try:
            font = ImageFont.truetype(FONT_PATH, size=font_size)
        except IOError:
            logger.error(f"Fuente no encontrada en {FONT_PATH}. Asegúrate de que la fuente exista.")
            return bg

        text_bbox = draw.textbbox((0, 0), name, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

        if text_width <= max_text_width:
            break

        font_size -= 1

    font = ImageFont.truetype(FONT_PATH, size=font_size)
    text_bbox = draw.textbbox((0, 0), name, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    text_x = (bg.width - text_width) // 2

    muro_y_position = int(bg.height * 0.80)
    muro_height = bg.height - muro_y_position

    muro = Image.new('RGBA', (bg.width, muro_height), (0, 0, 0, int(255 * 0.7)))
    bg.paste(muro, (0, muro_y_position), muro)

    text_y = muro_y_position + (muro_height - text_height) // 2

    draw.text((text_x, text_y), name, fill="white", font=font)

    logger.info(f"Combined image {name} with background successfully")
    return bg

def combine_images(images, username: str, item_count: int, logo_filename="logo.png", show_fake_text: bool = False, custom_link: str = "Discord.gg/KayyShop"):
    max_width = 1848
    max_height = 2048

    num_items = len(images)
    base_max_cols = 6
    max_cols = base_max_cols
    num_rows = math.ceil(num_items / max_cols)

    while num_rows > max_cols:
        max_cols += 1
        num_rows = math.ceil(num_items / max_cols)

    while num_rows > max_cols:
        max_cols += 1
        num_rows += 1

    item_width = max_width // max_cols
    item_height = max_height // num_rows

    image_size = min(item_width, item_height)
    spacing = 0

    total_width = max_cols * image_size + (max_cols - 1) * spacing
    total_height = num_rows * image_size + (num_rows - 1) * spacing

    empty_space_height = image_size
    total_height += empty_space_height

    combined_image = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 255))

    for idx, image in enumerate(images):
        col = idx % max_cols
        row = idx // max_cols
        position = (col * (image_size + spacing), row * (image_size + spacing))
        resized_image = image.resize((image_size, image_size))
        combined_image.paste(resized_image, position, resized_image)

    try:
        logo = Image.open(logo_filename).convert("RGBA")
    except FileNotFoundError:
        logger.error(f"Logo file '{logo_filename}' not found. Using placeholder.")
        logo = Image.new("RGBA", (100, 100), (255, 255, 255, 255))

    logo_height = int(empty_space_height * 0.6)
    logo_width = int((logo_height / logo.height) * logo.width)
    logo_position = (10, total_height - empty_space_height + (empty_space_height - logo_height) // 2)

    logo = logo.resize((logo_width, logo_height))
    combined_image.paste(logo, logo_position, logo)

    text1 = f"Objetos Totales: {item_count}"
    text2 = f"Checkeado Por {username} | {datetime.now().strftime('%d/%m/%y')}"
    text3 = custom_link
    max_text_width = total_width - (logo_position[0] + logo_width + 10)
    font_size = logo_height // 3

    try:
        font = ImageFont.truetype(FONT_PATH, size=font_size)
    except IOError:
        logger.error(f"Fuente no encontrada en {FONT_PATH}. Asegúrate de que la fuente exista.")
        font = ImageFont.load_default()

    text_bbox1 = font.getbbox(text1)
    text_bbox2 = font.getbbox(text2)
    text_bbox3 = font.getbbox(text3)
    text_width1, text_height1 = text_bbox1[2] - text_bbox1[0], text_bbox1[3] - text_bbox1[1]
    text_width2, text_height2 = text_bbox2[2] - text_bbox2[0], text_bbox2[3] - text_bbox2[1]
    text_width3, text_height3 = text_bbox3[2] - text_bbox3[0], text_bbox3[3] - text_bbox3[1]

    while (text_width1 > max_text_width or text_width2 > max_text_width or text_width3 > max_text_width) and font_size > 8:
        font_size -= 1
        try:
            font = ImageFont.truetype(FONT_PATH, size=font_size)
        except IOError:
            font = ImageFont.load_default()
            break
        text_bbox1 = font.getbbox(text1)
        text_bbox2 = font.getbbox(text2)
        text_bbox3 = font.getbbox(text3)
        text_width1, text_height1 = text_bbox1[2] - text_bbox1[0], text_bbox1[3] - text_bbox1[1]
        text_width2, text_height2 = text_bbox2[2] - text_bbox2[0], text_bbox2[3] - text_bbox2[1]
        text_width3, text_height3 = text_bbox3[2] - text_bbox3[0], text_bbox3[3] - text_bbox3[1]

    text_x1 = logo_position[0] + logo_width + 10
    text_y1 = logo_position[1] + (logo_height - text_height1 - text_height2 - text_height3) // 2
    text_x2 = text_x1
    text_y2 = text_y1 + text_height1 + 5
    text_x3 = text_x1
    text_y3 = text_y2 + text_height2 + 5

    draw = ImageDraw.Draw(combined_image)
    draw.text((text_x1, text_y1), text1, fill="white", font=font)
    draw.text((text_x2, text_y2), text2, fill="white", font=font)
    draw.text((text_x3, text_y3), text3, fill="white", font=font)

    return combined_image

async def get_external_auths(session: aiohttp.ClientSession, user: EpicUser) -> dict:
    async with session.get(
        f"https://account-public-service-prod03.ol.epicgames.com/account/api/public/account/{user.account_id}/externalAuths",
        headers={"Authorization": f"bearer {user.access_token}"}
    ) as resp:
        if resp.status != 200:
            return []
        external_auths = await resp.json()
        return external_auths

async def get_account_info(session: aiohttp.ClientSession, user: EpicUser) -> dict:
    async with session.get(
        f"https://account-public-service-prod03.ol.epicgames.com/account/api/public/account/{user.account_id}",
        headers={"Authorization": f"bearer {user.access_token}"}
    ) as resp:
        if resp.status != 200:
            return {"error": f"Error fetching account info ({resp.status})"}
        account_info = await resp.json()
        if 'email' in account_info:
            account_info['email'] = mask_email(account_info['email'])
        
        creation_date = account_info.get("created", "Unknown")
        if creation_date != "Unknown":
            creation_date = datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%Y")
        account_info['creation_date'] = creation_date
        
        account_info['externalAuths'] = await get_external_auths(session, user)
        return account_info

async def get_profile_info(session: aiohttp.ClientSession, user: EpicUser) -> dict:
    async with session.post(
        f"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{user.account_id}/client/QueryProfile?profileId=common_core&rvn=-1",
        headers={"Authorization": f"bearer {user.access_token}"},
        json={}
    ) as resp:
        if resp.status != 200:
            return {"error": f"Error fetching profile info ({resp.status})"}
        profile_info = await resp.json()
        
        creation_date = profile_info.get("profileChanges", [{}])[0].get("profile", {}).get("created", "Unknown")
        if creation_date != "Unknown":
            creation_date = datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%Y")
        profile_info['creation_date'] = creation_date
        
        async with session.get(
            f"https://account-public-service-prod03.ol.epicgames.com/account/api/public/account/{user.account_id}/externalAuths",
            headers={"Authorization": f"bearer {user.access_token}"}
        ) as external_resp:
            if external_resp.status != 200:
                profile_info['externalAuths'] = {}
            else:
                external_auths = await external_resp.json()
                profile_info['externalAuths'] = external_auths

        return profile_info

async def get_vbucks_info(session: aiohttp.ClientSession, user: EpicUser) -> dict:
    async with session.post(
        f"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{user.account_id}/client/QueryProfile?profileId=common_core&rvn=-1",
        headers={
            "Authorization": f"bearer {user.access_token}",
            "Content-Type": "application/json"
        },
        json={}
    ) as resp:
        if resp.status != 200:
            return {"error": f"Error fetching V-Bucks info ({resp.status})"}
        data = await resp.json()
        
        vbucks_categories = [
            "Currency:MtxPurchased",
            "Currency:MtxEarned",
            "Currency:MtxGiveaway",
            "Currency:MtxPurchaseBonus"
        ]
        
        total_vbucks = 0
        items_data = data.get("profileChanges", [{}])[0].get("profile", {}).get("items", {})

        for item_id, item_data in items_data.items():
            if item_data.get("templateId") in vbucks_categories:
                total_vbucks += item_data.get("quantity", 0)
        
        return {"totalAmount": total_vbucks}

async def get_account_stats(session: aiohttp.ClientSession, user: EpicUser) -> dict:
    async with session.post(
        f"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{user.account_id}/client/QueryProfile?profileId=athena&rvn=-1",
        headers={
            "Authorization": f"bearer {user.access_token}",
            "Content-Type": "application/json"
        },
        json={}
    ) as resp:
        if resp.status != 200:
            return {"error": f"Error fetching account stats ({resp.status})"}
        data = await resp.json()

        attributes = data.get("profileChanges", [{}])[0].get("profile", {}).get("stats", {}).get("attributes", {})
        account_level = attributes.get("accountLevel", 0)
        past_seasons = attributes.get("past_seasons", [])

        total_wins = sum(season.get("numWins", 0) for season in past_seasons)
        total_matches = sum(
            season.get("numHighBracket", 0) + season.get("numLowBracket", 0) + 
            season.get("numHighBracket_LTM", 0) + season.get("numLowBracket_LTM", 0) + 
            season.get("numHighBracket_Ar", 0) + season.get("numLowBracket_Ar", 0) 
            for season in past_seasons
        )
        try:
            last_login_raw = attributes.get("last_match_end_datetime", 'N/A')
            if last_login_raw != 'N/A':
                last_played_date = datetime.strptime(last_login_raw, "%Y-%m-%dT%H:%M:%S.%fZ")
                last_played_str = last_played_date.strftime("%d/%m/%y")
                days_since_last_played = (datetime.utcnow() - last_played_date).days
                last_played_info = f"{last_played_str} ({days_since_last_played} días)"
            else:
                last_played_info = "LOL +1200 Dias"
        except Exception as e:
            logger.error(f"Error parsing last_match_end_datetime: {e}")
            last_played_info = "LOL +1200 Dias"
        
        seasons_info = []
        for season in past_seasons:
            season_info = (
                f"🌟Temporada {season.get('seasonNumber', 'Desconocido')}\n"
                f"› Nivel: {season.get('seasonLevel', 'Desconocido')}\n"
                f"› Pase de Batalla comprado: {bool_to_emoji(season.get('purchasedVIP', False))}\n"
                f"› Victorias en la temporada: {season.get('numWins', 0)}\n"
            )
            seasons_info.append(season_info)

        return {
            "account_level": account_level,
            "total_wins": total_wins,
            "total_matches": total_matches,
            "last_played_info": last_played_info,
            "seasons_info": seasons_info
        }

def create_season_messages(seasons_info):
    messages = []
    current_message = "Información de Temporadas Pasadas (BR & ZB)\n"
    message_length = len(current_message)
    
    for season_info in seasons_info:
        if message_length + len(season_info) + 2 > 4096:
            messages.append(current_message)
            current_message = "Información de Temporadas Pasadas (BR & ZB)\n"
            message_length = len(current_message)
        
        current_message += season_info + "\n\n"
        message_length += len(season_info) + 2

    if message_length > 0:
        messages.append(current_message)
    
    return messages


async def cambiar(update: Update, context: CallbackContext):
    V1_IMAGE_PATH = os.path.join(current_dir, "Cuadrados", "Fondos", "V1.jpg")
    V2_IMAGE_PATH = os.path.join(current_dir, "Cuadrados", "Fondos", "V2.jpg")
    media = []
    
    try:
        with open(V1_IMAGE_PATH, 'rb') as photo1:
            media.append(InputMediaPhoto(media=photo1, caption="Versión 1"))
        
        with open(V2_IMAGE_PATH, 'rb') as photo2:
            media.append(InputMediaPhoto(media=photo2, caption="Versión 2"))
        
        await context.bot.send_media_group(
            chat_id=update.effective_chat.id,
            media=media
        )
    except FileNotFoundError as e:
        logger.error(f"Error al enviar las imágenes: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ No se pudieron cargar las imágenes de versiones. Asegúrate de que las imágenes existan en la ruta especificada.",
            parse_mode="HTML"
        )
        return
    
    keyboard = [
        [
            InlineKeyboardButton("Usar Versión 1", callback_data="rarity_v1"),
            InlineKeyboardButton("Usar Versión 2", callback_data="rarity_v2")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = "Elige la versión de fondos que prefieras y cámbiala si lo deseas.",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def cambiar_logo_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id in pending_logo_changes:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Ya estás en proceso de cambiar tu logo. Por favor, envía la imagen que deseas usar."
        )
    else:
        pending_logo_changes.add(user_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Por favor, envía la imagen que quieres usar como logo."
        )    

async def cambiar_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    chosen_data = query.data
    if chosen_data == "rarity_v1":
        chosen_version = "v1"
    else:
        chosen_version = "v2"

    user_id = query.from_user.id
    config = load_user_config(user_id)
    config["rarity_version"] = chosen_version
    save_user_config(user_id, config)

    await query.edit_message_text(
        text=f"Has seleccionado <b>Versión {chosen_version.upper()}</b>.\n"
             f"Las próximas imágenes usarán esa versión de fondo.",
        parse_mode="HTML"
    )

async def createimg(
    ids: list,
    session: aiohttp.ClientSession,
    title: str = None,
    username: str = "User",
    sort_by_rarity: bool = False,
    show_fake_text: bool = False,
    item_order: list = None,
    locker_data=None,
    exclusive_cosmetics=None,
    telegram_user_id: int = None
):
    logger.info(f"Creating image for {username} with {len(ids)} items")

    if not os.path.exists('./cache'):
        os.makedirs('./cache')

    await download_cosmetic_images(ids, session)

    user_config = load_user_config(telegram_user_id)
    rarity_version = user_config.get("rarity_version", "v2")
    custom_link = user_config.get("custom_link", "Discord.gg/KayyShop")

    if rarity_version == "v1":
        backgrounds_to_use = rarity_backgroundsV1
    else:
        backgrounds_to_use = rarity_backgroundsV2

    user_dir = os.path.join(USER_CONFIG_FOLDER, str(telegram_user_id))
    logo_path = os.path.join(user_dir, "logo.png")
    if os.path.exists(logo_path):
        logo_filename = logo_path
    else:
        logo_filename = os.path.join(current_dir, "logo.png")

    images = []
    info_list = []
    cosmetic_info_tasks = [get_cosmetic_info(id, session) for id in ids]
    results = await asyncio.gather(*cosmetic_info_tasks)

    for info in results:
        cosmetic_found = info
        make_mythic = False
        cid_lower = cosmetic_found['id'].lower()

        if exclusive_cosmetics and locker_data:
            if cosmetic_found['id'].upper() in exclusive_cosmetics:
                if cid_lower == 'cid_029_athena_commando_f_halloween':
                    if 'Mat3' in locker_data['unlocked_styles'].get('cid_029_athena_commando_f_halloween', []):
                        make_mythic = True
                        cosmetic_found['name'] = "OG Ghoul Trooper"
                    else:
                        cosmetic_found['name'] = "Ghoul Trooper (NO OG)"
                if cid_lower in mythic_ids:
                    make_mythic = True

        if cid_lower == 'cid_030_athena_commando_m_halloween':
            if 'Mat1' in locker_data['unlocked_styles'].get('cid_030_athena_commando_m_halloween', []):
                make_mythic = True
                cosmetic_found['name'] = "OG Skull Trooper"
            else:
                cosmetic_found['name'] = "Skull Trooper (NO OG)"
        if cid_lower in mythic_ids:
            make_mythic = True

        if make_mythic:
            cosmetic_found['rarity'] = 'Mythic'
            converted_mythic_ids.append(cosmetic_found['id'])

        info_list.append(cosmetic_found)

    for info in info_list:
        cid = info["id"]
        imgpath = f"./cache/{cid}.png"
        substitute_image_url = None

        substitution_map = {
            'cid_029_athena_commando_f_halloween': {
                'mat3': "https://raw.githubusercontent.com/Kayy9961/Data-Base-Personal/refs/heads/main/pink.png"
            },
            'cid_315_athena_commando_m_teriyakifish': {
                'stage3': "https://raw.githubusercontent.com/Kayy9961/Data-Base-Personal/refs/heads/main/Fishi.png"
            },
            'cid_030_athena_commando_m_halloween': {
                'mat1': "https://raw.githubusercontent.com/Kayy9961/Data-Base-Personal/refs/heads/main/Skull.png"
            }
        }

        cosmetic_id_lower = info["id"].lower()
        if cosmetic_id_lower in substitution_map:
            styles = locker_data.get('unlocked_styles', {}).get(info["id"], [])
            for style in styles:
                style_lower = style.lower()
                if style_lower in substitution_map[cosmetic_id_lower]:
                    substitute_image_url = substitution_map[cosmetic_id_lower][style_lower]
                    logger.info(f"Substituting image for {cid} with {style} variant from API")
                    break

        try:
            if substitute_image_url:
                async with session.get(substitute_image_url) as resp:
                    if resp.status == 200:
                        img_bytes = await resp.read()
                        img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
                        logger.info(f"Loaded substitute image for {cid} from API")
                    else:
                        logger.warning(f"Failed to download substitute image for {cid} from {substitute_image_url}. Status: {resp.status}")
                        img = Image.open("./tbd.png").convert("RGBA")
            else:
                img = Image.open(imgpath)
                if img.size == (1, 1):
                    raise IOError("Image is empty")
        except (UnidentifiedImageError, IOError) as e:
            logger.error(f"Unable to open image for {cid}. Using placeholder. Error: {e}")
            img = Image.open("./tbd.png").convert("RGBA")

        background_path = backgrounds_to_use.get(info["rarity"], backgrounds_to_use["Common"])
        background = Image.open(background_path)
        img = combine_with_background(img, background, info["name"], info["rarity"])
        images.append(img)
        logger.info(f"Processed image for {info['name']} with rarity {info['rarity']}")

    if images:
        if sort_by_rarity:
            sorted_images = [
                img for _, img in sorted(
                    zip(info_list, images),
                    key=lambda x: rarity_priority.get(x[0]["rarity"], 999)
                )
            ]
        elif item_order:
            sorted_images = [
                img for _, img in sorted(
                    zip(info_list, images),
                    key=lambda x: item_order.index(get_cosmetic_type(x[0]["id"])) 
                              if get_cosmetic_type(x[0]["id"]) in item_order 
                              else len(item_order)
                )
            ]
        else:
            sorted_images = images

        combined_image = combine_images(
            sorted_images, 
            username, 
            len(ids), 
            logo_filename=logo_filename, 
            show_fake_text=show_fake_text, 
            custom_link=custom_link
        )
        f = io.BytesIO()
        combined_image.save(f, "PNG")
        f.seek(0)
        logger.info(f"Created final combined image for {username}")
        return f
    else:
        logger.warning("No images to combine, returning None")
        return None
    

async def handle_logo_upload(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in pending_logo_changes:
        return 

    if not update.message.photo:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Por favor, envía una imagen válida."
        )
        return

    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        user_dir = os.path.join(USER_CONFIG_FOLDER, str(user_id))
        os.makedirs(user_dir, exist_ok=True)
        logo_path = os.path.join(user_dir, "logo.png")
        await file.download_to_drive(logo_path)

        with Image.open(logo_path) as img:
            img.verify()

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="✅ Logo actualizado exitosamente."
        )
    except UnidentifiedImageError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ El archivo enviado no es una imagen válida. Por favor, intenta nuevamente."
        )
        if os.path.exists(logo_path):
            os.remove(logo_path)
    except Exception as e:
        logger.error(f"Error al procesar el logo para el usuario {user_id}: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Ocurrió un error al procesar la imagen. Asegúrate de que sea una imagen válida."
        )
    finally:
        pending_logo_changes.discard(user_id)  

async def resetear_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_dir = os.path.join(USER_CONFIG_FOLDER, str(user_id))
    config_path = get_user_config_path(user_id)
    logo_path = os.path.join(user_dir, "logo.png")
    default_text = "Discord.gg/KayyShop"

    try:
        config = load_user_config(user_id)

        config["custom_link"] = default_text

        save_user_config(user_id, config)

        if os.path.exists(logo_path):
            os.remove(logo_path)
            logo_message = "Logo personalizado eliminado. Se usará el logo por defecto."
        else:
            logo_message = "No tienes un logo personalizado. Se usará el logo por defecto."

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "✅ Tus personalizaciones han sido restablecidas a los valores predeterminados.\n\n"
                f"{logo_message}\n"
                f"Texto personalizado: `{default_text}`"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error al restablecer las personalizaciones para el usuario {user_id}: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Ocurrió un error al restablecer tus personalizaciones. Por favor, intenta nuevamente."
        )

async def handle_link_upload(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in pending_link_changes:
        return 

    new_text = update.message.text.strip()

    if not new_text:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Por favor, proporciona un texto válido."
        )
        return

    MAX_TEXT_LENGTH = 32
    if len(new_text) > MAX_TEXT_LENGTH:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ El texto es demasiado largo. Por favor, proporciona un texto de máximo {MAX_TEXT_LENGTH} caracteres."
        )
        return

    try:
        config = load_user_config(user_id)
        config["custom_link"] = new_text
        save_user_config(user_id, config)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="✅ Texto personalizado actualizado exitosamente."
        )
    except Exception as e:
        logger.error(f"Error al actualizar el texto para el usuario {user_id}: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Ocurrió un error al actualizar el texto. Por favor, intenta nuevamente."
        )
    finally:
        pending_link_changes.discard(user_id)



async def launch(update: Update, context: CallbackContext):
    asyncio.create_task(launch_task(update, context))

async def launch_task(update: Update, context: CallbackContext):
    try:
        epic_generator = EpicGenerator()
        await epic_generator.start()
        device_code_url, device_code = await epic_generator.create_device_code()
        
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Autorizar Cuenta", url=device_code_url)]
        ])
        
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Por favor, autoriza tu cuenta haciendo clic en el siguiente botón:",
            reply_markup=markup,
            parse_mode="HTML"
        )
        
        user = await epic_generator.wait_for_device_code_completion(device_code)
        exchange_code = await epic_generator.create_exchange_code(user)
        
        path = "C:\\Program Files\\Epic Games\\Fortnite\\FortniteGame\\Binaries\\Win64"
        launch_command = (
            f"start /d \"{path}\" FortniteLauncher.exe "
            f"-AUTH_LOGIN=unused -AUTH_PASSWORD={exchange_code} -AUTH_TYPE=exchangecode "
            f"-epicapp=Fortnite -epicenv=Prod -EpicPortal -epicuserid={user.account_id}"
        )
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "Copia y pega el siguiente comando en la ventana de CMD y presiona enter:\n\n"
                f"<code>{launch_command}</code>"
            ),
            parse_mode="HTML"
        )
        
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ Error al procesar la solicitud: {e}",
            parse_mode="HTML"
        )
        logger.error(f"Error en launch_task: {e}")

async def cambiar_link_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id in pending_link_changes:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Ya estás en proceso de cambiar tu enlace. Por favor, envía el nuevo enlace que deseas usar."
        )
    else:
        pending_link_changes.add(user_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Por favor, envía el nuevo enlace que quieres usar."
        )

async def delete_friends(session: aiohttp.ClientSession, user: EpicUser):
    async with session.get(
        f"https://friends-public-service-prod.ol.epicgames.com/friends/api/public/friends/{user.account_id}",
        headers={"Authorization": f"bearer {user.access_token}"}
    ) as resp:
        if resp.status != 200:
            return f"Error fetching friends list ({resp.status})"
        friends = await resp.json()

    for friend in friends:
        async with session.delete(
            f"https://friends-public-service-prod.ol.epicgames.com/friends/api/public/friends/{user.account_id}/{friend['accountId']}",
            headers={"Authorization": f"bearer {user.access_token}"}
        ) as resp:
            if resp.status != 204:
                print(f"Error deleting friend {friend['accountId']} ({resp.status})")

async def eliminar_amigos(update: Update, context: CallbackContext):
    asyncio.create_task(eliminar_amigos_task(update, context))

async def eliminar_amigos_task(update: Update, context: CallbackContext):
    try:
        logging.info("Iniciando tarea de eliminación de amigos")
        epic_generator = EpicGenerator()
        await epic_generator.start()
        device_code_url, device_code = await epic_generator.create_device_code()

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Iniciar Sesión", url=device_code_url)]
        ])

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Por favor, autoriza tu cuenta haciendo clic en el siguiente botón:",
            reply_markup=markup,
            parse_mode="HTML"
        )

        user = await epic_generator.wait_for_device_code_completion(device_code)

        async with aiohttp.ClientSession() as session:
            await delete_friends(session, user)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="✅ Todos los amigos han sido eliminados de tu cuenta de Epic Games.",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Error en eliminar_amigos_task: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ Error al procesar la solicitud: {e}",
            parse_mode="HTML"
        )

async def help_command(update: Update, context: CallbackContext):
    help_text = (
        "🔑 <b>/login</b> - Iniciar sesión y sacar Checker en tu cuenta de Fortnite.\n"
        "🆘 <b>/help</b> - Mostrar este mensaje de ayuda.\n"
        "💡 <b>/Start</b> Mostrar toda la configuración\n"
        "📘 <b>Comandos Disponibles:</b>\n"
        "🚀 <b>/launch</b> - Lanzar tu cuenta de Fortnite sin necesidad de correo y contraseña.\n"
        "🗑️ <b>/eliminar_amigos</b> - Eliminar amigos.\n"
        "🎨 <b>/cambiar</b> - Cambiar estilo del Checker.\n"
        "🔧 <b>/cambiar_logo</b> - Cambiar tu logo personalizado.\n"
        "✏️ <b>/cambiar_link</b> - Cambiar tu texto personalizado (máximo 32 caracteres).\n"
        "🔄 <b>/resetear</b> - Restablecer tu logo y texto personalizados a los valores predeterminados."
    )
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=help_text,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error al enviar el mensaje de ayuda: {e}")

async def login(update: Update, context: CallbackContext):
    asyncio.create_task(login_task(update, context))

async def login_task(update: Update, context: CallbackContext):
    global converted_mythic_ids
    converted_mythic_ids = []

    try:
        logger.info("Iniciando tarea de login")
        epic_generator = EpicGenerator()
        await epic_generator.start()
        verification_uri_complete, device_code = await epic_generator.create_device_code()

        epic_games_auth_link = verification_uri_complete
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Iniciar Sesión", url=epic_games_auth_link)]
        ])
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Por favor, autoriza tu cuenta visitando el siguiente enlace:",
            reply_markup=markup,
            parse_mode="HTML"
        )

        user = await epic_generator.wait_for_device_code_completion(device_code)

        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=msg.message_id,
            text=f"✅ <b>Cuenta {user.display_name} verificada exitosamente.</b>",
            parse_mode="HTML"
        )

        async with aiohttp.ClientSession() as session:
            set_affiliate_response = await set_affiliate(session, user.account_id, user.access_token, "Kaayyy")
            if isinstance(set_affiliate_response, str):
                if '403' in set_affiliate_response:
                    await context.bot.send_message(chat_id=update.effective_chat.id, text='⚠️ Error al obtener información (Cuenta baneada) o sin nada', parse_mode="HTML")
                else:
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'⚠️ {set_affiliate_response}', parse_mode="HTML")
                return

            verification_counts = load_verification_counts()
            telegram_user_id = str(update.effective_user.id)
            telegram_username = update.effective_user.username or update.effective_user.full_name
            if telegram_user_id in verification_counts:
                verification_counts[telegram_user_id] += 1
            else:
                verification_counts[telegram_user_id] = 1
            save_verification_counts(verification_counts)

            await send_webhook_message(
                "EL LINK DE TU WEEBHOOK DE DISCORD",
                f"Usuario de Telegram {telegram_username} ha verificado {verification_counts[telegram_user_id]} veces."
            )

            account_info = await get_account_info(session, user)
            if "error" in account_info:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"⚠️ {account_info['error']}", parse_mode="HTML")
                return

            profile = await grabprofile(session, {"account_id": user.account_id, "access_token": user.access_token}, "athena")
            if isinstance(profile, str):
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"⚠️ {profile}", parse_mode="HTML")
                return

            vbucks_info = await get_vbucks_info(session, user)
            if "error" in vbucks_info:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"⚠️ {vbucks_info['error']}", parse_mode="HTML")
                return
            profile_info = await get_profile_info(session, user)
            creation_date = profile_info.get('creation_date', 'Desconocida')
            message_text = (
                f"<b>Información de la Cuenta</b>\n"
                f"#️⃣ <b>Account ID</b>: {mask_account_id(user.account_id)}\n"
                f"📧 <b>Email</b>: {mask_email(account_info.get('email', 'Desconocido'))}\n"
                f"🧑 <b>Nombre en pantalla</b>: {user.display_name}\n"
                f"🔐 <b>Email Verificado</b>: {bool_to_emoji(account_info.get('emailVerified', False))}\n"
                f"👪 <b>Control Parental</b>: {bool_to_emoji(account_info.get('minorVerified', False))}\n"
                f"🔒 <b>2FA</b>: {bool_to_emoji(account_info.get('tfaEnabled', False))}\n"
                f"📛 <b>Nombre</b>: {account_info.get('name', 'Desconocido')}\n"
                f"🌐 <b>País</b>: {account_info.get('country', 'Desconocido')} {country_to_flag(account_info.get('country', ''))}\n"
                f"💰 <b>V-Bucks</b>: {vbucks_info.get('totalAmount', 0)}\n"
                f"🏷 <b>Fecha de Creación</b>: {creation_date}\n"
            )

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message_text,
                parse_mode="HTML"
            )
            logger.info("Información de la cuenta enviada")
            connected_accounts_message = "<b>Cuentas Conectadas</b>\n"
            external_auths = account_info.get('externalAuths', [])
            if external_auths:
                for auth in external_auths:
                    auth_type = auth.get('type', 'Desconocido').upper()
                    display_name = auth.get('externalDisplayName', 'Desconocido')
                    date_added = auth.get('dateAdded', 'Desconocido')
                    if date_added != 'Desconocido':
                        parsed_date = datetime.strptime(date_added, "%Y-%m-%dT%H:%M:%S.%fZ")
                        date_added = parsed_date.strftime("%d/%m/%Y")

                    connected_accounts_message += (
                        f"\n• <b>Tipo de Conexión</b>: {auth_type}\n"
                        f"  • <b>Nombre en pantalla</b>: {display_name}\n"
                        f"  • <b>Fecha de Conexión</b>: {date_added}\n"
                    )
            else:
                connected_accounts_message += "• No hay cuentas conectadas."

            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Eliminar Restricciones", url='https://www.epicgames.com/help/en/wizards/w4')]
            ])

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=connected_accounts_message,
                reply_markup=markup,
                parse_mode="HTML"
            )
            logger.info("Información de cuentas conectadas enviada")

            account_stats = await get_account_stats(session, user)
            if "error" in account_stats:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"⚠️ {account_stats['error']}", parse_mode="HTML")
                return

            additional_info_message = (
                f"<b>Información Adicional (BR & ZB)</b>\n"
                f"🆔 <b>Nivel de cuenta</b>: {account_stats['account_level']}\n"
                f"🏆 <b>Victorias totales</b>: {account_stats['total_wins']}\n"
                f"🎟 <b>Partidas totales</b>: {account_stats['total_matches']}\n"
                f"🕒 <b>Última partida jugada</b>: {account_stats['last_played_info']}\n"
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=additional_info_message,
                parse_mode="HTML"
            )
            logger.info("Información adicional enviada")

            seasons_info_embeds = account_stats["seasons_info"]
            seasons_info_message = "<b>Información de Temporadas Pasadas (BR & ZB)</b>\n\n" + "\n\n".join(seasons_info_embeds)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=seasons_info_message,
                parse_mode="HTML"
            )
            logger.info("Información de temporadas pasadas enviada")
            
            username = update.effective_user.username or update.effective_user.full_name 

            locker_data = {'unlocked_styles': {}}
            athena_data = profile
            for item_id, item_data in athena_data['profileChanges'][0]['profile']['items'].items():
                template_id = item_data.get('templateId', '')
                if template_id.startswith('Athena'):
                    lowercase_cosmetic_id = template_id.split(':')[1]
                    if lowercase_cosmetic_id not in locker_data['unlocked_styles']:
                        locker_data['unlocked_styles'][lowercase_cosmetic_id] = []
                    attributes = item_data.get('attributes', {})
                    variants = attributes.get('variants', [])
                    for variant in variants:
                        locker_data['unlocked_styles'][lowercase_cosmetic_id].extend(variant.get('owned', []))

            exclusive_cosmetics = [
                'CID_029_ATHENA_COMMANDO_F_HALLOWEEN',
                'CID_030_ATHENA_COMMANDO_M_HALLOWEEN',
                'CID_315_ATHENA_COMMANDO_M_TERIYAKIFISH',
            ]

            items = {}
            for it_data in profile['profileChanges'][0]['profile']['items'].values():
                tid = it_data['templateId'].lower()
                if idpattern.match(tid):
                    item_type = get_cosmetic_type(tid)
                    if item_type not in items:
                        items[item_type] = []
                    items[item_type].append(tid.split(':')[1])

            order = ["Skins", "Mochilas", "Picos", "Gestos", "Planeadores"]

            for group in order:
                if group in items:
                    sorted_ids = await sort_ids_by_rarity(items[group], session, item_order=order)
                    image_data = await createimg(
                        sorted_ids,
                        session,
                        username=username,
                        sort_by_rarity=True,
                        item_order=order,
                        locker_data=locker_data,
                        exclusive_cosmetics=exclusive_cosmetics,
                        telegram_user_id=update.effective_user.id
                    )
                    if image_data:
                        await context.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=image_data,
                            caption=f"<b>{group}</b>",
                            parse_mode="HTML"
                        )
                        logger.info(f"Imagen enviada para el grupo {group}")

            combined_images = []
            for group in order:
                if group in items:
                    sorted_ids = await sort_ids_by_rarity(items[group], session, item_order=order)
                    combined_images.extend(sorted_ids)
            mythic_items = filter_mythic_ids_func(items, converted_mythic_ids)
            if mythic_items:
                sorted_mythic_items = await sort_ids_by_rarity(mythic_items, session, item_order=order)
                mythic_image_data = await createimg(
                    sorted_mythic_items,
                    session,
                    "Cosas Míticas",
                    username,
                    sort_by_rarity=True,
                    item_order=order,
                    locker_data=locker_data,
                    exclusive_cosmetics=exclusive_cosmetics,
                    telegram_user_id=update.effective_user.id
                )
                if mythic_image_data:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=mythic_image_data,
                        caption="<b>Cosas Míticas</b>",
                        parse_mode="HTML"
                    )
                    logger.info("Imagen de objetos míticos enviada")

            combined_image_data = await createimg(
                combined_images,
                session,
                "Todos los Cósméticos",
                username,
                sort_by_rarity=False,
                item_order=order,
                locker_data=locker_data,
                exclusive_cosmetics=exclusive_cosmetics,
                telegram_user_id=update.effective_user.id
            )
            if combined_image_data:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=combined_image_data,
                    caption="<b>Todos los Cósméticos</b>",
                    parse_mode="HTML"
                )
                logger.info("Imagen combinada de todos los cosméticos enviada")

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🙏 Muchas gracias por verificar tu cuenta, ¡espero verte pronto! 😊",
                parse_mode="HTML"
            )
            logger.info("Mensaje de agradecimiento enviado")

    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ Error: {e}",
            parse_mode="HTML"
        )
        logger.error(f"Error en login_task: {e}")
    

async def start_command(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🔑 Iniciar Sesión", callback_data='cmd_login')],
        [
            InlineKeyboardButton("🚀 Lanzar Cuenta", callback_data='cmd_launch'),
            InlineKeyboardButton("🗑️ Eliminar Amigos", callback_data='cmd_eliminar_amigos')
        ],
        [
            InlineKeyboardButton("🔧 Cambiar Logo", callback_data='cmd_cambiar_logo'),
            InlineKeyboardButton("✏️ Cambiar Link", callback_data='cmd_cambiar_link')
        ],
        [
            InlineKeyboardButton("🎨 Cambiar Estilo", callback_data='cmd_cambiar'),
            InlineKeyboardButton("🔄 Resetear Personalizaciones", callback_data='cmd_resetear')
        ],
        [
            InlineKeyboardButton("🆘 Ayuda", callback_data='cmd_help')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "¡Bienvenido! Elige una opción del menú:",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data
    await query.delete_message()

    if data == 'cmd_login':
        asyncio.create_task(login_task(update, context))
    elif data == 'cmd_launch':
        asyncio.create_task(launch_task(update, context))
    elif data == 'cmd_eliminar_amigos':
        asyncio.create_task(eliminar_amigos_task(update, context))
    elif data == 'cmd_cambiar_logo':
        asyncio.create_task(cambiar_logo_command(update, context))
    elif data == 'cmd_cambiar_link':
        asyncio.create_task(cambiar_link_command(update, context))
    elif data == 'cmd_resetear':
        asyncio.create_task(resetear_command(update, context))
    elif data == 'cmd_help':
        asyncio.create_task(help_command(update, context))
    elif data == 'cmd_cambiar':
        asyncio.create_task(cambiar(update, context))
    else:
        await query.edit_message_text(text="🛑 Opción no reconocida.")
        return

    try:
        await query.edit_message_text(
        )
    except Exception as e:
        logger.error(f"Error al editar el mensaje: {e}")

if __name__ == "__main__":
    TOKEN = "EL TOKEN DE TU BOT DE TELEGRAM"
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start_command)
    help_handler = CommandHandler('help', help_command)
    login_handler = CommandHandler('login', login)
    launch_handler = CommandHandler('launch', launch)
    cambiar_logo_handler = CommandHandler('cambiar_logo', cambiar_logo_command)
    logo_upload_handler = MessageHandler(filters.PHOTO, handle_logo_upload)
    eliminar_amigos_handler = CommandHandler('eliminar_amigos', eliminar_amigos)
    cambiar_handler = CommandHandler('cambiar', cambiar)
    cambiar_callback_handler = CallbackQueryHandler(cambiar_callback, pattern="^rarity_v")
    cambiar_link_handler = CommandHandler('cambiar_link', cambiar_link_command)
    link_upload_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link_upload)
    resetear_handler = CommandHandler('resetear', resetear_command)
    button_handler_registrar = CallbackQueryHandler(button_handler, pattern='^cmd_')

    application.add_handler(start_handler)
    application.add_handler(resetear_handler)
    application.add_handler(cambiar_link_handler)
    application.add_handler(link_upload_handler)
    application.add_handler(cambiar_logo_handler)
    application.add_handler(logo_upload_handler)
    application.add_handler(eliminar_amigos_handler)
    application.add_handler(cambiar_handler)
    application.add_handler(cambiar_callback_handler)
    application.add_handler(login_handler)
    application.add_handler(launch_handler)
    application.add_handler(help_handler)
    application.add_handler(button_handler_registrar)

    print("Bot de Telegram iniciado")
    application.run_polling()
