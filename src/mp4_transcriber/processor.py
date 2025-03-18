"""
Video processing pipeline for MP4 Transcriber.
"""

import os
import json
from pathlib import Path

from mp4_transcriber.audio import extract_audio
from mp4_transcriber.transcription import transcribe_audio, create_transcript_with_timestamps
from mp4_transcriber.text_processing import clean_transcript


def process_video(video_path, output_path=None, model_size="base", with_timestamps=False, cleanup=True, verbose=False):
    """
    Process a video file to create a transcript.
    
    Args:
        video_path (str): Path to the video file
        output_path (str, optional): Path to save the transcript
        model_size (str): Whisper model size
        with_timestamps (bool): Whether to include timestamps
        cleanup (bool): Whether to remove temporary files
        verbose (bool): Whether to show detailed output
        
    Returns:
        str: Path to the created transcript, or None if processing failed
    """
    # Define output path if not provided
    if output_path is None:
        base_path = os.path.splitext(video_path)[0]
        output_path = f"{base_path}_transcript.txt"
    
    # Extract audio from video
    audio_path = extract_audio(video_path, verbose=verbose)
    if not audio_path:
        return None
    
    try:
        # Transcribe the audio
        result = transcribe_audio(audio_path, model_size, verbose)
        
        # Format the transcript
        try:
            if with_timestamps:
                transcript = create_transcript_with_timestamps(result['segments'])
            else:
                transcript = clean_transcript(result)
        except Exception as e:
            print(f"Warning: Error during transcript formatting: {e}")
            # Fallback to raw text in case of formatting error
            transcript = result.get('text', '')
            print("Using raw transcript text without formatting.")
                
            # Add a basic cleanup even if text processing failed
            transcript = transcript.strip()
            if transcript and transcript[0].islower():
                transcript = transcript[0].upper() + transcript[1:]
        
        # Write the transcript to the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(transcript)
        
        print(f"Transcript saved to {output_path}")
        
        # Optionally save the raw JSON result
        if verbose:
            json_path = f"{os.path.splitext(output_path)[0]}_raw.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            print(f"Raw transcription data saved to {json_path}")
        
        return output_path
    
    finally:
        # Clean up temporary audio file
        if cleanup and audio_path and os.path.exists(audio_path):
            os.unlink(audio_path)
            if verbose:
                print(f"Cleaned up temporary audio file: {audio_path}")


def batch_process(directory, output_dir=None, model_size="base", with_timestamps=False, verbose=False):
    """
    Process all MP4 files in a directory.
    
    Args:
        directory (str): Directory containing MP4 files
        output_dir (str, optional): Directory to save transcripts
        model_size (str): Whisper model size
        with_timestamps (bool): Whether to include timestamps
        verbose (bool): Whether to show detailed output
    """
    dir_path = Path(directory)
    if output_dir:
        out_path = Path(output_dir)
        os.makedirs(out_path, exist_ok=True)
    else:
        out_path = dir_path
    
    mp4_files = list(dir_path.glob('*.mp4'))
    print(f"Found {len(mp4_files)} MP4 files in {directory}")
    
    for video_file in mp4_files:
        output_file = out_path / f"{video_file.stem}_transcript.txt"
        print(f"Processing {video_file}...")
        process_video(
            str(video_file), 
            str(output_file), 
            model_size=model_size, 
            with_timestamps=with_timestamps,
            verbose=verbose
        )
