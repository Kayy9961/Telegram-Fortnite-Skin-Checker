import logging
import os
import re
import io
import math
import json
import platform
import asyncio
import multiprocessing
import concurrent.futures
from datetime import datetime

import aiohttp
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError

from telegram import (
    Update,
    BotCommand,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    filters,
    CallbackQueryHandler
)
    
def calculate_font_size(name: str, base_size: int = 40, special: bool = False) -> int:
    if special:
        length = len(name)
        if length <= 1:
            return int(base_size * 0.4)
        elif length <= 2:
            return int(base_size * 0.5)
        elif length <= 3:
            return int(base_size * 0.6)
        elif length <= 4:
            return int(base_size * 0.7)
        elif length <= 5:
            return int(base_size * 0.8)
        elif length <= 6:
            return int(base_size * 0.9)
        elif length <= 7:
            return int(base_size * 1.0)
        elif length <= 8:
            return int(base_size * 1.1)
        elif length <= 9:
            return int(base_size * 1.2)
        elif length <= 10:
            return int(base_size * 1.3)
        elif length <= 11:
            return int(base_size * 1.4)
        elif length <= 12:
            return int(base_size * 1.5)
        elif length <= 13:
            return int(base_size * 1.6)
        elif length <= 14:
            return int(base_size * 1.7)
        elif length <= 15:
            return int(base_size * 1.8)
        else:
            return int(base_size * 2.0)
    else:
        return base_size    

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

os.system("title Code Created By Kayy / discord.gg/KayyShop")

webhook_url = None

pending_link_changes = set()
pending_logo_changes = set()

VERIFICATION_COUNT_FILE = "verification_countstele.json"
USER_CONFIG_FOLDER = "user_config"

Image.MAX_IMAGE_PIXELS = None

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
        return {"rarity_version": "v1", "custom_link": "Discord.gg/KayyShop"}

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

async def send_webhook_message(message: str):
    global webhook_url
    if webhook_url:
        async with aiohttp.ClientSession() as session:
            webhook_data = {"content": message}
            async with session.post(webhook_url, json=webhook_data) as resp:
                if resp.status != 204:
                    logger.error(f"Error enviando mensaje al webhook: {resp.status}")
                else:
                    logger.info("Mensaje enviado exitosamente al webhook.")
    else:
        logger.info("Webhook no está configurado. Se omite el envío del mensaje.")

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

rarity_backgroundsV3 = {
    "Common": os.path.join(current_dir, "Cuadrados", "CuadradosV3", "commun.png"),
    "Uncommon": os.path.join(current_dir, "Cuadrados", "CuadradosV3", "uncommun.png"),
    "Rare": os.path.join(current_dir, "Cuadrados", "CuadradosV3", "rare.png"),
    "Epic": os.path.join(current_dir, "Cuadrados", "CuadradosV3", "epico.png"),
    "Legendary": os.path.join(current_dir, "Cuadrados", "CuadradosV3", "legendary.png"),
    "Mythic": os.path.join(current_dir, "Cuadrados", "CuadradosV3", "mitico.png"),
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

rarity_backgroundsV4 = {
    "Common": os.path.join(current_dir, "Cuadrados", "CuadradosV4", "commun.png"),
    "Uncommon": os.path.join(current_dir, "Cuadrados", "CuadradosV4", "uncommun.png"),
    "Rare": os.path.join(current_dir, "Cuadrados", "CuadradosV4", "rare.png"),
    "Epic": os.path.join(current_dir, "Cuadrados", "CuadradosV4", "epico.png"),
    "Legendary": os.path.join(current_dir, "Cuadrados", "CuadradosV4", "legendary.png"),
    "Mythic": os.path.join(current_dir, "Cuadrados", "CuadradosV4", "mitico.png"),
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

rarity_backgroundsV5 = {
    "Common": os.path.join(current_dir, "Cuadrados", "CuadradosV5", "commun.png"),
    "Uncommon": os.path.join(current_dir, "Cuadrados", "CuadradosV5", "uncommun.png"),
    "Rare": os.path.join(current_dir, "Cuadrados", "CuadradosV5", "rare.png"),
    "Epic": os.path.join(current_dir, "Cuadrados", "CuadradosV5", "epico.png"),
    "Legendary": os.path.join(current_dir, "Cuadrados", "CuadradosV5", "legendary.png"),
    "Mythic": os.path.join(current_dir, "Cuadrados", "CuadradosV5", "mitico.png"),
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

rarity_backgroundsV6 = {
    "Common": os.path.join(current_dir, "Cuadrados", "CuadradosV6", "commun.png"),
    "Uncommon": os.path.join(current_dir, "Cuadrados", "CuadradosV6", "uncommun.png"),
    "Rare": os.path.join(current_dir, "Cuadrados", "CuadradosV6", "rare.png"),
    "Epic": os.path.join(current_dir, "Cuadrados", "CuadradosV6", "epico.png"),
    "Legendary": os.path.join(current_dir, "Cuadrados", "CuadradosV6", "legendary.png"),
    "Mythic": os.path.join(current_dir, "Cuadrados", "CuadradosV6", "mitico.png"),
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

rarity_backgroundsV7 = {
    "Common": os.path.join(current_dir, "Cuadrados", "CuadradosV7", "commun.png"),
    "Uncommon": os.path.join(current_dir, "Cuadrados", "CuadradosV7", "uncommun.png"),
    "Rare": os.path.join(current_dir, "Cuadrados", "CuadradosV7", "rare.png"),
    "Epic": os.path.join(current_dir, "Cuadrados", "CuadradosV7", "epico.png"),
    "Legendary": os.path.join(current_dir, "Cuadrados", "CuadradosV7", "legendary.png"),
    "Mythic": os.path.join(current_dir, "Cuadrados", "CuadradosV7", "mitico.png"),
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
    "cid_313_athena_commando_m_kpopfashion": 6,
    "cid_757_athena_commando_f_wildcat": 7,
    "cid_039_athena_commando_f_disco": 8,
    "cid_033_athena_commando_f_medieval": 9,
    "cid_032_athena_commando_m_medieval": 10,
    "cid_084_athena_commando_m_assassin": 11,
    "cid_095_athena_commando_m_founder": 12,
    "cid_096_athena_commando_f_founder": 13,
    "cid_113_athena_commando_m_blueace": 14,
    "cid_116_athena_commando_m_carbideblack": 15,
    "cid_175_athena_commando_m_celestial": 16,
    "cid_183_athena_commando_m_modernmilitaryred": 17,
    "cid_342_athena_commando_m_streetracermetallic": 18,
    "cid_371_athena_commando_m_speedymidnight": 19,
    "cid_434_athena_commando_f_stealthhonor": 20,
    "cid_441_athena_commando_f_cyberscavengerblue": 21,
    "cid_479_athena_commando_f_davinci": 22,
    "cid_515_athena_commando_m_barbequelarry": 23,
    "cid_516_athena_commando_m_blackwidowrogue": 24,
    "cid_703_athena_commando_m_cyclone": 25,
    "cid_npc_athena_commando_m_masterkey": 26
}

mythic_ids = [
    "cid_017_athena_commando_m", "cid_028_athena_commando_f", "eid_tidy", "banner_influencerbanner21", "banner_brseason01", "banner_ot1banner", "banner_ot2banner", "banner_ot3banner", "banner_ot4banner", "banner_ot5banner",
    "banner_influencerbanner54", "banner_influencerbanner38", "banner_ot6banner", "banner_ot7banner", "banner_ot8banner", "banner_ot9banner", "banner_ot10banner", "banner_ot11banner",
    "cid_032_athena_commando_m_medieval", "cid_033_athena_commando_f_medieval", "cid_035_athena_commando_m_medieval",
    "eid_uproar_496sc", "eid_textile_3o8qg", "eid_sunrise_rpz6m", "eid_sleek_s20cu", "eid_sandwichbop", "eid_sahara", "eid_rigormortis", "eid_richfam", "eid_provisitorprotest", "eid_playereleven", "eid_lasagnadance", "eid_jingle", "eid_hoppin", "eid_hnygoodriddance", "eid_hawtchamp", "eid_gleam", "eid_galileo3_t4dko", "eid_eerie_8wgyk", "eid_dumbbell_lift", "eid_downward_8gzua", "eid_cyclone", "eid_cycloneheadbang", "eid_astray", "eid_antivisitorprotest", 
    "pickaxe_spookyneonred", "pickaxe_id_tbd_crystalshard", "pickaxe_id_461_skullbritecube", "pickaxe_id_398_wildcatfemale", "pickaxe_id_338_bandageninjablue1h", "pickaxe_id_178_speedymidnight", "pickaxe_id_099_modernmilitaryred", "pickaxe_id_077_carbidewhite", "pickaxe_id_044_tacticalurbanhammer", "pickaxe_id_039_tacticalblack", "pickaxe_accumulateretro", 
    "character_vampirehunter_galaxy", "character_sahara", "character_reconexpert_fncs", "character_masterkeyorder", 
    "cid_a_329_athena_commando_f_uproar_i5n5z", "cid_a_271_athena_commando_m_fncs_purple", "cid_a_269_athena_commando_f_hastestreet_b563i", "cid_a_256_athena_commando_f_uproarbraids_8iozw", "cid_a_215_athena_commando_f_sunrisecastle_48tiz", "cid_a_216_athena_commando_m_sunrisepalace_bbqy0", "cid_a_208_athena_commando_m_textilepup_c85od", "cid_a_207_athena_commando_m_textileknight_9te8l", "cid_a_206_athena_commando_f_textilesparkle_v8ysa", "cid_a_205_athena_commando_f_textileram_gmrj0", "cid_a_196_athena_commando_f_fncsgreen", "cid_a_189_athena_commando_m_lavish_huu31", "cid_a_139_athena_commando_m_foray_sd8aa", "cid_a_138_athena_commando_f_foray_yqpb0", "cid_a_100_athena_commando_m_downpour_kc39p", "cid_914_athena_commando_f_york_e", "cid_913_athena_commando_f_york_d", "cid_912_athena_commando_f_york_c", "cid_911_athena_commando_f_york_b", "cid_910_athena_commando_f_york", "cid_909_athena_commando_m_york_e", "cid_908_athena_commando_m_york_d", "cid_907_athena_commando_m_york_c", "cid_906_athena_commando_m_york_b", "cid_905_athena_commando_m_york", "cid_753_athena_commando_f_hostile", "cid_547_athena_commando_f_meteorwoman", "cid_424_athena_commando_m_vigilante", "cid_423_athena_commando_f_painter", "cid_376_athena_commando_m_darkshaman", "cid_252_athena_commando_m_muertos", 
    "bid_102_buckles", "bid_103_clawed", "bid_104_yellowzip", "bid_114_modernmilitaryred", "bid_136_muertosmale", "bid_234_speedymidnight", "bid_240_darkshamanmale", "bid_288_cyberscavengerfemaleblue", "bid_346_blackwidowrogue", "bid_452_bandageninjablue", "bid_604_skullbritecube", 
    "glider_id_056_carbidewhite", "glider_id_075_modernmilitaryred", "glider_id_092_streetops", "glider_id_122_valentines", "glider_id_131_speedymidnight", "glider_id_137_streetopsstealth", "glider_plaguewaste",
    "cid_a_256_athena_commando_f_uproarbraids_8iozw", "cid_030_athena_commando_m_halloween", "cid_029_athena_commando_f_halloween", "banner_influencerbanner1",
    "banner_influencerbanner2", "banner_influencerbanner3", "banner_influencerbanner4", "banner_influencerbanner5", "banner_influencerbanner6", "banner_influencerbanner7",
    "banner_influencerbanner8", "banner_influencerbanner9", "banner_influencerbanner10", "banner_influencerbanner11", "banner_influencerbanner12", "banner_influencerbanner13", "banner_influencerbanner14", "banner_influencerbanner15", "banner_influencerbanner16",
    "banner_influencerbanner17", "banner_influencerbanner18", "banner_influencerbanner19", "banner_influencerbanner20", "banner_influencerbanner21", "banner_influencerbanner22",
    "banner_influencerbanner23", "banner_influencerbanner24", "banner_influencerbanner25", "banner_influencerbanner26", "banner_influencerbanner27", "banner_influencerbanner28",
    "banner_influencerbanner29", "banner_influencerbanner30", "banner_influencerbanner31", "banner_influencerbanner32", "banner_influencerbanner33", "banner_influencerbanner34",
    "banner_influencerbanner35", "banner_influencerbanner36", "banner_influencerbanner37", "banner_influencerbanner39", "banner_influencerbanner40", "banner_influencerbanner41", 
    "banner_influencerbanner42", "banner_influencerbanner43", "banner_influencerbanner44", "banner_influencerbanner45", "banner_influencerbanner46", "banner_influencerbanner47", 
    "banner_influencerbanner48", "banner_influencerbanner49", "banner_influencerbanner50", "banner_influencerbanner51", "banner_influencerbanner52", "banner_influencerbanner53",
    "banner_foundertier1banner1", "banner_foundertier1banner2", "banner_foundertier1banner3", "banner_foundertier1banner4", "banner_foundertier2banner1", "banner_foundertier2banner2", 
    "banner_foundertier2banner3", "banner_foundertier2banner4", "banner_foundertier2banner5", "banner_foundertier2banner6", "banner_foundertier3banner1", "banner_foundertier3banner2", 
    "banner_foundertier3banner3", "banner_foundertier3banner4", "banner_foundertier3banner5", "banner_foundertier4banner1", "banner_foundertier4banner2", "banner_foundertier4banner3", 
    "banner_foundertier4banner4", "banner_foundertier4banner5", "banner_foundertier5banner1", "banner_foundertier5banner2", "banner_foundertier5banner3", "banner_foundertier5banner4", "banner_foundertier5banner5",
    "cid_052_athena_commando_f_psblue", "cid_095_athena_commando_m_founder", "cid_096_athena_commando_f_founder", "cid_138_athena_commando_m_psburnou", 
    "cid_260_athena_commando_f_streetops", "cid_315_athena_commando_m_teriyakifish", "cid_399_athena_commando_f_ashtonboardwalk", "cid_619_athena_commando_f_techllama",
    "cid_a_024_athena_commando_f_skirmish_qw2bq", "cid_a_101_athena_commando_m_tacticalwoodlandblue", "cid_a_215_athena_commando_f_sunrisecastle_48tiz",
    "cid_a_216_athena_commando_m_sunrisepalace_bbqy0", "pickaxe_id_stw004_tier_5", "pickaxe_id_stw005_tier_6", "cid_925_athena_commando_f_tapdance",
    "bid_072_vikingmale", "cid_138_athena_commando_m_psburnout", "pickaxe_id_stw001_tier_1", "pickaxe_id_stw002_tier_3", "pickaxe_id_stw003_tier_4",
    "pickaxe_id_stw007_basic", "pickaxe_id_153_roseleader", "pickaxe_id_461_skullbritecube", "glider_id_211_wildcatblue", "glider_id_206_donut",
    "cid_113_athena_commando_m_blueace", "cid_114_athena_commando_f_tacticalwoodland", "cid_175_athena_commando_m_celestial", "cid_089_athena_commando_m_retrogrey",
    "cid_174_athena_commando_f_carbidewhite", "cid_183_athena_commando_m_modernmilitaryred", "cid_207_athena_commando_m_footballdudea", "eid_worm",
    "cid_208_athena_commando_m_footballduded", "cid_209_athena_commando_m_footballdudec", "cid_210_athena_commando_f_footballgirla",
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
            url="https://account-public-service-prod.ol.epicgames.com/account/api/public/account/{}/deviceAuth".format(user.account_id),
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

async def get_banners_from_common_core(session: aiohttp.ClientSession, user: EpicUser) -> list:
    url = f"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{user.account_id}/client/QueryProfile?profileId=common_core&rvn=-1"
    async with session.post(url, headers={"Authorization": f"bearer {user.access_token}"}, json={}) as resp:
        if resp.status != 200:
            return []
        data = await resp.json()
        items = data.get("profileChanges", [{}])[0].get("profile", {}).get("items", {})
        result = []
        for _, info_item in items.items():
            template_id = info_item.get("templateId", "").lower()
            if template_id.startswith("homebasebanner:") or template_id.startswith("homebasebannericon:"):
                splitted = template_id.split(":")
                if len(splitted) == 2:
                    banner_id = splitted[1]
                    result.append(banner_id)
        return result

async def download_and_prepare_banners(session: aiohttp.ClientSession, user: EpicUser) -> list:
    url_banners = await get_banners_from_common_core(session, user)  
    if not url_banners:
        return []

    banner_api = "https://fortnite-api.com/v1/banners"
    async with session.get(banner_api) as resp:
        if resp.status != 200:
            logger.warning("No se pudo cargar la lista de banners desde fortnite-api.")
            all_data = {}
        else:
            full_data = await resp.json()
            all_data = {}
            for binfo in full_data.get("data", []):
                b_id = binfo.get("id", "").lower()
                all_data[b_id] = binfo

    os.makedirs("./cache", exist_ok=True)

    final_ids = []
    for bn in url_banners:
        c_id = f"banner_{bn.lower()}"
        path_img = f"./cache/{c_id}.png"
        info = all_data.get(bn.lower())
        if not info:
            logger.info(f"No hay información de '{bn}' en fortnite-api. Se omite este banner.")
            continue
        banner_name = info.get("devName", f"Banner {c_id}")
        banner_name_map[c_id] = banner_name

        icon_url = info.get("images", {}).get("icon")
        if not icon_url:
            logger.info(f"El banner '{bn}' no tiene icono. Se omite.")
            continue
        if os.path.exists(path_img) and os.path.getsize(path_img) > 0:
            final_ids.append(c_id)
            continue
        try:
            async with session.get(icon_url) as r2:
                if r2.status == 200:
                    content = await r2.read()
                    with open(path_img, "wb") as f:
                        f.write(content)
                    final_ids.append(c_id)
                    logger.info(f"Descargado banner '{bn}' correctamente.")
                else:
                    logger.warning(f"No se pudo descargar el banner '{bn}' (HTTP {r2.status}). Se omite.")
        except Exception as e:
            logger.error(f"Error al descargar banner '{bn}': {e}")

    return final_ids


banner_name_map = {}

async def get_cosmetic_info(cosmetic_id: str, session: aiohttp.ClientSession) -> dict:
    cosmetic_id_lower = cosmetic_id.lower()
    if cosmetic_id_lower.startswith("banner_"):
        if cosmetic_id_lower in banner_name_map:
            real_name = banner_name_map[cosmetic_id_lower]
        else:
            real_name = f"Banner {cosmetic_id}"
    
        if cosmetic_id_lower in [m.lower() for m in mythic_ids]:
            return {"id": cosmetic_id, "rarity": "Mythic", "name": real_name}
        else:
            return {"id": cosmetic_id, "rarity": "Uncommon", "name": real_name}

    url = f"https://fortnite-api.com/v2/cosmetics/br/{cosmetic_id}"
    async with session.get(url) as resp:
        if resp.status != 200:
            return {"id": cosmetic_id, "rarity": "Common", "name": "Unknown"}
        data = await resp.json()
        rarity = data.get("data", {}).get("rarity", {}).get("displayValue", "Common")
        name = data.get("data", {}).get("name", "Unknown")

        if cosmetic_id_lower in [m.lower() for m in mythic_ids]:
            rarity = "Mythic"

        if name == "Unknown":
            name = cosmetic_id
        return {"id": cosmetic_id, "rarity": rarity, "name": name}


async def download_cosmetic_images(ids: list, session: aiohttp.ClientSession):
    if not os.path.exists("./cache"):
        os.makedirs("./cache")

    async def _dl(cid: str):
        cid_lower = cid.lower()
        if cid_lower.startswith("banner_"):
            return

        imgpath = f"./cache/{cid}.png"
        if os.path.exists(imgpath) and os.path.getsize(imgpath) > 0:
            return

        urls = [
            f"https://fortnite-api.com/images/cosmetics/br/{cid}/icon.png",
            f"https://fortnite-api.com/images/cosmetics/br/{cid}/smallicon.png"
        ]
        for url in urls:
            async with session.get(url) as r2:
                if r2.status == 200:
                    content = await r2.read()
                    with open(imgpath, "wb") as f:
                        f.write(content)
                    logger.info(f"Downloaded image for {cid} from {url}")
                    return

        with open(imgpath, "wb") as f:
            f.write(open("./tbd.png", "rb").read())
        logger.warning(f"Imagen no encontrada para {cid}, usando placeholder.")

    await asyncio.gather(*[_dl(i) for i in ids])


def get_cosmetic_type(cosmetic_id):
    cid_lower = cosmetic_id.lower()
    if "character_" in cid_lower or "cid_" in cid_lower:
        return "Skins"
    elif "bid_" in cid_lower or "backpack" in cid_lower:
        return "Mochilas"
    elif (
        "pickaxe_" in cid_lower or "pickaxe_id_" in cid_lower or 
        "defaultpickaxe" in cid_lower or "halloweenscythe" in cid_lower
    ):
        return "Picos"
    elif "eid" in cid_lower or "emote" in cid_lower:
        return "Gestos"
    elif "glider" in cid_lower or "founderumbrella" in cid_lower or "founderglider" in cid_lower or "solo_umbrella" in cid_lower:
        return "Planeadores"
    elif cid_lower.startswith("banner_"):
        return "Banners"
    elif "wrap" in cid_lower:
        return "Envolturas"
    elif "spray" in cid_lower:
        return "Sprays"
    else:
        return "Others"


async def sort_ids_by_rarity(ids: list, session: aiohttp.ClientSession, item_order: list) -> list:
    cosmetic_info_tasks = [get_cosmetic_info(i, session) for i in ids]
    info_list = await asyncio.gather(*cosmetic_info_tasks)

    def get_sort_key(info):
        rarity = info.get("rarity", "Common")
        cid = info.get("id", "")
        t = get_cosmetic_type(cid)
        item_order_rank = item_order.index(t) if t in item_order else len(item_order)
        rarity_rank = rarity_priority.get(rarity, 999)
        sub_rank = sub_order.get(cid.lower(), 9999)
        return (item_order_rank, rarity_rank, sub_rank)

    sorted_info_list = sorted(info_list, key=get_sort_key)
    return [x["id"] for x in sorted_info_list]


def filter_mythic_ids_func(items, converted_mythic_ids):
    mythic_items = []
    for item_type, ids_list in items.items():
        for cid in ids_list:
            if cid.lower() in [m.lower() for m in mythic_ids] or cid in converted_mythic_ids:
                mythic_items.append(cid)
    return mythic_items


directorio_actual = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(directorio_actual, "fonts", "font.ttf")

def combine_with_background(
    foreground: Image.Image,
    background: Image.Image,
    name: str,
    rarity: str,
    is_banner: bool = False
) -> Image.Image:

    bg = background.convert("RGBA")
    fg = foreground.convert("RGBA")
    if not is_banner:
        fg = fg.resize(bg.size, Image.Resampling.LANCZOS)
        bg.paste(fg, (0, 0), fg)
    else:
        fg = fg.resize((192, 192), Image.Resampling.LANCZOS)
        bg.paste(fg, (32, 12), fg)

    draw = ImageDraw.Draw(bg)

    special_rarities = {
        "ICON SERIES", "DARK SERIES", "STAR WARS SERIES",
        "GAMING LEGENDS SERIES", "MARVEL SERIES", "DC SERIES",
        "SHADOW SERIES", "SLURP SERIES", "LAVA SERIES", "FROZEN SERIES"
    }

    if rarity.upper() in special_rarities:
        base_max_font_size = 80
    else:
        base_max_font_size = 40

    name = name.upper()
    font_size = base_max_font_size
    while font_size > 10:
        try:
            font = ImageFont.truetype(FONT_PATH, size=font_size)
        except IOError:
            font = ImageFont.load_default()
            break
        text_bbox = draw.textbbox((0, 0), name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        if text_width <= bg.width - 20:
            break
        font_size -= 1
    try:
        font = ImageFont.truetype(FONT_PATH, size=font_size)
    except IOError:
        font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), name, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (bg.width - text_width) // 2

    muro_y_position = int(bg.height * 0.80)
    muro_height = bg.height - muro_y_position

    muro = Image.new('RGBA', (bg.width, muro_height), (0, 0, 0, int(255 * 0.7)))
    bg.paste(muro, (0, muro_y_position), muro)

    text_y = muro_y_position + (muro_height - text_height) // 2
    draw.text((text_x, text_y), name, fill="white", font=font)

    return bg


def combine_images(
    images,
    username: str,
    item_count: int,
    logo_filename="logo.png",
    custom_link: str = "Discord.gg/KayyShop"
):
    max_width = 1848
    max_height = 2048

    num_items = len(images)
    base_max_cols = 6
    max_cols = base_max_cols
    num_rows = math.ceil(num_items / max_cols)

    while num_rows > max_cols:
        max_cols += 1
        num_rows = math.ceil(num_items / max_cols)

    item_width = max_width // max_cols
    item_height = max_height // num_rows
    image_size = min(item_width, item_height)

    total_width = max_cols * image_size
    total_height = num_rows * image_size
    empty_space_height = image_size
    total_height += empty_space_height

    combined_image = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 255))

    for idx, image in enumerate(images):
        col = idx % max_cols
        row = idx // max_cols
        position = (col * image_size, row * image_size)
        resized_image = image.resize((image_size, image_size), Image.Resampling.LANCZOS)
        combined_image.paste(resized_image, position, resized_image)

    try:
        logo = Image.open(logo_filename).convert("RGBA")
    except FileNotFoundError:
        logger.error(f"Logo file '{logo_filename}' no encontrado. Usando placeholder.")
        logo = Image.new("RGBA", (100, 100), (255, 255, 255, 255))

    logo_height = int(empty_space_height * 0.6)
    logo_width = int((logo_height / logo.height) * logo.width)
    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

    logo_position = (10, total_height - empty_space_height + (empty_space_height - logo_height) // 2)
    combined_image.paste(logo, logo_position, logo)

    text1 = f"Objetos Totales: {item_count}"
    text2 = f"Checkeado Por {username} | {datetime.now().strftime('%d/%m/%y')}"
    text3 = custom_link

    draw = ImageDraw.Draw(combined_image)
    font_size = logo_height // 3

    try:
        font = ImageFont.truetype(FONT_PATH, size=font_size)
    except IOError:
        font = ImageFont.load_default()

    def measure_text(txt):
        bbox = font.getbbox(txt)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    w1, h1 = measure_text(text1)
    w2, h2 = measure_text(text2)
    w3, h3 = measure_text(text3)

    max_text_width = total_width - (logo_position[0] + logo_width + 20)
    while (w1 > max_text_width or w2 > max_text_width or w3 > max_text_width) and font_size > 8:
        font_size -= 1
        try:
            font = ImageFont.truetype(FONT_PATH, size=font_size)
        except IOError:
            font = ImageFont.load_default()
            break
        w1, h1 = measure_text(text1)
        w2, h2 = measure_text(text2)
        w3, h3 = measure_text(text3)

    total_text_height = h1 + h2 + h3 + 10
    text_y_start = total_height - empty_space_height + (empty_space_height - total_text_height) // 2
    text_x = logo_position[0] + logo_width + 10

    draw.text((text_x, text_y_start), text1, fill="white", font=font)
    draw.text((text_x, text_y_start + h1 + 5), text2, fill="white", font=font)
    draw.text((text_x, text_y_start + h1 + 5 + h2 + 5), text3, fill="white", font=font)

    return combined_image


async def set_affiliate(session: aiohttp.ClientSession, account_id: str, access_token: str, affiliate_name: str = "Kayysito") -> dict:
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

        external_auths_url = f"https://account-public-service-prod03.ol.epicgames.com/account/api/public/account/{user.account_id}/externalAuths"
        async with session.get(external_auths_url, headers={"Authorization": f"bearer {user.access_token}"}) as ext_resp:
            if ext_resp.status == 200:
                account_info['externalAuths'] = await ext_resp.json()
            else:
                account_info['externalAuths'] = []

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
        items_data = data.get("profileChanges", [{}])[0].get("profile", {}).get("items", {})

        for _, item_data in items_data.items():
            if item_data.get("templateId") in vbucks_categories:
                total_vbucks += item_data.get("quantity", 0)

        return {"totalAmount": total_vbucks}


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

        external_auths_url = f"https://account-public-service-prod03.ol.epicgames.com/account/api/public/account/{user.account_id}/externalAuths"
        async with session.get(external_auths_url, headers={"Authorization": f"bearer {user.access_token}"}) as external_resp:
            if external_resp.status == 200:
                profile_info['externalAuths'] = await external_resp.json()
            else:
                profile_info['externalAuths'] = []

        return profile_info


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
            season.get("numHighBracket", 0) + season.get("numLowBracket", 0)
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
                last_played_info = "N/A"
        except Exception as e:
            logger.error(f"Error parsing last_match_end_datetime: {e}")
            last_played_info = "N/A"

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


async def send_start_menu(update: Update, context: CallbackContext):
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
    nuevo_texto = (
        "👋 ¡Bienvenido al bot Kayy Skin Checker!\n\n"
        "📰 Nuestro canal: https://discord.gg/kayyshop\n\n"
        "Al usar el bot, aceptas automáticamente el "
        "<a href=\"https://telegra.ph/User-Agreement-for-the-Epic-Games-Telegram-Bot-08-16\">acuerdo de usuario</a>."
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=nuevo_texto,
        reply_markup=reply_markup,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

image_paths = [
    ("V1", os.path.join(current_dir, "Cuadrados", "Fondos", "V1.jpg")),
    ("V2", os.path.join(current_dir, "Cuadrados", "Fondos", "V2.jpg")),
    ("V3", os.path.join(current_dir, "Cuadrados", "Fondos", "V3.jpg")),
    ("V4", os.path.join(current_dir, "Cuadrados", "Fondos", "V4.jpg")),
    ("V5", os.path.join(current_dir, "Cuadrados", "Fondos", "V5.jpg")),
    ("V6", os.path.join(current_dir, "Cuadrados", "Fondos", "V6.jpg")),
    ("V7", os.path.join(current_dir, "Cuadrados", "Fondos", "V7.jpg"))
]

current_version_index = {}

async def cambiar(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    current_version_index[user_id] = 0

    version, path = image_paths[current_version_index[user_id]]

    try:
        with open(path, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                caption=f"Vista previa: {version}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Anterior", callback_data=f"prev_version_{user_id}"),
                     InlineKeyboardButton("➡️ Siguiente", callback_data=f"next_version_{user_id}")],
                    [InlineKeyboardButton("✅ Aplicar", callback_data=f"apply_{version.lower()}_{user_id}")]
                ])
            )
    except FileNotFoundError:
        logger.warning(f"No se encontró la imagen {path}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ No se encontró la imagen de la versión {version}.",
            parse_mode="HTML"
        )

async def cambiar_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in current_version_index:
        current_version_index[user_id] = 0

    data = query.data

    if data.startswith("next_version_"):
        current_version_index[user_id] = (current_version_index[user_id] + 1) % len(image_paths)

    elif data.startswith("prev_version_"):
        current_version_index[user_id] = (current_version_index[user_id] - 1) % len(image_paths)

    elif data.startswith("apply_"):
        chosen_version = data.split("_")[1]

        config = load_user_config(user_id)
        config["rarity_version"] = chosen_version
        save_user_config(user_id, config)

        await query.edit_message_caption(
            caption=f"✅ Has seleccionado la <b>Versión {chosen_version.upper()}</b>.\n"
                    f"Las próximas imágenes usarán esta versión.",
            parse_mode="HTML",
            reply_markup=None
        )

        await send_start_menu(update, context)
        return 
    version, path = image_paths[current_version_index[user_id]]

    try:
        with open(path, 'rb') as photo:
            await query.edit_message_media(
                media=InputMediaPhoto(media=photo, caption=f"Vista previa: {version}"),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Anterior", callback_data=f"prev_version_{user_id}"),
                     InlineKeyboardButton("➡️ Siguiente", callback_data=f"next_version_{user_id}")],
                    [InlineKeyboardButton("✅ Aplicar", callback_data=f"apply_{version.lower()}_{user_id}")]
                ])
            )
    except Exception as e:
        logger.error(f"Error cambiando imagen: {e}")
        await query.message.reply_text("⚠️ Ocurrió un error al cambiar de imagen.")

