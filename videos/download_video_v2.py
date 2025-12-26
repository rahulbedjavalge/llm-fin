"""
Script to download video from OneDrive link using yt-dlp
"""

import subprocess
import sys
from pathlib import Path


def download_video_with_ytdlp(url: str, output_filename: str = "video.mp4") -> bool:
    """
    Download video using yt-dlp which handles redirects and authentication better
    
    Args:
        url: Video URL (OneDrive link)
        output_filename: Output filename
        
    Returns:
        True if successful, False otherwise
    """
    output_path = Path(__file__).parent / output_filename
    
    try:
        print(f"Downloading video from: {url}")
        print(f"Output file: {output_path}")
        print("-" * 80)
        
        # yt-dlp command
        cmd = [
            sys.executable, "-m", "yt_dlp",
            "--no-warnings",
            "-f", "best",
            "-o", str(output_path),
            url
        ]
        
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode == 0 and output_path.exists():
            file_size_gb = output_path.stat().st_size / (1024 * 1024 * 1024)
            print("-" * 80)
            print(f"✓ Video downloaded successfully!")
            print(f"  File: {output_path}")
            print(f"  Size: {file_size_gb:.2f} GB")
            return True
        else:
            print("✗ Download failed")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    # OneDrive video URL
    VIDEO_URL = "https://1drv.ms/v/c/9bc898f01b89e9f9/IQABbo4uCXjqQJIMca7N9cvbAX2mxS9eOy_GB73KAwSA0XY?e=BE9hvv"
    
    # Download the video
    success = download_video_with_ytdlp(VIDEO_URL, output_filename="video.mp4")
    
    sys.exit(0 if success else 1)
