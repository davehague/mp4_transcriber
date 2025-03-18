"""
Audio extraction utilities for MP4 Transcriber.
"""

import os
import subprocess
import tempfile


def extract_audio(video_path, audio_path=None, verbose=False):
    """
    Extract audio from video file using ffmpeg.
    
    Args:
        video_path (str): Path to the video file
        audio_path (str, optional): Path to save the extracted audio
        verbose (bool): Whether to show detailed output
        
    Returns:
        str: Path to the extracted audio file, or None if extraction failed
    """
    if audio_path is None:
        # Create a temporary file if no output path is specified
        audio_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        audio_path = audio_file.name
        audio_file.close()
    
    # Command to extract audio
    cmd = [
        'ffmpeg', 
        '-i', video_path,
        '-y',  # Always overwrite existing files
        '-q:a', '0',
        '-map', 'a',
        '-vn', audio_path
    ]
    
    if not verbose:
        cmd.extend(['-loglevel', 'error'])
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Audio extracted successfully to {audio_path}")
        return audio_path
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e}")
        if os.path.exists(audio_path):
            os.unlink(audio_path)
        return None


def check_ffmpeg_installed():
    """
    Check if ffmpeg is installed and available in PATH.
    
    Returns:
        bool: True if ffmpeg is installed, False otherwise
    """
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