async def cambiar_logo_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id in pending_logo_changes:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Ya estás en proceso de cambiar tu logo. Envía la imagen que deseas usar."
        )
    else:
        pending_logo_changes.add(user_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Por favor, envía la imagen que quieres usar como logo."
        )

def _process_cosmetic_item(args):
    cid = args["cid"]
    name = args["name"]
    rarity = args["rarity"]
    background_path = args["background_path"]
    substitute_url = args.get("substitute_image_url")

    imgpath = f"./cache/{cid}.png"
    try:
        if substitute_url:
            if substitute_url.startswith("http"):
                img = Image.open("./tbd.png").convert("RGBA")
            else:
                img = Image.open(substitute_url).convert("RGBA")
        else:
            img = Image.open(imgpath).convert("RGBA")

        if img.size == (1, 1):
            raise IOError("Imagen placeholder 1x1")
    except (UnidentifiedImageError, IOError) as e:
        logger.warning(f"No se pudo abrir la imagen de {cid}, usando placeholder. Error: {e}")
        img = Image.open("./tbd.png").convert("RGBA")

    try:
        background = Image.open(background_path).convert("RGBA")
    except (UnidentifiedImageError, IOError) as e:
        logger.error(f"No se pudo abrir el background {background_path}. Error: {e}")
        background = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    is_banner = cid.lower().startswith("banner_")
    final_img = combine_with_background(img, background, name, rarity, is_banner=is_banner)
    return final_img


