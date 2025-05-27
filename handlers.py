import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import config
import db
import json

logger = logging.getLogger(__name__)

user_states = {}

def start_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    
    if user_id not in config.ADMIN_IDS:
        update.message.reply_text("Вы не имеете доступа к этому боту.")
        return
    
    user_states[user_id] = {"state": "main_menu"}
    
    show_channels_menu(update, context)

def show_channels_menu(update: Update, context: CallbackContext):
    channels = config.get_channels()
    
    keyboard = []
    for channel_id, channel_data in channels.items():
        keyboard.append([InlineKeyboardButton(
            channel_data["name"], 
            callback_data=f"channel_{channel_id}"
        )])
    
    keyboard.append([InlineKeyboardButton("➕ Добавить канал", callback_data="add_channel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        update.callback_query.message.edit_text(
            "Выберите канал:", 
            reply_markup=reply_markup
        )
    else:
        update.message.reply_text(
            "Выберите канал:", 
            reply_markup=reply_markup
        )

def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id not in config.ADMIN_IDS:
        query.answer("Вы не имеете доступа к этому боту.")
        return
    
    query.answer()
    
    callback_data = query.data

    if user_id not in user_states:
        user_states[user_id] = {"state": "main_menu"}
    
    if callback_data.startswith("channel_"):
        channel_id = callback_data.replace("channel_", "")
        user_states[user_id]["channel_id"] = channel_id
        user_states[user_id]["state"] = "channel_menu"
        show_channel_menu(update, context)
    
    elif callback_data == "add_channel":
        user_states[user_id]["state"] = "add_channel_name"
        query.message.edit_text(
            "Отправьте название канала:"
        )
    
    elif callback_data == "send_posts":
        user_states[user_id]["state"] = "send_post"
        query.message.edit_text(
            "Отправьте сообщение для отложенной публикации (текст, фото, видео, GIF или их комбинацию).\n\n"
            "Или вернитесь в меню канала:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_channel")]
            ])
        )
    
    elif callback_data == "view_posts":
        user_states[user_id]["state"] = "view_posts"
        channel_id = user_states[user_id]["channel_id"]
        show_posts_list(update, context, channel_id)
    
    elif callback_data == "back_to_channel":
        user_states[user_id]["state"] = "channel_menu"
        show_channel_menu(update, context)
    
    elif callback_data == "back_to_channels":
        user_states[user_id]["state"] = "main_menu"
        if "channel_id" in user_states[user_id]:
            del user_states[user_id]["channel_id"]
        show_channels_menu(update, context)
    
    elif callback_data.startswith("delete_post_"):
        parts = callback_data.split("_")
        post_index = int(parts[2])
        channel_id = user_states[user_id]["channel_id"]
        
        config.remove_post_from_queue(channel_id, post_index)
        
        show_posts_list(update, context, channel_id)
    
    elif callback_data.startswith("page_"):
        page = int(callback_data.split("_")[1])
        channel_id = user_states[user_id]["channel_id"]
        show_posts_list(update, context, channel_id, page)

