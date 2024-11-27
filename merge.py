import subprocess
from PIL import Image

def create_overlay_video(input_video: str, overlay_image: str, output_video: str):
    """
    Create a video with an overlay PNG image where transparency shows the video background.
    The output video will have the same dimensions as the PNG image (adjusted to even numbers).
    
    Args:
        input_video (str): Path to the input video file
        overlay_image (str): Path to the PNG image with transparency
        output_video (str): Path where the output video will be saved
    """
    try:
        # Get overlay image dimensions
        with Image.open(overlay_image) as img:
            overlay_width, overlay_height = img.size
            
        # Ensure dimensions are even
        overlay_width = overlay_width + (overlay_width % 2)
        overlay_height = overlay_height + (overlay_height % 2)

        # Construct the FFmpeg command
        command = [
            'ffmpeg',
            '-i', input_video,  # Input video
            '-i', overlay_image,  # Overlay image
            '-filter_complex',
            f'''
            [0:v]scale={overlay_width}:{overlay_height}:force_original_aspect_ratio=increase,
            crop={overlay_width}:{overlay_height},
            setsar=1[bg];
            [bg][1:v]overlay=0:0:format=auto,
            scale={overlay_width}:{overlay_height},
            format=yuv420p
            ''',
            '-c:v', 'libx264',  # Use H.264 codec
            '-preset', 'medium',  # Encoding preset
            '-crf', '23',  # Quality setting
            '-y',  # Overwrite output file if it exists
            output_video
        ]

        # Execute the FFmpeg command
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for the process to complete and get output
        _stdout, stderr = process.communicate()

        # Check if the process was successful
        if process.returncode != 0:
            raise Exception(f"FFmpeg error: {stderr.decode()}")

        print(f"Successfully created overlay video: {output_video}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