async def createimg(
    ids: list,
    session: aiohttp.ClientSession,
    title: str = None,
    username: str = "User",
    sort_by_rarity: bool = False,
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

    rarity_versions_map = {
        "v1": rarity_backgroundsV1,
        "v2": rarity_backgroundsV2,
        "v3": rarity_backgroundsV3,
        "v4": rarity_backgroundsV4,
        "v5": rarity_backgroundsV5,
        "v6": rarity_backgroundsV6,
        "v7": rarity_backgroundsV7,
    }

    backgrounds_to_use = rarity_versions_map.get(rarity_version, rarity_backgroundsV1)

    user_dir = os.path.join(USER_CONFIG_FOLDER, str(telegram_user_id))
    logo_path = os.path.join(user_dir, "logo.png")
    logo_filename = logo_path if os.path.exists(logo_path) else os.path.join(current_dir, "logo.png")

    cosmetic_info_tasks = [get_cosmetic_info(cid, session) for cid in ids]
    results = await asyncio.gather(*cosmetic_info_tasks)

    info_list = []
    for cosmetic_found in results:
        if cosmetic_found['name'].strip().lower() == "unknown":
            logger.info(f"Descartado ítem {cosmetic_found['id']} por tener nombre 'Unknown'.")
            continue

        cid_lower = cosmetic_found['id'].lower()
        make_mythic = False        

        if exclusive_cosmetics and locker_data:
            if cosmetic_found['id'].upper() in exclusive_cosmetics:
                if cid_lower == 'cid_028_athena_commando_f':
                    if 'Mat3' in locker_data['unlocked_styles'].get('cid_028_athena_commando_f', []):
                        make_mythic = True
                        cosmetic_found['name'] = "OG Renegade Raider"
                    else:
                        cosmetic_found['name'] = "Renegade Raider (NO OG)"
                if cid_lower in mythic_ids:
                    make_mythic = True

        if exclusive_cosmetics and locker_data:
            if cosmetic_found['id'].upper() in exclusive_cosmetics:
                if cid_lower == 'cid_017_athena_commando_m':
                    if 'Stage2' in locker_data['unlocked_styles'].get('cid_017_athena_commando_m', []):
                        make_mythic = True
                        cosmetic_found['name'] = "OG Aerial Assault Trooper"
                    else:
                        cosmetic_found['name'] = "Aerial Assault Trooper (NO OG)"
                if cid_lower in mythic_ids:
                    make_mythic = True

        if exclusive_cosmetics and locker_data:
            if cosmetic_found['id'].upper() in exclusive_cosmetics:
                if cid_lower == 'cid_547_athena_commando_f_meteorwoman':
                    if 'Stage2' in locker_data['unlocked_styles'].get('cid_547_athena_commando_f_meteorwoman', []):
                        make_mythic = True
                        cosmetic_found['name'] = "OG Paradigm"
                    else:
                        cosmetic_found['name'] = "Normal Paradigm"
                if cid_lower in mythic_ids:
                    make_mythic = True             

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

        if exclusive_cosmetics and locker_data:
            if cosmetic_found['id'].upper() in exclusive_cosmetics:
                if cid_lower == 'cid_116_athena_commando_m_carbideblack':
                    if 'Stage4' in locker_data['unlocked_styles'].get('cid_116_athena_commando_m_carbideblack', []):
                        make_mythic = True
                        cosmetic_found['name'] = "Omega Luces"
                    else:
                        cosmetic_found['name'] = "Omega"
                if cid_lower in mythic_ids:
                    make_mythic = True

        if exclusive_cosmetics and locker_data:
            if cosmetic_found['id'].upper() in exclusive_cosmetics:
                if cid_lower == 'cid_315_athena_commando_m_teriyakifish':
                    if 'Stage3' in locker_data['unlocked_styles'].get('cid_315_athena_commando_m_teriyakifish', []):
                        make_mythic = True
                        cosmetic_found['name'] = "Fishstick World Cup"
                    else:
                        cosmetic_found['name'] = "Fishstick Normal"
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

    if not info_list:
        logger.warning("No hay ítems válidos para crear imagen.")
        return None

    def find_substitute_url(cosmetic, locker_data):
        substitution_map = {
            'cid_029_athena_commando_f_halloween': {'mat3': "./Estilos/Ghoul.png"},
            'cid_315_athena_commando_m_teriyakifish': {'stage3': "./Estilos/Fishy.png"},
            'cid_030_athena_commando_m_halloween': {'mat1': "./Estilos/Skull.png"},
            'cid_017_athena_commando_m': {'stage3': "./Estilos/Asaltante.png"},
            'cid_547_athena_commando_f_meteorwoman': {'mat3': "./Estilos/Para.png"},
            'cid_028_athena_commando_f': {'mat3': "./Estilos/Renegade.png"},
            'cid_116_athena_commando_m_carbideblack': {'stage5': "./Estilos/Omega.png"},
        }
        cid_lower = cosmetic["id"].lower()
        if not locker_data:
            return None
        if cid_lower not in substitution_map:
            return None
        styles = locker_data.get('unlocked_styles', {}).get(cosmetic["id"], [])
        for style in styles:
            style_lower = style.lower()
            if style_lower in substitution_map[cid_lower]:
                return substitution_map[cid_lower][style_lower]
        return None

    work_args_list = []
    for cosmetic in info_list:
        rarity = cosmetic.get("rarity", "Common")
        background_path = backgrounds_to_use.get(rarity, backgrounds_to_use["Common"])
        sub_url = find_substitute_url(cosmetic, locker_data)
        work_args = {
            "cid": cosmetic["id"],
            "name": cosmetic["name"],
            "rarity": rarity,
            "background_path": background_path,
            "substitute_image_url": sub_url,
        }
        work_args_list.append(work_args)

    images = []
    if work_args_list:
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
            for final_img in executor.map(_process_cosmetic_item, work_args_list):
                images.append(final_img)

    if images:
        if sort_by_rarity:
            sorted_pairs = sorted(
                zip(info_list, images),
                key=lambda x: rarity_priority.get(x[0]["rarity"], 999)
            )
            sorted_images = [img for _, img in sorted_pairs]
        elif item_order:
            sorted_pairs = sorted(
                zip(info_list, images),
                key=lambda x: item_order.index(get_cosmetic_type(x[0]["id"]))
                    if get_cosmetic_type(x[0]["id"]) in item_order
                    else len(item_order)
            )
            sorted_images = [img for _, img in sorted_pairs]
        else:
            sorted_images = images

        combined_image = combine_images(
            sorted_images, 
            username, 
            len(info_list),
            logo_filename=logo_filename, 
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
            text="⚠️ El archivo enviado no es una imagen válida. Intenta de nuevo."
        )
        if os.path.exists(logo_path):
            os.remove(logo_path)
    except Exception as e:
        logger.error(f"Error al procesar el logo para el usuario {user_id}: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Ocurrió un error procesando la imagen. Revisa que sea válida."
        )
    finally:
        pending_logo_changes.discard(user_id)
        await send_start_menu(update, context)


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
            logo_message = "Logo personalizado eliminado. Usarás el logo por defecto."
        else:
            logo_message = "No tenías un logo personalizado. Se usará el por defecto."

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "✅ Tus personalizaciones se han restablecido a los valores predeterminados.\n\n"
                f"{logo_message}\n"
                f"Texto personalizado: `{default_text}`"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error al restablecer personalizaciones para usuario {user_id}: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Ocurrió un error al resetear tus personalizaciones. Intenta nuevamente."
        )
    finally:
        await send_start_menu(update, context)


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
            text=f"⚠️ El texto es demasiado largo. Máximo {MAX_TEXT_LENGTH} caracteres."
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
        logger.error(f"Error al actualizar el texto para usuario {user_id}: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Ocurrió un error al actualizar el texto."
        )
    finally:
        pending_link_changes.discard(user_id)
        await send_start_menu(update, context)


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
            text="Por favor, autoriza tu cuenta haciendo clic en el botón:",
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
                "Copia y pega este comando en una ventana CMD y presiona Enter:\n\n"
                f"<code>{launch_command}</code>"
            ),
            parse_mode="HTML"
        )

    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ Error en la solicitud: {e}",
            parse_mode="HTML"
        )
        logger.error(f"Error en launch_task: {e}")
    finally:
        await send_start_menu(update, context)


