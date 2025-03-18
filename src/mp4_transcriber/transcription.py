"""
Speech-to-text transcription functionality for MP4 Transcriber.
"""

import time
from datetime import timedelta
import torch
import whisper


def format_timestamp(seconds):
    """
    Convert seconds to HH:MM:SS format.
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted time string
    """
    return str(timedelta(seconds=seconds)).split('.')[0]


def transcribe_audio(audio_path, model_size="base", verbose=False):
    """
    Transcribe audio using Whisper.
    
    Args:
        audio_path (str): Path to the audio file
        model_size (str): Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
        verbose (bool): Whether to show detailed output
        
    Returns:
        dict: Transcription results from Whisper
    """
    print(f"Loading Whisper model '{model_size}'...")
    
    # Check if CUDA is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if verbose:
        print(f"Using device: {device}")
    
    # Load the Whisper model
    model = whisper.load_model(model_size, device=device)
    
    print("Transcribing audio...")
    start_time = time.time()
    
    # Transcribe the audio file
    result = model.transcribe(
        audio_path, 
        fp16=(device == "cuda"),
        verbose=verbose
    )
    
    elapsed = time.time() - start_time
    print(f"Transcription completed in {elapsed:.2f} seconds")
    
    return result


def create_transcript_with_timestamps(segments):
    """
    Create transcript with timestamps from segments.
    
    Args:
        segments (list): List of segment dictionaries from Whisper
        
    Returns:
        str: Formatted transcript with timestamps
    """
    lines = []
    for segment in segments:
        start_time = format_timestamp(segment['start'])
        end_time = format_timestamp(segment['end'])
        text = segment['text'].strip()
        lines.append(f"[{start_time} - {end_time}] {text}")
    
    return '\n'.join(lines)
