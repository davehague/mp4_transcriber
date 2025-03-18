#!/usr/bin/env python
"""
Utility script to download required NLTK data.
"""

import nltk
import sys

def download_nltk_data():
    """Download required NLTK data packages."""
    print("Downloading required NLTK data...")
    try:
        # Download the punkt tokenizer data
        nltk.download('punkt')
        # Attempt to download punkt_tab explicitly as well
        try:
            nltk.download('punkt_tab')
        except:
            print("Note: punkt_tab resource not available directly. Using alternative approach.")
            # punkt_tab is part of the punkt package but might not be directly downloadable
        
        print("NLTK data downloaded successfully.")
        return True
    except Exception as e:
        print(f"Error downloading NLTK data: {e}")
        return False

if __name__ == "__main__":
    success = download_nltk_data()
    sys.exit(0 if success else 1)
