"""
Command-line interface for MP4 Transcriber.
"""

import os
import argparse
import sys

from mp4_transcriber.audio import check_ffmpeg_installed
from mp4_transcriber.processor import process_video, batch_process


def parse_args():
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Convert MP4 files to text transcripts.")
    
    # Main arguments
    parser.add_argument('-i', '--input', help='Input MP4 file or directory')
    parser.add_argument('-o', '--output', help='Output transcript file or directory (optional)')
    parser.add_argument('-m', '--model', default='base', 
                        choices=['tiny', 'base', 'small', 'medium', 'large'],
                        help='Whisper model size (default: base)')
    
    # Optional flags
    parser.add_argument('-t', '--timestamps', action='store_true', 
                        help='Include timestamps in the transcript')
    parser.add_argument('-b', '--batch', action='store_true',
                        help='Process all MP4 files in the input directory')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--keep-audio', action='store_true',
                        help='Do not delete temporary audio files')
    
    return parser.parse_args()


def main():
    """
    Main entry point for the command-line interface.
    """
    args = parse_args()
    
    if not args.input:
        print("Error: Input path is required. Use -i or --input to specify.")
        return 1
    
    # Check if ffmpeg is installed
    if not check_ffmpeg_installed():
        print("Error: ffmpeg is not installed or not in PATH. Please install ffmpeg.")
        return 1
    
    # Check if input exists
    if not os.path.exists(args.input):
        print(f"Error: Input path '{args.input}' does not exist.")
        return 1
    
    # Process input
    try:
        if args.batch or os.path.isdir(args.input):
            batch_process(
                args.input, 
                args.output, 
                model_size=args.model, 
                with_timestamps=args.timestamps,
                verbose=args.verbose
            )
        else:
            process_video(
                args.input, 
                args.output, 
                model_size=args.model, 
                with_timestamps=args.timestamps,
                cleanup=not args.keep_audio,
                verbose=args.verbose
            )
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
