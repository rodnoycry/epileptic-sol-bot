from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import os
from dotenv import load_dotenv
from merge import create_overlay_video

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
    await update.message.reply_text(
        "🎥 Welcome to Background Video Generator Bot!\n\n"
        "I can help you create a video with your PNG image overlaid on our special theme background.\n\n"
        "Simply send me your PNG image with transparent background, and I'll generate the video for you.\n\n"
        "Type /help for more information."
    )
    return WAITING_FOR_PNG

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Need help?\n\n"
        f"• For technical support, contact {SUPPORT_USERNAME} in {MEMECOIN_CHAT} or DM\n"
        f"• Need help with PNG preparation? You can use Photoshop, online services, or contact {SUPPORT_USERNAME}\n\n"
        "🔗 Contract Address:\n"
        f"{CONTRACT_ADDRESS}\n\n"
        "💰 Support the development:\n"
        f"• Solana address: {SOLANA_ADDRESS}\n"
        f"• For other donation methods, please DM {SUPPORT_USERNAME}\n\n"
        "Web service coming soon! Your donations will help with development, domain, and hosting costs."
    )

async def handle_png(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document or not update.message.document.file_name.lower().endswith('.png'):
        await update.message.reply_text(
            "❌ Please send a PNG file with transparent background.\n\n"
            "Need help creating one? You can:\n"
            "• Use Photoshop\n"
            "• Use online PNG background removal services\n"
            f"• Contact {SUPPORT_USERNAME} for assistance"
        )
        return WAITING_FOR_PNG

    # Download the file
    file = await context.bot.get_file(update.message.document.file_id)
    input_path = f"temp/temp_{update.message.from_user.id}.png"
    output_path = f"output/output_{update.message.from_user.id}.mp4"
    await file.download_to_drive(input_path)

    await update.message.reply_text("🎬 Processing your video... Please wait.")

    try:
        # Your video generation function here
        create_overlay_video(BACKGROUND_VIDEO_PATH, input_path, output_path)

        # Send the generated video
        with open(output_path, 'rb') as video:
            await update.message.reply_video(video)
        
        # Cleanup
        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        print(e)
        await update.message.reply_text(f"❌ Sorry, something went wrong. Please try again or contact {SUPPORT_USERNAME} for support.")

    return WAITING_FOR_PNG

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING_FOR_PNG: [MessageHandler(filters.Document.ALL, handle_png)]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('help', help))

    application.run_polling()

if __name__ == '__main__':
    main()