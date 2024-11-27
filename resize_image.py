import math
from PIL import Image

def resize_image_if_needed(image_path, max_pixels=1024*1024):  # 1 megapixel default
    """
    Resize image if its total pixel count exceeds the maximum,
    maintaining aspect ratio and treating all aspect ratios fairly.
    Returns True if image was resized, False otherwise.
    """
    with Image.open(image_path) as img:
        original_width, original_height = img.size
        current_pixels = original_width * original_height
        
        # Check if resizing is needed
        if current_pixels <= max_pixels:
            return False
            
        # Calculate scaling factor based on area
        scale_factor = math.sqrt(max_pixels / current_pixels)
        
        # Calculate new dimensions
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
            
        # Resize image
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save with original format and transparency if present
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            resized_img.save(image_path, format='PNG')
        else:
            resized_img.save(image_path, format='JPEG', quality=95)
            
        return True
