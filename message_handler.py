import os
from telegram import Update
from telegram.ext import ContextTypes
import rembg
from PIL import Image
import time
import datetime

# Assuming these are defined elsewhere in your code
from merge import create_overlay_video
from logger import logger
from config import BACKGROUND_VIDEO_PATH, SUPPORT_USERNAME
from resize_image import resize_image_if_needed

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
    if is_group_chat and not get_is_message_mentions_bot(update, context):
        return
    
    transparent_image_path = None
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S_%f')

    # Handle image
    if update.message.photo:
        if not is_group_chat:
            await update.message.reply_text("🎬 Processing your image... Please wait.")
            
        logger.info(f"User {user_id} sent a photo")
        photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
        file_extension = photo_file.file_path.split('.')[-1]
        
        downloaded_image_path = os.path.abspath(f"temp/temp_{user_id}_{timestamp}.{file_extension}")
        image_with_removed_bg_path = os.path.abspath(f"temp/bg_removed_{user_id}_{timestamp}.{file_extension}")
        
        try:
            await photo_file.download_to_drive(downloaded_image_path)
            resize_image_if_needed(downloaded_image_path)
            await remove_background(downloaded_image_path, image_with_removed_bg_path)

        except Exception as e:
            await handle_processing_error(update, user_id, e)
            
        transparent_image_path = image_with_removed_bg_path

    # Handle file
    elif update.message.document and update.message.document.file_name.split('.')[-1].lower() in ["png", "jpg", "jpeg"]:
        if not is_group_chat:
            await update.message.reply_text("🎬 Processing your image... Please wait.")
            
        logger.info(f"User {user_id} sent a file")
        file_extension = update.message.document.file_name.split('.')[-1]
        
        downloaded_image_path = os.path.abspath(f"temp/temp_{user_id}_{timestamp}.{file_extension}")
        file = await context.bot.get_file(update.message.document.file_id)
        await file.download_to_drive(downloaded_image_path)
        resize_image_if_needed(downloaded_image_path)
        
        if file_extension.lower() == 'png' and png_has_transpare(downloaded_image_path):
            transparent_image_path = downloaded_image_path
        else:
            image_with_removed_bg_path = os.path.abspath(f"temp/bg_removed_{user_id}.png")
            
            try:
                await remove_background(downloaded_image_path, image_with_removed_bg_path)
            except Exception as e:
                await handle_processing_error(update, user_id, e)
                
            os.remove(downloaded_image_path)
            transparent_image_path = image_with_removed_bg_path
    
    # Handle sticker
    elif update.message.sticker:
        if not is_group_chat:
            await update.message.reply_text("🎬 Processing sticker... Please wait.")
            
        # Generate unique filenames
        temp_sticker = f"temp/sticker_{user_id}_{timestamp}.webp"
        temp_png = f"temp/sticker_{user_id}_{timestamp}.png"
        
        try:
            # Download sticker file
            sticker_file = await update.message.sticker.get_file()
            await sticker_file.download_to_drive(temp_sticker)
            
            # Convert WebP to PNG
            with Image.open(temp_sticker) as img:
                # If the image doesn't have transparency, add an alpha channel
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                img.save(temp_png, 'PNG')
                
        
            if png_has_transpare(temp_png):
                transparent_image_path = temp_png
            else:
                image_with_removed_bg_path = os.path.abspath(f"temp/bg_removed_{user_id}.png")
                
                try:
                    await remove_background(temp_png, image_with_removed_bg_path)
                except Exception as e:
                    await handle_processing_error(update, user_id, e)
            
                transparent_image_path = image_with_removed_bg_path
                os.remove(temp_png)
                    
            os.remove(temp_sticker)
                
        except Exception as e:
            await handle_processing_error(update, user_id, e)

    else:
        logger.info(f"User {user_id} sent an invalid message type")
        # Send usage instructions in both private and group chats
        await send_usage_instructions(update)
        return
        
    if not transparent_image_path:
        logger.info(f"User {user_id}: Unhandled case, 'transparent_image_path' is empty")
        # Send usage instructions in both private and group chats
        await send_usage_instructions(update)
        return
    
    # Process Image
    try:
        output_path = os.path.abspath(f"output/output_{user_id}_{timestamp}.mp4")
        background_video_path = os.path.abspath(BACKGROUND_VIDEO_PATH)
        create_overlay_video(background_video_path, transparent_image_path, output_path)
        await send_video_response(update, output_path, is_group_chat)
        
        # Cleanup
        os.remove(transparent_image_path)
        os.remove(output_path)

    except Exception as e:
        await handle_processing_error(update, user_id, e)
        return
    
        
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

def png_has_transpare(image_path):
    with Image.open(image_path) as img:
        if img.mode == "RGBA":
            extrema = img.getextrema()
            if extrema[3][0] < 255:  # Check if minimum alpha value is less than 255
                return True
    return False

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