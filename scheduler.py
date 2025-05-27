import logging
import time
import threading
from datetime import datetime
import db
import config
from telegram import Bot, ParseMode
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

def schedule_posts_thread(bot: Bot):
    logger.info("Планировщик публикаций запущен")
    
    while True:
        try:
            channels = config.get_channels()
            
            for channel_id, channel_data in channels.items():
                interval_minutes = channel_data.get("interval_minutes", 60)
                last_post_time = db.get_last_post_time(channel_id)
                current_time = datetime.now().timestamp()
                
                if current_time - last_post_time >= interval_minutes * 60:
                    posts = config.get_channel_queue(channel_id)
                    
                    if posts:
                        post = posts[0]
                        
                        sent = send_post(bot, channel_id, post)
                        
                        if sent:
                            db.update_last_post_time(channel_id)
                            
                            config.remove_post_from_queue(channel_id, 0)
                            
                            logger.info(f"Опубликовано запланированное сообщение в канал {channel_id}")
            
            time.sleep(60)
        except Exception as e:
            logger.error(f"Ошибка в планировщике: {e}")
            time.sleep(60)

def start_scheduler(bot: Bot):
    thread = threading.Thread(target=schedule_posts_thread, args=(bot,))
    thread.daemon = True
    thread.start()
    return thread

def send_post(bot: Bot, channel_id, post):
    try:
        if post['type'] == 'text':
            bot.send_message(
                chat_id=channel_id, 
                text=post['content'],
                parse_mode=post.get('parse_mode', ParseMode.HTML)
            )
        elif post['type'] == 'photo':
            bot.send_photo(
                chat_id=channel_id,
                photo=post['file_id'],
                caption=post.get('caption', ''),
                parse_mode=post.get('parse_mode', ParseMode.HTML)
            )
        elif post['type'] == 'video':
            bot.send_video(
                chat_id=channel_id,
                video=post['file_id'],
                caption=post.get('caption', ''),
                parse_mode=post.get('parse_mode', ParseMode.HTML)
            )
        elif post['type'] == 'animation':
            bot.send_animation(
                chat_id=channel_id,
                animation=post['file_id'],
                caption=post.get('caption', ''),
                parse_mode=post.get('parse_mode', ParseMode.HTML)
            )
        elif post['type'] == 'document':
            bot.send_document(
                chat_id=channel_id,
                document=post['file_id'],
                caption=post.get('caption', ''),
                parse_mode=post.get('parse_mode', ParseMode.HTML)
            )
        elif post['type'] == 'media_group':
            from telegram import InputMediaPhoto, InputMediaVideo
            
            media = []
            for item in post['media']:
                if item['type'] == 'photo':
                    media.append(
                        InputMediaPhoto(
                            media=item['media'],
                            caption=item.get('caption', ''),
                            parse_mode=item.get('parse_mode', ParseMode.HTML)
                        )
                    )
                elif item['type'] == 'video':
                    media.append(
                        InputMediaVideo(
                            media=item['media'],
                            caption=item.get('caption', ''),
                            parse_mode=item.get('parse_mode', ParseMode.HTML)
                        )
                    )
            
            bot.send_media_group(
                chat_id=channel_id,
                media=media
            )
        return True
    except TelegramError as e:
        logger.error(f"Не удалось отправить сообщение в канал {channel_id}: {e}")
        return False 