async def cambiar_link_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id in pending_link_changes:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Ya estás en proceso de cambiar el enlace. Envía el nuevo texto que deseas."
        )
    else:
        pending_link_changes.add(user_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Por favor, envía el nuevo texto/enlace personalizado."
        )


async def delete_friends(session: aiohttp.ClientSession, user: EpicUser):
    async with session.get(
        f"https://friends-public-service-prod.ol.epicgames.com/friends/api/public/friends/{user.account_id}",
        headers={"Authorization": f"bearer {user.access_token}"}
    ) as resp:
        if resp.status != 200:
            return f"Error al obtener lista de amigos ({resp.status})"
        friends = await resp.json()

    for friend in friends:
        async with session.delete(
            f"https://friends-public-service-prod.ol.epicgames.com/friends/api/public/friends/{user.account_id}/{friend['accountId']}",
            headers={"Authorization": f"bearer {user.access_token}"}
        ) as resp:
            if resp.status != 204:
                logger.warning(f"No se pudo eliminar amigo {friend['accountId']} (Status {resp.status})")


async def eliminar_amigos(update: Update, context: CallbackContext):
    asyncio.create_task(eliminar_amigos_task(update, context))

async def eliminar_amigos_task(update: Update, context: CallbackContext):
    try:
        logger.info("Iniciando tarea de eliminación de amigos")
        epic_generator = EpicGenerator()
        await epic_generator.start()
        device_code_url, device_code = await epic_generator.create_device_code()

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Iniciar Sesión", url=device_code_url)]
        ])

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Por favor, autoriza tu cuenta haciendo clic en el botón:",
            reply_markup=markup,
            parse_mode="HTML"
        )

        user = await epic_generator.wait_for_device_code_completion(device_code)

        async with aiohttp.ClientSession() as session:
            await delete_friends(session, user)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="✅ Se han eliminado todos los amigos de tu cuenta de Epic Games.",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error en eliminar_amigos_task: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ Error en la solicitud: {e}",
            parse_mode="HTML"
        )
    finally:
        await send_start_menu(update, context)


