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
    """Create a video with PNG overlay while maintaining PNG's aspect ratio"""
    
    # Get dimensions
    video_info = get_video_info(input_video)
    image_info = get_image_dimensions(overlay_image)
    
    # Calculate scaling factors to fit video to image
    scale_w = image_info['width'] / video_info['width']
    scale_h = image_info['height'] / video_info['height']
    
    # Use the larger scaling factor to ensure image fits
    scale_factor = max(scale_w, scale_h)
    
    # Calculate new video dimensions
    new_width = int(video_info['width'] * scale_factor)
    new_height = int(video_info['height'] * scale_factor)
    
    # Calculate padding to center the video
    pad_x = max(0, (image_info['width'] - new_width) // 2)
    pad_y = max(0, (image_info['height'] - new_height) // 2)
    
    cmd = [
        'ffmpeg', '-y',
        '-i', input_video,
        '-i', overlay_image,
        '-filter_complex',
        f'[0:v]scale={new_width}:{new_height}[scaled];'
        f'[scaled]pad={image_info["width"]}:{image_info["height"]}:{pad_x}:{pad_y}[padded];'
        '[padded][1:v]overlay=0:0',
        '-c:v', 'libx264',
        '-c:a', 'copy',
        '-y',  # Overwrite output file if it exists
        output_video
    ]
    
    subprocess.run(cmd)