"""
Integration between GUI and mp4_transcriber backend.
"""
import os
import json
import traceback
import multiprocessing
from pathlib import Path
import signal
import sys

from mp4_transcriber.audio import extract_audio
from mp4_transcriber.transcription import transcribe_audio, create_transcript_with_timestamps
from mp4_transcriber.text_processing import clean_transcript

# Global process reference for termination
current_process = None

def transcription_worker(file_path, output_path, model_size, with_timestamps, auto_clean, 
                         result_queue, progress_queue):
    """
    Worker function to run in a separate process for transcription.
    """
    try:
        # Extract audio
        progress_queue.put(("log", f"Extracting audio from {os.path.basename(file_path)}"))
        progress_queue.put(("progress", 5, "Starting audio extraction..."))
        
        audio_path = extract_audio(file_path, verbose=True)
        if not audio_path:
            progress_queue.put(("log", "Failed to extract audio"))
            progress_queue.put(("error", "Failed to extract audio"))
            return
            
        progress_queue.put(("progress", 30, "Audio extraction complete"))
        progress_queue.put(("log", f"Transcribing with {model_size} model..."))
        progress_queue.put(("progress", 35, f"Starting transcription with {model_size} model..."))
        
        # Transcribe
        result = transcribe_audio(audio_path, model_size, True)
        
        progress_queue.put(("progress", 80, "Transcription complete"))
        progress_queue.put(("log", "Processing transcript..."))
        progress_queue.put(("progress", 85, "Processing transcript..."))
        
        # Process transcript
        try:
            if with_timestamps:
                transcript = create_transcript_with_timestamps(result['segments'])
                progress_queue.put(("log", "Added timestamps to transcript"))
            else:
                if auto_clean:
                    transcript = clean_transcript(result)
                    progress_queue.put(("log", "Cleaned transcript text"))
                else:
                    transcript = result.get('text', '')
        except Exception as e:
            progress_queue.put(("log", f"Warning: Error during transcript formatting: {str(e)}"))
            # Fallback to raw text
            transcript = result.get('text', '')
            progress_queue.put(("log", "Using raw transcript text without formatting."))
            
            # Basic cleanup
            transcript = transcript.strip()
            if transcript and transcript[0].islower():
                transcript = transcript[0].upper() + transcript[1:]
        
        # Save transcript
        progress_queue.put(("progress", 90, "Saving transcript..."))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(transcript)
            
        progress_queue.put(("log", f"Transcript saved to {output_path}"))
        progress_queue.put(("progress", 100, "Completed"))
        
        # Cleanup audio file if needed
        if not auto_clean and audio_path and os.path.exists(audio_path):
            os.unlink(audio_path)
            progress_queue.put(("log", "Cleaned up temporary audio file"))
        
        # Signal completion
        result_queue.put(("completed", output_path))
        
    except Exception as e:
        progress_queue.put(("log", f"Error: {str(e)}"))
        progress_queue.put(("error", str(e)))
        traceback.print_exc()

class GUIProcessor:
    """
    Wrapper for mp4_transcriber functionality that reports progress back to the GUI.
    """
    def __init__(self, signals):
        """
        Initialize with signal handlers from the worker.
        
        Args:
            signals: WorkerSignals instance for reporting progress
        """
        self.signals = signals
        self.process = None
        
    def process_file(self, file_path, output_dir, model_name, include_timestamps, auto_clean, keep_audio):
        """
        Process a single MP4 file with progress reporting using multiprocessing.
        
        Args:
            file_path: Path to the MP4 file
            output_dir: Directory to save the output transcript
            model_name: Whisper model name to use
            include_timestamps: Whether to include timestamps in the transcript
            auto_clean: Whether to clean up the transcript
            keep_audio: Whether to keep the temporary audio file
        """
        try:
            # Create output dir if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate output filename
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_file = os.path.join(output_dir, f"{base_name}.txt")
            
            # Create queues for process communication
            result_queue = multiprocessing.Queue()
            progress_queue = multiprocessing.Queue()
            
            # Create and start process
            self.process = multiprocessing.Process(
                target=transcription_worker,
                args=(
                    file_path,
                    output_file,
                    model_name,
                    include_timestamps,
                    auto_clean,
                    result_queue,
                    progress_queue
                )
            )
            
            # Set as daemon so it terminates when main process exits
            self.process.daemon = True
            self.process.start()
            
            global current_process
            current_process = self.process
            
            # Monitor queues until process completes or is terminated
            self.monitor_process(file_path, self.process, result_queue, progress_queue)
            
        except Exception as e:
            self.signals.log.emit(f"Error setting up process: {str(e)}")
            self.signals.error.emit(file_path, str(e))
            traceback.print_exc()
            
    def monitor_process(self, file_path, process, result_queue, progress_queue):
        """
        Monitor the progress queue for updates from the transcription process.
        
        Args:
            file_path: Path to the MP4 file being processed
            process: The multiprocessing.Process object
            result_queue: Queue for results
            progress_queue: Queue for progress updates
        """
        import time
        
        while process.is_alive():
            # Check for progress updates
            while not progress_queue.empty():
                try:
                    update = progress_queue.get_nowait()
                    if update[0] == "progress":
                        _, percent, message = update
                        self.signals.progress.emit(file_path, percent, message)
                    elif update[0] == "log":
                        self.signals.log.emit(update[1])
                    elif update[0] == "error":
                        self.signals.error.emit(file_path, update[1])
                except Exception as e:
                    self.signals.log.emit(f"Error receiving update: {str(e)}")
            
            # Check for results
            if not result_queue.empty():
                try:
                    result = result_queue.get_nowait()
                    if result[0] == "completed":
                        self.signals.completed.emit(file_path)
                except Exception as e:
                    self.signals.log.emit(f"Error receiving result: {str(e)}")
            
            # Small delay to prevent CPU spinning
            time.sleep(0.1)
        
        # Process has ended, check if there are any remaining messages
        try:
            while not progress_queue.empty():
                update = progress_queue.get_nowait()
                if update[0] == "progress":
                    _, percent, message = update
                    self.signals.progress.emit(file_path, percent, message)
                elif update[0] == "log":
                    self.signals.log.emit(update[1])
                elif update[0] == "error":
                    self.signals.error.emit(file_path, update[1])
                    
            while not result_queue.empty():
                result = result_queue.get_nowait()
                if result[0] == "completed":
                    self.signals.completed.emit(file_path)
        except Exception as e:
            self.signals.log.emit(f"Error processing remaining messages: {str(e)}")
            
    def terminate(self):
        """
        Terminate the current transcription process if it exists.
        """
        if self.process and self.process.is_alive():
            # Terminate without excessive logging
            self.process.terminate()
            self.process.join(timeout=1)  # Wait a bit for clean termination
            
            # If process is still alive, try more aggressive termination
            if self.process.is_alive():
                if hasattr(os, 'kill'):
                    try:
                        os.kill(self.process.pid, signal.SIGKILL)
                    except Exception:
                        pass
