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
    
    # Determine the appropriate scaling approach
    if scale_w > scale_h:
        # Fit to width
        new_width = image_info['width']
        new_height = int(video_info['height'] * scale_w)
    else:
        # Fit to height
        new_height = image_info['height']
        new_width = int(video_info['width'] * scale_h)
    
    # Ensure dimensions are even (required by some codecs)
    new_width = (new_width + 1) & ~1
    new_height = (new_height + 1) & ~1
    
    # Calculate padding
    pad_width = max(new_width, image_info['width'])
    pad_height = max(new_height, image_info['height'])
    pad_x = (pad_width - new_width) // 2
    pad_y = (pad_height - new_height) // 2
    
    cmd = [
        'ffmpeg', '-y',
        '-i', input_video,
        '-i', overlay_image,
        '-filter_complex',
        f'[0:v]scale={new_width}:{new_height}[scaled];'
        f'[scaled]pad={pad_width}:{pad_height}:{pad_x}:{pad_y}[padded];'
        '[padded][1:v]overlay=0:0',
        '-c:v', 'libx264',
        '-c:a', 'copy',
        '-y',
        output_video
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
    except Exception as e:
        print(f"Error during video processing: {str(e)}")
        raise