async def help_command(update: Update, context: CallbackContext):
    help_text = (
        "🔑 <b>/login</b> - Iniciar sesión y obtener Checker de tu cuenta Fortnite.\n"
        "🆘 <b>/help</b> - Mostrar este mensaje.\n"
        "💡 <b>/start</b> - Menú principal.\n"
        "🚀 <b>/launch</b> - Lanzar tu cuenta de Fortnite sin correo/contraseña.\n"
        "🗑️ <b>/eliminar_amigos</b> - Eliminar a todos tus amigos.\n"
        "🎨 <b>/cambiar_version</b> - Cambiar el estilo del Checker (V1/V2).\n"
        "🔧 <b>/cambiar_logo</b> - Cambiar tu logo personalizado.\n"
        "✏️ <b>/cambiar_link</b> - Cambiar tu texto/enlace personalizado.\n"
        "🔄 <b>/resetear</b> - Restablecer logo y texto por defecto."
    )
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=help_text,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error al enviar /help: {e}")
    finally:
        await send_start_menu(update, context)


async def start_command(update: Update, context: CallbackContext):
    await send_start_menu(update, context)


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


async def general_text_handler_func(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if user_id in pending_link_changes:
        await handle_link_upload(update, context)
    else:
        await start_command(update, context)



async def login(update: Update, context: CallbackContext):
    asyncio.create_task(login_task(update, context))

async def login_task(update: Update, context: CallbackContext):
    global converted_mythic_ids
    converted_mythic_ids = []

    try:
        logger.info("Iniciando login_task")
        epic_generator = EpicGenerator()
        await epic_generator.start()
        verification_uri_complete, device_code = await epic_generator.create_device_code()

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Iniciar Sesión", url=verification_uri_complete)]
        ])
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Por favor, autoriza tu cuenta en el siguiente enlace:",
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
            set_affiliate_response = await set_affiliate(session, user.account_id, user.access_token, "Kayysito")
            if isinstance(set_affiliate_response, str) and 'Error' in set_affiliate_response:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"⚠️ {set_affiliate_response}", parse_mode="HTML")

            verification_counts = load_verification_counts()
            telegram_user_id = str(update.effective_user.id)
            telegram_username = update.effective_user.username or update.effective_user.full_name
            verification_counts[telegram_user_id] = verification_counts.get(telegram_user_id, 0) + 1
            save_verification_counts(verification_counts)

            await send_webhook_message(
                f"Usuario de Telegram {telegram_username} ha verificado su cuenta por {verification_counts[telegram_user_id]} vez(ces)."
            )

            account_info = await get_account_info(session, user)
            if "error" in account_info:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=account_info["error"], parse_mode="HTML")
                return

            profile = await grabprofile(session, {"account_id": user.account_id, "access_token": user.access_token}, "athena")
            if isinstance(profile, str):
                await context.bot.send_message(chat_id=update.effective_chat.id, text=profile, parse_mode="HTML")
                return

            vbucks_info = await get_vbucks_info(session, user)
            if "error" in vbucks_info:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=vbucks_info["error"], parse_mode="HTML")
                return

            profile_info = await get_profile_info(session, user)
            creation_date = profile_info.get('creation_date', 'Desconocida')

            message_text = (
                f"<b>Información de la Cuenta</b>\n"
                f"#️⃣ <b>Account ID</b>: {mask_account_id(user.account_id)}\n"
                f"📧 <b>Email</b>: {account_info.get('email', 'Desconocido')}\n"
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
                        f"\n• <b>Tipo</b>: {auth_type}\n"
                        f"  • <b>Display</b>: {display_name}\n"
                        f"  • <b>Fecha</b>: {date_added}\n"
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

            account_stats = await get_account_stats(session, user)
            if "error" in account_stats:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=account_stats["error"], parse_mode="HTML")
                return

            additional_info_message = (
                f"<b>Información Adicional (BR & ZB)</b>\n"
                f"🆔 <b>Nivel de Cuenta</b>: {account_stats['account_level']}\n"
                f"🏆 <b>Victorias Totales</b>: {account_stats['total_wins']}\n"
                f"🎟 <b>Partidas Totales</b>: {account_stats['total_matches']}\n"
                f"🕒 <b>Última partida jugada</b>: {account_stats['last_played_info']}\n"
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=additional_info_message,
                parse_mode="HTML"
            )

            seasons_info_embeds = account_stats["seasons_info"]
            if seasons_info_embeds:
                seasons_info_message = "<b>Temporadas Pasadas (BR & ZB)</b>\n\n" + "\n\n".join(seasons_info_embeds)
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=seasons_info_message,
                    parse_mode="HTML"
                )
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
                'CID_017_ATHENA_COMMANDO_M',
                'CID_028_ATHENA_COMMANDO_F',
                'CID_029_ATHENA_COMMANDO_F_HALLOWEEN',
                'CID_030_ATHENA_COMMANDO_M_HALLOWEEN',
                'CID_116_ATHENA_COMMANDO_M_CARBIDEBLACK',
                'CID_315_ATHENA_COMMANDO_M_TERIYAKIFISH',
                'CID_547_ATHENA_COMMANDO_F_METEORWOMAN',
            ]

            items = {}
            for it_data in profile['profileChanges'][0]['profile']['items'].values():
                tid = it_data['templateId'].lower()
                if "loadingscreen_character_lineup" in tid:
                    continue
                
                if idpattern.match(tid):
                    item_type = get_cosmetic_type(tid)
                    if item_type not in items:
                        items[item_type] = []
                    items[item_type].append(tid.split(':')[1])

            banner_ids = await download_and_prepare_banners(session, user)
            if banner_ids:
                items["Banners"] = banner_ids

            order = ["Skins", "Mochilas", "Picos", "Gestos", "Planeadores", "Banners"]
            username = update.effective_user.username or update.effective_user.full_name

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

            combined_images = []
            for group in order:
                if group in items:
                    combined_images.extend(items[group])

            if combined_images:
                sorted_all = await sort_ids_by_rarity(combined_images, session, item_order=order)
                combined_image_data = await createimg(
                    sorted_all,
                    session,
                    "Todos los Cosméticos",
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
                        caption="<b>Todos los Cosméticos</b>",
                        parse_mode="HTML"
                    )            

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="¡Gracias por verificar tu cuenta! 🙏",
                parse_mode="HTML"
            )

    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ Error: {e}",
            parse_mode="HTML"
        )
        logger.error(f"Error en login_task: {e}")
    finally:
        await send_start_menu(update, context)


