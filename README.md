# MP4 to Transcript Converter

A Python tool that extracts text transcripts from MP4 video files using local compute resources. This tool extracts audio, performs speech-to-text conversion, and cleans up the resulting transcript.

## Features

- **100% Local Processing**: No API keys or internet connection required
- **GPU Acceleration**: Utilizes CUDA for faster processing if available
- **Multiple Model Options**: Choose from tiny to large models based on your accuracy needs
- **Batch Processing**: Convert multiple MP4 files at once
- **Timestamp Support**: Optionally include timestamps in transcripts
- **Automatic Text Cleanup**: Improves transcript readability with proper formatting
- **Graphical User Interface**: User-friendly GUI with file queue management, real-time progress tracking, and customizable processing options

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for audio extraction)
- NVIDIA GPU with CUDA support (optional, for faster processing)
- NLTK data for text processing (optional; fallback mechanisms are in place)

### Setup

1. **Clone this repository**:

   ```bash
   git clone <repository-url>
   cd mp4_transcriber
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the package**:

   ```bash
   pip install -e .
   ```

4. **Download NLTK data (recommended but optional)**:

   ```bash
   python download_nltk_data.py
   ```
   
   Note: The transcriber will still work without NLTK data, using simplified text processing.

5. **Install FFmpeg**:
   - **Ubuntu/Debian**: `sudo apt update && sudo apt install ffmpeg`
   - **macOS** (using Homebrew): `brew install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

## Usage

### Basic Usage

Convert a single MP4 file to a transcript:

```bash
mp4-to-transcript -i video.mp4 -o transcript.txt
```

Or use the module directly:

```bash
python -m mp4_transcriber -i video.mp4 -o transcript.txt
```

### Using the GUI

For an easier user experience, you can use the graphical interface:

```bash
mp4-to-transcript-gui
```

Or use the module directly:

```bash
python -m mp4_transcriber.gui.app
```

The GUI provides these features:

- **File Management**
  - Add multiple MP4 files to the queue
  - Select which files to process using checkboxes
  - Process only checked files regardless of their status
  - Remove files from the queue

- **Transcription Options**
  - Select Whisper model size (tiny, base, small, medium, large)
  - Toggle timestamp inclusion
  - Enable/disable transcript auto-cleaning
  - Option to keep temporary audio files
  - Select output directory for transcripts

- **Process Monitoring**
  - Real-time progress tracking with progress bar
  - Current operation display
  - Timestamped log of all activities
  - Start/Stop controls with proper process termination

- **Default Settings**
  - Uses "tiny" model by default for fastest processing
  - Configurable default directories via `.env` file
  - Falls back to `~/Movies` for input and `~/Downloads` for output if not configured

#### GUI Screenshot

The GUI is organized with a clear layout:
- Top section: File management buttons (Add Files, Remove Selected, Start, Stop)
- File list: Shows all added files with checkboxes and status indicators
- Options panel: Configure transcription settings
- Progress section: Shows current file, operation, and progress bar
- Log window: Displays timestamped operation logs

### Configuration

You can customize default settings by creating a `.env` file in the project root directory:

```
# Default directories
DEFAULT_INPUT_LOCATION='/path/to/your/videos'
DEFAULT_OUTPUT_LOCATION='/path/to/save/transcripts'
```

If the `.env` file doesn't exist or a setting is missing, the application will use these defaults:
- Input location: `~/Movies`
- Output location: `~/Downloads`

### Advanced Command-Line Options

1. **Choose a different Whisper model**:

   ```bash
   mp4-to-transcript -i video.mp4 -m medium
   ```

   Available models: tiny, base, small, medium, large (larger models are more accurate but slower)

2. **Include timestamps in the transcript**:

   ```bash
   mp4-to-transcript -i video.mp4 -t
   ```

3. **Batch process all MP4 files in a directory**:

   ```bash
   mp4-to-transcript -i /path/to/videos/ -o /path/to/output/ -b
   ```

4. **Enable verbose output**:

   ```bash
   mp4-to-transcript -i video.mp4 -v
   ```

5. **Keep temporary audio files**:
   ```bash
   mp4-to-transcript -i video.mp4 --keep-audio
   ```

## Model Selection Guide

| Model  | Accuracy | Speed   | VRAM Required | Use Case                         |
| ------ | -------- | ------- | ------------- | -------------------------------- |
| tiny   | Lowest   | Fastest | 1GB           | Quick drafts, simple content     |
| base   | Low      | Fast    | 1GB           | Good default for most cases      |
| small  | Medium   | Medium  | 2GB           | Better accuracy for clear audio  |
| medium | High     | Slow    | 5GB           | High quality transcripts         |
| large  | Highest  | Slowest | 10GB          | Professional-grade transcription |

If you don't have a compatible GPU, the script will automatically use CPU.

## Performance Tips

- For best performance, use a computer with an NVIDIA GPU and ensure CUDA is properly installed
- Processing time depends on video length, model size, and your hardware
- The medium model offers a good balance between accuracy and performance for most cases
- For batch processing long videos, consider running overnight

## Troubleshooting

1. **FFmpeg errors**: Ensure FFmpeg is properly installed and in your PATH
2. **CUDA errors**: Update your GPU drivers or fall back to CPU-only mode
3. **Memory issues**: Try a smaller model size or process shorter video segments
4. **NLTK data errors**: If you see warnings about NLTK resources, you can run `python download_nltk_data.py` to download them. The transcriber will still work without these resources by using a simplified sentence splitting algorithm.

## Development

### Project Structure

```
mp4_transcriber/
├── src/                    # Source code
│   └── mp4_transcriber/    # Main package
│       ├── __init__.py     # Package initialization
│       ├── __main__.py     # Entry point for python -m
│       ├── audio.py        # Audio extraction utilities
│       ├── cli.py          # Command-line interface
│       ├── processor.py    # Video processing pipeline
│       ├── text_processing.py  # Text cleaning utilities
│       ├── transcription.py    # Speech-to-text functionality
│       └── gui/            # Graphical user interface
│           ├── __init__.py # GUI package initialization
│           ├── app.py      # GUI entry point
│           ├── main_window.py # Main window implementation
│           └── processor.py   # GUI integration with backend
├── tests/                  # Test suite
├── pyproject.toml         # Project metadata and dependencies
├── LICENSE                # MIT License
├── download_nltk_data.py  # Utility to download required NLTK data
└── README.md              # This file
```

### Running Tests

```bash
python -m pytest
```

or with coverage:

```bash
python -m pytest --cov=mp4_transcriber
```

### Note on Dependencies

The mp4-to-transcript tool requires an active virtual environment where it's installed. The commands are only available when the virtual environment is activated.

- The GUI interface requires PyQt6, which will be automatically installed when you install the package.
- The application uses python-dotenv for configuration management.
- If you encounter any GUI-related issues, ensure the dependencies are properly installed: `pip install PyQt6 python-dotenv`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
