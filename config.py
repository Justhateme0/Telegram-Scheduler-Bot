import os
from dotenv import load_dotenv
import json

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN or BOT_TOKEN == '':
    BOT_TOKEN = ''

ADMIN_IDS = [int(admin_id) for admin_id in os.getenv('ADMIN_IDS', '').split(',') if admin_id]
if not ADMIN_IDS:
    ADMIN_IDS = []

DEFAULT_CONFIG = {
    "channels": {}
}

CONFIG_FILE = "channel_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def add_channel(channel_id, channel_name, interval_minutes):
    config = load_config()
    config["channels"][str(channel_id)] = {
        "name": channel_name,
        "interval_minutes": interval_minutes,
        "queue": []
    }
    save_config(config)
    
def remove_channel(channel_id):
    config = load_config()
    if str(channel_id) in config["channels"]:
        del config["channels"][str(channel_id)]
        save_config(config)
        
def get_channels():
    config = load_config()
    return config["channels"]

def add_post_to_queue(channel_id, post_data):
    config = load_config()
    if str(channel_id) in config["channels"]:
        config["channels"][str(channel_id)]["queue"].append(post_data)
        save_config(config)
        return len(config["channels"][str(channel_id)]["queue"])
    return 0

def remove_post_from_queue(channel_id, post_index):
    config = load_config()
    if str(channel_id) in config["channels"]:
        channel = config["channels"][str(channel_id)]
        if 0 <= post_index < len(channel["queue"]):
            channel["queue"].pop(post_index)
            save_config(config)
            return True
    return False

def get_channel_queue(channel_id):
    config = load_config()
    if str(channel_id) in config["channels"]:
        return config["channels"][str(channel_id)]["queue"]
    return []

def get_channel_interval(channel_id):
    config = load_config()
    if str(channel_id) in config["channels"]:
        return config["channels"][str(channel_id)]["interval_minutes"]
    return 0