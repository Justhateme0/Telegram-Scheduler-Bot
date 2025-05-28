import logging
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler, 
    MessageHandler, Filters
)
import config
import handlers
import scheduler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def error_handler(update, context):
    """Log errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater(config.BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", handlers.start_handler))
    
    dispatcher.add_handler(CallbackQueryHandler(handlers.callback_handler))
    
    dispatcher.add_handler(MessageHandler(
        Filters.text | Filters.photo | Filters.video | 
        Filters.animation | Filters.document, 
        handlers.message_handler
    ))
    
    # Register error handler
    dispatcher.add_error_handler(error_handler)
    
    updater.job_queue.run_repeating(handlers.process_pending_media_groups, interval=2, first=0)
    
    updater.start_polling()
    
    scheduler_thread = scheduler.start_scheduler(updater.bot)
    
    updater.idle()

if __name__ == '__main__':
    main()