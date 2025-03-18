"""
Tests for the text_processing module.
"""

import unittest
from mp4_transcriber.text_processing import clean_transcript


class TestTextProcessing(unittest.TestCase):
    """Test cases for text processing functions."""
    
    def test_clean_transcript_string(self):
        """Test cleaning a transcript from a string."""
        # Input with various issues
        text = "this is a   test. with  extra spaces. and lowercase sentences"
        
        # Expected result
        expected = "This is a test. With extra spaces. And lowercase sentences"
        
        # Clean the text
        result = clean_transcript(text)
        
        # Verify result
        self.assertEqual(result, expected)
    
    def test_clean_transcript_dict(self):
        """Test cleaning a transcript from a dictionary."""
        # Input with dictionary format similar to Whisper output
        transcript_data = {
            'text': "this is a   test. with  extra spaces. and lowercase sentences"
        }
        
        # Expected result
        expected = "This is a test. With extra spaces. And lowercase sentences"
        
        # Clean the text
        result = clean_transcript(transcript_data)
        
        # Verify result
        self.assertEqual(result, expected)
    
    def test_clean_transcript_hyphenated_words(self):
        """Test cleaning a transcript with hyphenated words."""
        # Input with hyphenated words
        text = "This is a multi- word sentence."
        
        # Expected result
        expected = "This is a multiword sentence."
        
        # Clean the text
        result = clean_transcript(text)
        
        # Verify result
        self.assertEqual(result, expected)
    
    def test_clean_transcript_unintelligible(self):
        """Test cleaning a transcript with unintelligible markers."""
        # Input with unintelligible markers
        text = "This is a (unintelligible) word."
        
        # Expected result
        expected = "This is a word."
        
        # Clean the text
        result = clean_transcript(text)
        
        # Verify result
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
