"""
Tests for the audio module.
"""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from mp4_transcriber.audio import extract_audio, check_ffmpeg_installed


class TestAudio(unittest.TestCase):
    """Test cases for audio module functions."""
    
    @patch('subprocess.run')
    def test_extract_audio_success(self, mock_run):
        """Test successful audio extraction."""
        # Setup mock
        mock_run.return_value = MagicMock(returncode=0)
        
        # Call function with temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp4') as video_file:
            with tempfile.NamedTemporaryFile(suffix='.wav') as audio_file:
                result = extract_audio(video_file.name, audio_file.name)
                
                # Verify result
                self.assertEqual(result, audio_file.name)
                mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_extract_audio_failure(self, mock_run):
        """Test failed audio extraction."""
        # Setup mock to raise exception
        mock_run.side_effect = Exception("FFmpeg error")
        
        # Call function
        with tempfile.NamedTemporaryFile(suffix='.mp4') as video_file:
            result = extract_audio(video_file.name)
            
            # Verify result
            self.assertIsNone(result)
    
    @patch('subprocess.run')
    def test_check_ffmpeg_installed_true(self, mock_run):
        """Test ffmpeg installation check when installed."""
        # Setup mock
        mock_run.return_value = MagicMock(returncode=0)
        
        # Call function
        result = check_ffmpeg_installed()
        
        # Verify result
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_check_ffmpeg_installed_false(self, mock_run):
        """Test ffmpeg installation check when not installed."""
        # Setup mock to raise FileNotFoundError
        mock_run.side_effect = FileNotFoundError("No such file or directory: 'ffmpeg'")
        
        # Call function
        result = check_ffmpeg_installed()
        
        # Verify result
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
