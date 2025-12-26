"""
Script to download video from OneDrive link
"""

import requests
import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import re


def convert_onedrive_url_to_direct(onedrive_url: str) -> str:
    """
    Convert OneDrive sharing link to direct download URL
    
    Args:
        onedrive_url: OneDrive sharing link
        
    Returns:
        Direct download URL
    """
    # Extract the file ID from OneDrive URL
    # OneDrive URL format: https://1drv.ms/v/c/SHARE_ID?e=QUERYSTRING
    if '1drv.ms' in onedrive_url:
        # For video files, use /download=1 parameter
        if '?' in onedrive_url:
            base_url = onedrive_url.split('?')[0]
            direct_url = base_url + '?download=1'
            return direct_url
        else:
            return onedrive_url + '?download=1'
    
    # Handle direct sharepoint/onedrive.com URLs
    if 'onedrive.com' in onedrive_url or 'sharepoint.com' in onedrive_url:
        if '?' in onedrive_url:
            return onedrive_url + '&download=1'
        else:
            return onedrive_url + '?download=1'
    
    return onedrive_url


def download_video(url: str, output_filename: str = None) -> bool:
    """
    Download video from OneDrive
    
    Args:
        url: OneDrive video URL
        output_filename: Optional custom filename (default: video.mp4)
        
    Returns:
        True if download successful, False otherwise
    """
    if output_filename is None:
        output_filename = 'video.mp4'
    
    # Convert OneDrive URL to direct download URL
    direct_url = convert_onedrive_url_to_direct(url)
    
    output_path = Path(__file__).parent / output_filename
    
    try:
        print(f"Downloading video from: {url}")
        print(f"Direct URL: {direct_url}")
        print(f"Saving to: {output_path}")
        
        # Headers to mimic browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Download with streaming to handle large files
        response = requests.get(direct_url, stream=True, timeout=30, headers=headers, allow_redirects=True)
        response.raise_for_status()
        
        # Get total file size
        total_size = int(response.headers.get('content-length', 0))
        
        print(f"File size: {total_size / (1024*1024*1024):.2f} GB")
        
        if total_size < 1024*1024:  # Less than 1MB
            print("⚠ Warning: File appears to be very small (< 1MB). This might not be the actual video.")
        
        # Download with progress
        downloaded = 0
        chunk_size = 1024*1024  # 1MB chunks for better progress reporting
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size:
                        percent = (downloaded / total_size) * 100
                        print(f"Progress: {percent:.1f}% ({downloaded / (1024*1024*1024):.2f}GB / {total_size / (1024*1024*1024):.2f}GB)", end='\r')
        
        # Verify file size
        actual_size = output_path.stat().st_size
        print(f"\n✓ Video downloaded successfully!")
        print(f"  File: {output_path}")
        print(f"  Size: {actual_size / (1024*1024*1024):.2f} GB")
        
        if actual_size < 1024*1024:
            print("⚠ Warning: Downloaded file is very small. It may not have downloaded correctly.")
            print("  Try opening the link in a browser to verify it's accessible.")
            return False
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Download failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    # OneDrive video URL
    VIDEO_URL = "https://1drv.ms/v/c/9bc898f01b89e9f9/IQABbo4uCXjqQJIMca7N9cvbAX2mxS9eOy_GB73KAwSA0XY?e=BE9hvv"
    
    # Download the video
    success = download_video(VIDEO_URL, output_filename="video.mp4")
    
    if success:
        exit(0)
    else:
        exit(1)
