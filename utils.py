
from telegram import Update
from telegram.ext import ContextTypes

from logger import logger
from config import SUPPORT_USERNAME
        
def get_is_message_mentions_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    bot_username = context.bot.username
    message_mentions_bot = False
    
    # Check message text or caption for bot mention
    message_text = update.message.text or update.message.caption or ""
    
    # Check text mentions in message or caption
    entities = update.message.entities or update.message.caption_entities or []
    for entity in entities:
        if entity.type == 'mention':
            mentioned_username = message_text[entity.offset:entity.offset + entity.length]
            if mentioned_username == f"@{bot_username}":
                message_mentions_bot = True
                break
    
    # Check if bot was replied to
    if update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id:
        message_mentions_bot = True
        
    return message_mentions_bot


async def send_video_response(update: Update, output_path, is_group_chat):
    """
    Send video response and optional success message
    """
    with open(output_path, 'rb') as video:
        await update.message.reply_video(video)
        # Only send success message in private chats
        if not is_group_chat:
            await update.message.reply_text("That's it! Download the video, share it or use a profile pic\n\nShow the 🟥🟩 to the world!")
    
    logger.info(f"Successfully processed video for user {update.effective_user.id}")


async def handle_processing_error(update, user_id, error):
    """
    Handle and log processing errors
    """
    logger.error(f"Error processing video for user {user_id}: {str(error)}")
    # Send error message in both private and group chats
    await update.message.reply_text(
        f"❌ Sorry, something went wrong. Please try again or contact {SUPPORT_USERNAME} for support.",
        parse_mode="markdown"
    )

async def send_usage_instructions(update):
    """
    Send usage instructions for the bot
    """
    await update.message.reply_text(
        "📸 Please send a PNG image as a file or photo!\n\n"
        "How to send:\n"
        "1. Choose a PNG image with a person/object\n"
        "2. Send as a file (📎) or direct photo\n"
        "3. I'll remove the background and create a video!"
    )