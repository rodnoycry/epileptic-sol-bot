import subprocess
import cv2

def create_overlay_video_from_chromakey(background_video_path: str, overlay_video_path: str, output_video_path: str):
    """
    Create a video by overlaying a video with green screen over another video.
    The green screen will be made transparent to show the background video.
    The output video will have the same dimensions as the overlay video (adjusted to even numbers).
    The background video will loop to match the duration of the overlay video.
    
    Args:
        background_video_path (str): Path to the background video file
        overlay_video_path (str): Path to the video with green screen
        output_video_path (str): Path where the output video will be saved
    """
    try:
        # Get overlay video dimensions and duration
        cap = cv2.VideoCapture(overlay_video_path)
        overlay_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        overlay_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        overlay_duration = float(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        # Ensure dimensions are even
        overlay_width = overlay_width + (overlay_width % 2)
        overlay_height = overlay_height + (overlay_height % 2)

        # Construct the FFmpeg command
        command = [
            'ffmpeg',
            '-stream_loop', '-1',  # Loop the background video indefinitely
            '-i', background_video_path,  # Background video
            '-i', overlay_video_path,  # Overlay video with green screen
            '-filter_complex',
            f'''
            [0:v]scale={overlay_width}:{overlay_height}:force_original_aspect_ratio=increase,
            crop={overlay_width}:{overlay_height},
            setsar=1[bg];
            [1:v]colorkey=color=0x00ff00:similarity=0.3:blend=0.2[ckout];
            [bg][ckout]overlay=0:0:format=auto,
            scale={overlay_width}:{overlay_height},
            format=yuv420p
            ''',
            '-c:v', 'libx264',  # Use H.264 codec
            '-preset', 'medium',  # Encoding preset
            '-crf', '23',  # Quality setting
            '-t', str(overlay_duration),  # Set output duration to match overlay video
            '-y',  # Overwrite output file if it exists
            output_video_path
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

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise