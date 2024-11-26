import subprocess
import json

def get_video_info(video_path):
    """Get video dimensions and duration using ffprobe"""
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        video_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    
    # Find video stream
    video_stream = next(s for s in data['streams'] if s['codec_type'] == 'video')
    
    return {
        'width': int(video_stream['width']),
        'height': int(video_stream['height']),
        'duration': float(data['format']['duration'])
    }

def get_image_dimensions(image_path):
    """Get PNG image dimensions using ffprobe"""
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_streams',
        image_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    
    return {
        'width': int(data['streams'][0]['width']),
        'height': int(data['streams'][0]['height'])
    }

def create_overlay_video(input_video, overlay_image, output_video):
    """
    Create a video with PNG overlay maintaining the overlay image's dimensions
    and replacing transparency with video
    """
    
    # Get dimensions
    video_info = get_video_info(input_video)
    image_info = get_image_dimensions(overlay_image)
    
    # Resize video to match overlay image dimensions
    cmd = [
        'ffmpeg', '-y',
        '-i', input_video,
        '-i', overlay_image,
        '-filter_complex', 
        # Resize video to match overlay image, maintaining aspect ratio
        f'[0:v]scale={image_info["width"]}:{image_info["height"]}:force_original_aspect_ratio=decrease,pad={image_info["width"]}:{image_info["height"]}:(ow-iw)/2:(oh-ih)/2[bg];'
        # Overlay the PNG on top of the resized video
        '[bg][1:v]overlay=0:0:enable=\'between(t,0,999999)\'',
        '-c:v', 'libx264',
        '-c:a', 'copy',
        '-pix_fmt', 'yuv420p',
        output_video
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
        print(f"Overlay video created successfully: {output_video}")
    except Exception as e:
        print(f"Error during video processing: {str(e)}")
        raise