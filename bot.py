from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import os
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from merge import create_overlay_video
from logger import logger

# Load environment variables
load_dotenv()

# Environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
SOLANA_ADDRESS = os.getenv('SOLANA_ADDRESS')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
SUPPORT_USERNAME = os.getenv('SUPPORT_USERNAME')
MEMECOIN_CHAT = os.getenv('MEMECOIN_CHAT')
BACKGROUND_VIDEO_PATH = os.getenv('BACKGROUND_VIDEO_PATH')

# States
WAITING_FOR_PNG = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"User {update.effective_user.id} started the bot")
    await update.message.reply_text(
        "🎥 Welcome to Background Video Generator Bot!\n\n"
        "I can help you create a video with your PNG image overlaid on our special theme background.\n\n"
        "Simply send me your PNG image with transparent background, and I'll generate the video for you.\n\n"
        "Type /help for more information."
    )
    return WAITING_FOR_PNG

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"User {update.effective_user.id} requested help")
    await update.message.reply_text(
        "📖 Need help?\n\n"
        f"• For technical support, contact {SUPPORT_USERNAME} in {MEMECOIN_CHAT} or DM\n"
        f"• Need help with PNG preparation? You can use Photoshop, online services, or contact {SUPPORT_USERNAME}\n\n"
        "🔗 Contract Address:\n"
        f"{CONTRACT_ADDRESS}\n\n"
        "💰 Support the development:\n"
        f"• Solana address: `{SOLANA_ADDRESS}`\n"
        f"• For other donation methods, please DM {SUPPORT_USERNAME}\n\n"
        "Web service coming soon! Your donations will help with development, domain, and hosting costs."
    )

def send_usage_instructions(update: Update):
    return update.message.reply_text(
        "ℹ️ How to use this bot:\n\n"
        "1. Send a PNG file with transparent background\n"
        "2. Make sure to send it as a file, not as a photo to preserve transparency\n"
        "3. Wait for the bot to process your image\n\n"
        f"Need help? Contact {SUPPORT_USERNAME}"
    )

async def handle_png(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Handle PNG file
    if update.message.document and update.message.document.file_name.lower().endswith('.png'):
        logger.info(f"User {user_id} sent a PNG file")
        # Download the file
        file = await context.bot.get_file(update.message.document.file_id)
        input_path = f"temp/temp_{user_id}.png"
        output_path = f"output/output_{user_id}.mp4"
        await file.download_to_drive(input_path)

        await update.message.reply_text("🎬 Processing your video... Please wait.")

        try:
            # Your video generation function here
            create_overlay_video(BACKGROUND_VIDEO_PATH, input_path, output_path)

            # Send the generated video
            with open(output_path, 'rb') as video:
                await update.message.reply_video(video)
            
            logger.info(f"Successfully processed video for user {user_id}")
            
            # Cleanup
            os.remove(input_path)
            os.remove(output_path)

        except Exception as e:
            logger.error(f"Error processing video for user {user_id}: {str(e)}")
            await update.message.reply_text(
                f"❌ Sorry, something went wrong. Please try again or contact {SUPPORT_USERNAME} for support."
            )

    # Handle photo (PNG sent as image)
    elif update.message.photo:
        logger.info(f"User {user_id} sent a photo instead of file")
        await update.message.reply_text(
            "⚠️ Please send your PNG image as a file, not as a photo!\n\n"
            "This is important because sending as a photo will compress the image "
            "and remove transparency.\n\n"
            "How to send as file:\n"
            "1. Click the file attachment icon (📎)\n"
            "2. Select 'File'\n"
            "3. Choose your PNG image\n"
            "4. Send it to the bot without compression"
        )
    
    # Handle all other incorrect messages
    else:
        logger.info(f"User {user_id} sent an invalid message type")
        await send_usage_instructions(update)

    return WAITING_FOR_PNG

def main():
    # Create required directories
    os.makedirs('temp', exist_ok=True)
    os.makedirs('output', exist_ok=True)

    logger.info("Starting bot...")
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING_FOR_PNG: [
                MessageHandler(filters.Document.ALL | filters.PHOTO | filters.TEXT, handle_png)
            ]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('help', help))

    logger.info("Bot started successfully")
    application.run_polling()

if __name__ == '__main__':
    main()