import json
import os
from datetime import datetime

DB_FILE = "scheduled_posts.json"

def initialize_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump({"last_post_time": {}, "posts": {}}, f, indent=4)

def load_db():
    initialize_db()
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

def update_last_post_time(channel_id, timestamp=None):
    db = load_db()
    if timestamp is None:
        timestamp = datetime.now().timestamp()
    db["last_post_time"][str(channel_id)] = timestamp
    save_db(db)

def get_last_post_time(channel_id):
    db = load_db()
    return db["last_post_time"].get(str(channel_id), 0)

def store_post(channel_id, post_index, post_data):
    db = load_db()
    if str(channel_id) not in db["posts"]:
        db["posts"][str(channel_id)] = {}
    db["posts"][str(channel_id)][str(post_index)] = post_data
    save_db(db)

def get_post(channel_id, post_index):
    db = load_db()
    return db["posts"].get(str(channel_id), {}).get(str(post_index))

def delete_post(channel_id, post_index):
    db = load_db()
    if str(channel_id) in db["posts"] and str(post_index) in db["posts"][str(channel_id)]:
        del db["posts"][str(channel_id)][str(post_index)]
        save_db(db)
        return True
    return False

def get_all_channel_posts(channel_id):
    db = load_db()
    return db["posts"].get(str(channel_id), {}) 