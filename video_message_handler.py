import os
from telegram import Update
from telegram.ext import ContextTypes

# Assuming these are defined elsewhere in your code
from logger import logger

async def handle_message_with_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message
        chat_id = message.chat_id
        
        # Create temporary directory for this processing
        temp_dir = os.path.join('temp', str(chat_id))
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate temporary file paths
        temp_input_path = os.path.join(temp_dir, f'input_video_{message.message_id}')
        output_path = os.path.join('output', f'processed_video_{message.message_id}.mp4')
        
        # Handle different types of video messages
        if message.video:
            # Case 1: Regular video message
            video_file = await message.video.get_file()
            await video_file.download_to_drive(f"{temp_input_path}.mp4")
            await process_mp4(f"{temp_input_path}.mp4", overlay_image_path, output_path)
            
        elif message.document:
            # Case 2: Video sent as file
            file_extension = os.path.splitext(message.document.file_name)[1].lower()
            video_file = await message.document.get_file()
            
            if file_extension == '.mp4':
                await video_file.download_to_drive(f"{temp_input_path}.mp4")
                await process_mp4(f"{temp_input_path}.mp4", overlay_image_path, output_path)
            elif file_extension == '.mov':
                await video_file.download_to_drive(f"{temp_input_path}.mov")
                await process_mov(f"{temp_input_path}.mov", overlay_image_path, output_path)
            elif file_extension == '.webm':
                await video_file.download_to_drive(f"{temp_input_path}.webm")
                await process_webm(f"{temp_input_path}.webm", overlay_image_path, output_path)
            else:
                await message.reply_text("Unsupported file format. Please send MP4, MOV, or WEBM files.")
                return
                
        elif message.sticker and message.sticker.is_animated:
            # Case 3: Animated sticker
            sticker_file = await message.sticker.get_file()
            file_extension = os.path.splitext(sticker_file.file_path)[1].lower()
            
            if file_extension == '.mp4':
                await sticker_file.download_to_drive(f"{temp_input_path}.mp4")
                await process_mp4(f"{temp_input_path}.mp4", overlay_image_path, output_path)
            elif file_extension == '.webm':
                await sticker_file.download_to_drive(f"{temp_input_path}.webm")
                await process_webm(f"{temp_input_path}.webm", overlay_image_path, output_path)
            else:
                await message.reply_text("Unsupported sticker format.")
                return
                
        else:
            await message.reply_text("Please send a video, video file, or animated sticker.")
            return
            
        # Send the processed video back
        with open(output_path, 'rb') as video:
            await message.reply_video(video)
            
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        await message.reply_text("Sorry, there was an error processing your video.")
        
    finally:
        # Cleanup temporary files
        try:
            if os.path.exists(temp_dir):
                for file in os.listdir(temp_dir):
                    os.remove(os.path.join(temp_dir, file))
                os.rmdir(temp_dir)
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception as e:
            logger.error(f"Error cleaning up files: {str(e)}")