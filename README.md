<<<<<<< HEAD
# Whisper Subtitle Generator

A subtitle generation tool utilizing OpenAI's Whisper for speech-to-text conversion. This application can automatically generate English and Korean subtitles from video/audio files or YouTube links.

## Key Features

- Support for multiple video/audio formats (mp4, avi, mov, mkv, mp3, wav, m4a, webm)
- YouTube video subtitle extraction
- Multiple Whisper model options (from tiny to large-v3)
- English/Korean translation capabilities
- srt/txt subtitle file generation
- Optional timestamp inclusion
- Custom output filename support
- User-friendly web interface wiht gradio

## System Requirements

- Python 3.10 or higher (Python 3.10 is recommended)
- NVIDIA GPU (with CUDA support)
- ffmpeg

## Installation

1. Install ffmpeg 
```
For Windows users
Download and install ffmpeg-master-latest-win64-gpl.zip from https://github.com/BtbN/FFmpeg-Builds/releases
```

2. Install required Python packages
```bash
pip install -r whisper_requirements.txt
```

## Usage Instructions

1. Launch the application
```bash
python whisper_e2k.py
```

2. Access the web interface
   - A browser window will automatically open
   - Default address: http://localhost:7860

3. Input Source Selection
   - "File" tab: Upload local video/audio files
   - "Link" tab: Enter YouTube video URL

4. Configure Options
   - Select Whisper model (tiny, base, small, medium, large, etc.)
   - Choose input language (Auto-detect, Korean, English, Japanese, Chinese)
   - Select output format (srt/txt)
   - Set translation options (English/Korean)
   - Toggle timestamp inclusion
   - Specify output filename

5. Click "Generate Subtitles"
   - Result files will be automatically downloaded upon completion

## Advanced Features

### Model Selection Guide
- tiny: Fastest, suitable for quick tests
- base: Good balance of speed and accuracy
- small: Better accuracy than base
- medium: High accuracy
- large/large-v2/large-v3: Best accuracy, requires more GPU memory

### Output Formats
- srt: Standard subtitle format with timestamps
- txt: Plain text format with optional timestamps

## Troubleshooting

1. CUDA Error Resolution
   - Ensure PyTorch version matches your CUDA version
   - Modify torch version in requirements.txt to match your system

2. FFmpeg Issues
   - Verify FFmpeg is correctly added to system PATH
   - For Windows users, confirm FFmpeg executables are in PATH

3. Common Error Solutions
   - "CUDA out of memory": Try using a smaller model
   - "FFmpeg not found": Check FFmpeg installation and PATH
   - "Invalid YouTube URL": Verify URL format and video availability


## License

This project is distributed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
=======
# whisper_e2k
>>>>>>> 197208a70d602bf1b820d45d6095368a313ffc3a
