import os
import logging
from telegram import Update
from telegram.ext import ContextTypes
import rembg  # Add rembg import

# Assuming these are defined elsewhere in your code
from merge import create_overlay_video
from logger import logger
from config import BACKGROUND_VIDEO_PATH, SUPPORT_USERNAME

async def remove_background(input_path, output_path):
    """
    Remove background from an image using rembg.
    
    :param input_path: Path to the input image
    :param output_path: Path to save the background-removed image
    """
    with open(input_path, 'rb') as input_file:
        input_image = input_file.read()
    
    # Remove background
    output_image = rembg.remove(input_image)
    
    # Save the output image
    with open(output_path, 'wb') as output_file:
        output_file.write(output_image)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_group_chat = update.message.chat.type in ['group', 'supergroup']

    # Check if bot should respond in group chat
    if is_group_chat:
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

        # If bot wasn't mentioned in group chat, return
        if not message_mentions_bot:
            return

    # Handle PNG file (existing logic)
    if update.message.document and update.message.document.file_name.lower().endswith('.png'):
        logger.info(f"User {user_id} sent a PNG file")
        # Download the file
        file = await context.bot.get_file(update.message.document.file_id)
        input_path = os.path.abspath(f"temp/temp_{user_id}.png")
        output_path = os.path.abspath(f"output/output_{user_id}.mp4")
        background_video_path = os.path.abspath(BACKGROUND_VIDEO_PATH)
        await file.download_to_drive(input_path)

        # Process PNG file (same as before)
        try:
            create_overlay_video(background_video_path, input_path, output_path)
            await send_video_response(update, output_path, is_group_chat)
            
            # Cleanup
            os.remove(input_path)
            os.remove(output_path)

        except Exception as e:
            await handle_processing_error(update, user_id, e)

    # Handle photo (image sent directly)
    elif update.message.photo:
        logger.info(f"User {user_id} sent a photo")
        
        # Get the largest photo (highest resolution)
        photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
        
        # Paths for processing
        input_path = os.path.abspath(f"temp/temp_{user_id}.png")
        bg_removed_path = os.path.abspath(f"temp/bg_removed_{user_id}.png")
        output_path = os.path.abspath(f"output/output_{user_id}.mp4")

        try:
            # Download the original photo
            await photo_file.download_to_drive(input_path)

            # Remove background
            await remove_background(input_path, bg_removed_path)

            # Only send processing message in private chats
            if not is_group_chat:
                await update.message.reply_text("🎬 Processing your image... Please wait.")

            # Create video with background-removed image
            create_overlay_video(BACKGROUND_VIDEO_PATH, bg_removed_path, output_path)

            # Send the generated video
            await send_video_response(update, output_path, is_group_chat)
            
            # Cleanup
            os.remove(input_path)
            os.remove(bg_removed_path)
            os.remove(output_path)

        except Exception as e:
            await handle_processing_error(update, user_id, e)
    
    # Handle all other incorrect messages
    else:
        logger.info(f"User {user_id} sent an invalid message type")
        # Send usage instructions in both private and group chats
        await send_usage_instructions(update)

async def send_video_response(update, output_path, is_group_chat):
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