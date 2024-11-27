from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from logger import logger
from config import BOT_TOKEN, SOLANA_ADDRESS, CONTRACT_ADDRESS, SUPPORT_USERNAME, MEMECOIN_CHAT, BACKGROUND_VIDEO_PATH
from message_handler import handle_message

# States
WAITING_FOR_PNG = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"User {update.effective_user.id} started the bot")
    escaped_underscore = "\\_"
    await update.message.reply_animation(
        animation=open(os.path.abspath('messages/start.gif'), 'rb'),
        caption=
            "Welcome to 🟥🟩 Video Generator\n\n"
            "This bot will create a video with your PNG image overlaid on 🟥🟩 background.\n\n"
            "Send your PNG image with transparent background, and this bot will generate the video for you.\n"
            f"{escaped_underscore * 31}\n\n"
            "New features coming soon!\n"
            "- Video overlaying\n"
            "- Automatic background removal\n"
            "- Website version\n\n"
            "If you want to see these feature as soon as possible, please consider donating some SOL to developer's wallet:\n"
            f"`{SOLANA_ADDRESS}`\n\n"
            "I do this stuff for the community, but I will really appreciate the support and you will speed up the development process \u2764\ufe0f",
        parse_mode="markdown"
    )
    return WAITING_FOR_PNG

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"User {update.effective_user.id} requested help")
    await update.message.reply_text(
        "📖 Need help?\n\n"
        f"• For technical support, contact {SUPPORT_USERNAME} in {MEMECOIN_CHAT} or DM\n"
        f"• Need help with PNG preparation? You can use Photoshop, online services, or contact {SUPPORT_USERNAME}\n\n"
        "🔗 Contract Address:\n"
        f"`{CONTRACT_ADDRESS}`\n\n"
        "💰 Support the development:\n"
        f"• Solana address: `{SOLANA_ADDRESS}`\n"
        f"• For other donation methods, please DM {SUPPORT_USERNAME}\n\n"
        "Web service and new features coming soon! Your donations will help with speeding up the development and will cover hosting costs",
        parse_mode="markdown"
    )

def send_usage_instructions(update: Update):
    return update.message.reply_text(
        "ℹ️ How to use this bot:\n\n"
        "1. Send a PNG file with transparent background\n"
        "2. Make sure to send it as a file, not as a photo to preserve transparency\n"
        "3. Wait for the bot to process your image\n\n"
        f"Need help? Contact {SUPPORT_USERNAME}",
        parse_mode="markdown"
    )

def main():
    # Create required directories
    os.makedirs('temp', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    
    private_or_mentioned_in_group_filter = (
        filters.ChatType.PRIVATE |
        (
            (filters.ChatType.GROUP | filters.ChatType.GROUPS | filters.ChatType.SUPERGROUP) & 
            (filters.Entity("mention") | filters.CaptionEntity("mention") | filters.REPLY)
        )
    )

    logger.info("Starting bot...")
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(MessageHandler(
        (filters.Document.ALL | filters.PHOTO | filters.TEXT | filters.Sticker.STATIC) & private_or_mentioned_in_group_filter,
        handle_message
    ))
    logger.info("Bot started successfully")
    application.run_polling()

if __name__ == '__main__':
    main()
