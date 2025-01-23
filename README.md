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

For Windows users:
- Download ffmpeg-master-latest-win64-gpl.zip from https://github.com/BtbN/FFmpeg-Builds/releases
- Extract to desired directory (e.g., C:\ffmpeg)
- Add to system PATH:
  1. Open System Properties > Advanced > Environment Variables (시스템 환경 변수 편집 -> 환경변수)
  2. Under "System Variables", select "Path" (시스템 변수 -> Path)
  3. Add path to ffmpeg\bin folder (새로만들기 후 ffmpeg의 bin 폴더 경로 추가)
  4. Verify with `ffmpeg -version` in Command Prompt



For Linux users:
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

2. Install required Python packages
```bash
pip install -r whisper_requirements.txt
```

 3. Install PyTorch

Install PyTorch with CUDA support:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Verify CUDA installation:
```python
import torch
print(torch.cuda.is_available())  # Should return True
print(torch.version.cuda)         # Should show CUDA version
```

Note: This installation assumes CUDA 12.1. If you have a different CUDA version, adjust the command accordingly.

## Usage Instructions

1. Launch the application
```bash
python whisper_e2k.py
```

2. Access the web interface
   - Browser opens automatically
   - Default: http://localhost:7860

3. Input Source Selection
   - "File" tab: Upload local video/audio files
   - "Link" tab: Enter YouTube video URL

4. Configure Options
   - Select Whisper model
   - Choose input language
   - Select output format
   - Set translation options
   - Toggle timestamp inclusion
   - Specify output filename

5. Click "Generate Subtitles"
   - Files download automatically when complete

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
   - Ensure PyTorch version matches CUDA version

2. FFmpeg Issues
   - Verify FFmpeg is in system PATH
   - For Windows, confirm executables location

3. Common Error Solutions
   - "CUDA out of memory": Use smaller model
   - "FFmpeg not found": Check installation/PATH
   - "Invalid YouTube URL": Verify URL format

## License

This project is distributed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
