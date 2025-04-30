# Audio to Transcript Converter

A Python tool that extracts text transcripts from MP3, MP4, and M4A files using local compute resources. This tool extracts audio, performs speech-to-text conversion using Whisper.

## Features

- **100% Local Processing**: No API keys or internet connection required
- **Multiple Model Options**: Choose from tiny to large models based on your accuracy needs
- **Graphical User Interface**: User-friendly GUI with drag and drop file selection and customizable processing options

## Installation

### Prerequisites

- Python 3.12 or higher
- [FFmpeg](https://formulae.brew.sh/formula/ffmpeg) (for audio extraction)

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
       - Use drag and drop to add files, or select from quick options (see below for configuration)
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
  - Uses "medium" model by default for fastest processing
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

#### Default Input/Output Directories (.env)

You can customize the default _input_ and _output_ directories used by the "Browse" buttons by creating a `.env` file in the project root directory:

```dotenv
# Default directories
DEFAULT_INPUT_LOCATION='/path/to/your/videos'
DEFAULT_OUTPUT_LOCATION='/path/to/save/transcripts'
```

If the `.env` file doesn't exist or a setting is missing, the application will use these defaults:

- Input location: `~/Movies`
- Output location: `~/Downloads`

#### Quick Path Selection (quick_paths.json)

The GUI includes a "Source" dropdown menu that allows you to quickly select predefined directories when adding files. To configure these paths:

1.  **Copy the example file**:
    ```bash
    cp quick_paths.example.json quick_paths.json
    ```
2.  **Edit `quick_paths.json`**: Open the newly created `quick_paths.json` file and replace the placeholder paths with the actual paths on your system. The keys (e.g., "My Videos") will be the names displayed in the dropdown.

```json
{
  "My Videos": "/actual/path/to/your/videos",
  "Project Audio": "/actual/path/to/your/project/audio/files",
  "Downloads": "/actual/path/to/your/downloads"
}
```

3.  **Manage in GUI**: You can also add, edit, or delete these paths directly within the application by clicking the "Manage..." button next to the "Source" dropdown.

**Note**: `quick_paths.json` is included in `.gitignore`, so your personal paths won't be committed to the repository. If `quick_paths.json` is missing or invalid, the dropdown will only show the "Browse..." option, and a message will guide you to create the file from the example.

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

- Processing time depends on video length, model size, and your hardware
- The medium model offers a good balance between accuracy and performance for most cases

## Troubleshooting

1. **FFmpeg errors**: Ensure FFmpeg is properly installed and in your PATH
2. **CUDA errors**: Update your GPU drivers or fall back to CPU-only mode
3. **Memory issues**: Try a smaller model size or process shorter video segments
4. **NLTK data errors**: If you see warnings about NLTK resources, you can run `python download_nltk_data.py` to download them. The transcriber will still work without these resources by using a simplified sentence splitting algorithm.


### Note on Dependencies

The mp4-to-transcript tool requires an active virtual environment where it's installed. The commands are only available when the virtual environment is activated.

- The GUI interface requires PyQt6, which will be automatically installed when you install the package.
- The application uses python-dotenv for configuration management.
- If you encounter any GUI-related issues, ensure the dependencies are properly installed: `pip install PyQt6 python-dotenv`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