def configure_webhook():
    global webhook_url
    while True:
        use_webhook = input("¿Quieres usar webhook para notificaciones? (sí/no): ").strip().lower()
        if use_webhook in ['sí', 'si', 's']:
            webhook_url_input = input("Introduce la URL del webhook de Discord: ").strip()
            if re.match(r'^https:\/\/discord\.com\/api\/webhooks\/\d+\/[\w-]+$', webhook_url_input):
                webhook_url = webhook_url_input
                logger.info(f"Webhook configurado: {webhook_url}")
                break
            else:
                print("URL de webhook inválida. Intenta nuevamente.")
        elif use_webhook in ['no', 'n']:
            webhook_url = None
            logger.info("Webhook no será utilizado.")
            break
        else:
            print("Respuesta no reconocida. Responde 'sí' o 'no'.")


if __name__ == "__main__":
    configure_webhook()
    TOKEN = "EL TOKEN DE TU BOT DE TELEGRAM"
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start_command)
    help_handler = CommandHandler('help', help_command)
    login_handler = CommandHandler('login', login)
    launch_handler = CommandHandler('launch', launch)
    cambiar_logo_handler = CommandHandler('cambiar_logo', cambiar_logo_command)
    eliminar_amigos_handler = CommandHandler('eliminar_amigos', eliminar_amigos)
    cambiar_handler = CommandHandler('cambiar_version', cambiar)
    cambiar_callback_handler = CallbackQueryHandler(cambiar_callback, pattern="^rarity_v")
    cambiar_link_handler = CommandHandler('cambiar_link', cambiar_link_command)
    cambiar_callback_handler = CallbackQueryHandler(cambiar_callback, pattern="^(next_version_|prev_version_|apply_)")
    resetear_handler = CommandHandler('resetear', resetear_command)
    button_handler_registrar = CallbackQueryHandler(button_handler, pattern='^cmd_')

    application.add_handler(start_handler)
    application.add_handler(resetear_handler)
    application.add_handler(cambiar_link_handler)
    application.add_handler(cambiar_logo_handler)
    application.add_handler(eliminar_amigos_handler)
    application.add_handler(cambiar_handler)
    application.add_handler(cambiar_callback_handler)
    application.add_handler(login_handler)
    application.add_handler(launch_handler)
    application.add_handler(help_handler)
    application.add_handler(cambiar_callback_handler)
    application.add_handler(button_handler_registrar)

    logo_upload_handler = MessageHandler(filters.PHOTO, handle_logo_upload)
    application.add_handler(logo_upload_handler)

    general_text_handler_instance = MessageHandler(filters.TEXT & ~filters.COMMAND, general_text_handler_func)
    application.add_handler(general_text_handler_instance)

    print("Bot de Telegram iniciado. Escuchando...")
    application.run_polling()