def show_channel_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    channel_id = user_states[user_id]["channel_id"]
    
    channels = config.get_channels()
    channel_name = channels[channel_id]["name"]
    
    keyboard = [
        [InlineKeyboardButton("📤 Отправить посты", callback_data="send_posts")],
        [InlineKeyboardButton("👁 Просмотреть/удалить посты", callback_data="view_posts")],
        [InlineKeyboardButton("⬅️ Назад к списку каналов", callback_data="back_to_channels")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.message.edit_text(
        f"Канал: {channel_name}\n"
        f"Интервал: {channels[channel_id]['interval_minutes']} минут\n\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )

def show_posts_list(update: Update, context: CallbackContext, channel_id, page=0):
    posts = config.get_channel_queue(channel_id)
    
    if not posts:
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_channel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.callback_query.message.edit_text(
            "Нет запланированных постов для этого канала.",
            reply_markup=reply_markup
        )
        return
    
    posts_per_page = 5
    total_pages = (len(posts) - 1) // posts_per_page + 1
    start_idx = page * posts_per_page
    end_idx = min(start_idx + posts_per_page, len(posts))
    
    text = "Запланированные посты:\n\n"
    
    for i in range(start_idx, end_idx):
        post = posts[i]
        post_type = post["type"]
        
        if post_type == "text":
            content = post["content"][:50] + "..." if len(post["content"]) > 50 else post["content"]
            text += f"{i+1}. Текст: {content}\n"
        elif post_type == "photo":
            caption = post.get("caption", "")[:30] + "..." if len(post.get("caption", "")) > 30 else post.get("caption", "")
            text += f"{i+1}. Фото" + (f": {caption}" if caption else "") + "\n"
        elif post_type == "video":
            caption = post.get("caption", "")[:30] + "..." if len(post.get("caption", "")) > 30 else post.get("caption", "")
            text += f"{i+1}. Видео" + (f": {caption}" if caption else "") + "\n"
        elif post_type == "animation":
            caption = post.get("caption", "")[:30] + "..." if len(post.get("caption", "")) > 30 else post.get("caption", "")
            text += f"{i+1}. GIF" + (f": {caption}" if caption else "") + "\n"
        elif post_type == "media_group":
            text += f"{i+1}. Группа медиа ({len(post['media'])} файлов)\n"
    
    keyboard = []
    pagination_row = []
    
    if page > 0:
        pagination_row.append(InlineKeyboardButton("⬅️", callback_data=f"page_{page-1}"))
    
    if page < total_pages - 1:
        pagination_row.append(InlineKeyboardButton("➡️", callback_data=f"page_{page+1}"))
    
    if pagination_row:
        keyboard.append(pagination_row)
    
    for i in range(start_idx, end_idx):
        keyboard.append([InlineKeyboardButton(f"❌ Удалить пост {i+1}", callback_data=f"delete_post_{i}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_channel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.callback_query.message.edit_text(
        text,
        reply_markup=reply_markup
    )

def message_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    
    if user_id not in config.ADMIN_IDS:
        return
    
    if user_id not in user_states:
        user_states[user_id] = {"state": "main_menu"}
        show_channels_menu(update, context)
        return
    
    state = user_states[user_id]["state"]
    
    if state == "add_channel_name":
        channel_name = update.message.text.strip()
        user_states[user_id]["channel_name"] = channel_name
        user_states[user_id]["state"] = "add_channel_id"
        
        update.message.reply_text(
            "Отправьте ID канала (например, -100123456789):"
        )
    
    elif state == "add_channel_id":
        try:
            channel_id = int(update.message.text.strip())
            user_states[user_id]["channel_id"] = channel_id
            user_states[user_id]["state"] = "add_channel_interval"
            
            update.message.reply_text(
                "Отправьте интервал публикации в минутах:"
            )
        except ValueError:
            update.message.reply_text(
                "Ошибка! Отправьте корректный ID канала (число):"
            )
    
    elif state == "add_channel_interval":
        try:
            interval = int(update.message.text.strip())
            
            if interval <= 0:
                update.message.reply_text(
                    "Интервал должен быть положительным числом. Попробуйте еще раз:"
                )
                return
            
            channel_id = user_states[user_id]["channel_id"]
            channel_name = user_states[user_id]["channel_name"]
            
            config.add_channel(channel_id, channel_name, interval)
            
            user_states[user_id]["state"] = "main_menu"
            
            keyboard = []
            channels = config.get_channels()
            
            for ch_id, ch_data in channels.items():
                keyboard.append([InlineKeyboardButton(
                    ch_data["name"], 
                    callback_data=f"channel_{ch_id}"
                )])
            
            keyboard.append([InlineKeyboardButton("➕ Добавить канал", callback_data="add_channel")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            update.message.reply_text(
                f"Канал '{channel_name}' добавлен с интервалом {interval} минут!",
                reply_markup=reply_markup
            )
        except ValueError:
            update.message.reply_text(
                "Ошибка! Отправьте корректный интервал (число минут):"
            )
    
    elif state == "send_post":
        channel_id = user_states[user_id]["channel_id"]
        
        post_data = None
        
        if update.message.text:
            post_data = {
                "type": "text",
                "content": update.message.text,
                "parse_mode": "HTML"
            }
        elif update.message.photo:
            photo = update.message.photo[-1]
            post_data = {
                "type": "photo",
                "file_id": photo.file_id,
                "caption": update.message.caption or "",
                "parse_mode": "HTML"
            }
        elif update.message.video:
            post_data = {
                "type": "video",
                "file_id": update.message.video.file_id,
                "caption": update.message.caption or "",
                "parse_mode": "HTML"
            }
        elif update.message.animation:
            post_data = {
                "type": "animation",
                "file_id": update.message.animation.file_id,
                "caption": update.message.caption or "",
                "parse_mode": "HTML"
            }
        elif update.message.document:
            post_data = {
                "type": "document",
                "file_id": update.message.document.file_id,
                "caption": update.message.caption or "",
                "parse_mode": "HTML"
            }
        elif update.message.media_group_id:

            
            if "media_groups" not in context.bot_data:
                context.bot_data["media_groups"] = {}
            
            media_group_id = update.message.media_group_id
            
            if media_group_id not in context.bot_data["media_groups"]:
                context.bot_data["media_groups"][media_group_id] = {
                    "items": [],
                    "user_id": user_id,
                    "channel_id": channel_id,
                    "expires": context.bot.get_updates()[-1].update_id + 10
                }
            
            media_group = context.bot_data["media_groups"][media_group_id]
            
            media_item = None
            
            if update.message.photo:
                media_item = {
                    "type": "photo",
                    "media": update.message.photo[-1].file_id,
                    "caption": update.message.caption or "",
                    "parse_mode": "HTML"
                }
            elif update.message.video:
                media_item = {
                    "type": "video",
                    "media": update.message.video.file_id,
                    "caption": update.message.caption or "",
                    "parse_mode": "HTML"
                }
            
            if media_item and media_item not in media_group["items"]:
                media_group["items"].append(media_item)
            
            return
        
        if post_data:
            position = config.add_post_to_queue(channel_id, post_data)
            
            keyboard = [
                [InlineKeyboardButton("📤 Отправить еще пост", callback_data="send_posts")],
                [InlineKeyboardButton("⬅️ Назад к меню канала", callback_data="back_to_channel")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            update.message.reply_text(
                f"Пост добавлен в очередь на позицию {position}!\n"
                "Отправьте следующее сообщение или выберите действие:",
                reply_markup=reply_markup
            )

def process_pending_media_groups(context: CallbackContext):
    if "media_groups" not in context.bot_data:
        return
    
    current_update_id = context.bot.get_updates()[-1].update_id if context.bot.get_updates() else 0
    
    for media_group_id, group_data in list(context.bot_data["media_groups"].items()):
        if current_update_id > group_data["expires"]:
            media = []
            for item in group_data["items"]:
                if item["type"] == "photo":
                    media.append({
                        "type": "photo",
                        "media": item["media"],
                        "caption": item.get("caption", ""),
                        "parse_mode": item.get("parse_mode", "HTML")
                    })
                elif item["type"] == "video":
                    media.append({
                        "type": "video",
                        "media": item["media"],
                        "caption": item.get("caption", ""),
                        "parse_mode": item.get("parse_mode", "HTML")
                    })
            
            if media:
                post_data = {
                    "type": "media_group",
                    "media": media
                }
                
                position = config.add_post_to_queue(group_data["channel_id"], post_data)
                
                keyboard = [
                    [InlineKeyboardButton("📤 Отправить еще пост", callback_data="send_posts")],
                    [InlineKeyboardButton("⬅️ Назад к меню канала", callback_data="back_to_channel")]
                ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                context.bot.send_message(
                    chat_id=group_data["user_id"],
                    text=f"Группа из {len(media)} медиафайлов добавлена в очередь на позицию {position}!\n"
                    "Отправьте следующее сообщение или выберите действие:",
                    reply_markup=reply_markup
                )
            
            del context.bot_data["media_groups"][media_group_id]