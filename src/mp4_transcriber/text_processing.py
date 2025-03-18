"""
Text processing utilities for cleaning up transcription output.
"""

import re
import nltk
from nltk.tokenize import sent_tokenize as nltk_sent_tokenize

# Define our own sent_tokenize that handles missing resources gracefully
def sent_tokenize(text):
    """Tokenize text into sentences, with fallback for missing resources."""
    try:
        return nltk_sent_tokenize(text)
    except LookupError as e:
        print(f"Warning: NLTK tokenization failed, using simple fallback: {e}")
        # Simple period-based sentence splitting as fallback
        return [s.strip() for s in text.split('.') if s.strip()]


def clean_transcript(transcript_data):
    """
    Clean up the transcript.
    
    Args:
        transcript_data (dict or str): Transcript data from Whisper or text string
        
    Returns:
        str: Cleaned transcript text
    """
    # Get the text from the transcript data
    if isinstance(transcript_data, dict):
        text = transcript_data.get('text', '')
    else:
        text = transcript_data
    
    # Basic cleanup
    text = re.sub(r'\s+', ' ', text)                 # Remove extra whitespace
    text = re.sub(r'(\w)- (\w)', r'\1\2', text)      # Join hyphenated words
    text = re.sub(r'\(\s*[Uu]nintelligible\s*\)', '', text)  # Remove unintelligible markers
    
    # Ensure proper sentence boundaries
    sentences = sent_tokenize(text)
    
    # Capitalize first letter of each sentence
    sentences = [s[0].upper() + s[1:] if s and len(s) > 0 else s for s in sentences]
    
    # Join sentences with proper spacing
    cleaned_text = ' '.join(sentences)
    
    return cleaned_text
