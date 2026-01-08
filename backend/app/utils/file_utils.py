"""
File utility functions for source management.

Educational Note: This module provides file type validation and categorization
for the source management system. It follows the NoobBook pattern of organizing
files by category (document, image, audio, data).
"""
import os
from pathlib import Path
from typing import Dict, List

# Allowed file extensions by category (matching NoobBook)
ALLOWED_EXTENSIONS = {
    'document': ['.pdf', '.docx', '.pptx', '.txt', '.md'],
    'image': ['.png', '.jpg', '.jpeg', '.webp', '.gif'],
    'audio': ['.mp3', '.wav', '.m4a', '.ogg', '.flac'],
    'data': ['.csv']
}

# Flatten for easy lookup
_ALL_EXTENSIONS = set()
for extensions in ALLOWED_EXTENSIONS.values():
    _ALL_EXTENSIONS.update(extensions)


def is_allowed_file_type(filename: str) -> bool:
    """
    Check if a file type is allowed.

    Args:
        filename: The filename to check

    Returns:
        True if the file type is allowed, False otherwise
    """
    if not filename:
        return False
    
    extension = Path(filename).suffix.lower()
    return extension in _ALL_EXTENSIONS


def get_file_category(filename: str) -> str:
    """
    Get the category for a file based on its extension.

    Args:
        filename: The filename to categorize

    Returns:
        The category name (document, image, audio, data) or 'unknown'
    """
    if not filename:
        return 'unknown'
    
    extension = Path(filename).suffix.lower()
    
    for category, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return category
    
    return 'unknown'


def get_file_size(file_path: Path) -> int:
    """
    Get the size of a file in bytes.

    Args:
        file_path: Path to the file

    Returns:
        File size in bytes, or 0 if file doesn't exist
    """
    try:
        return file_path.stat().st_size
    except (OSError, IOError):
        return 0


def format_file_size(size_bytes: int) -> str:
    """
    Format a file size in bytes to a human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def get_mime_type(filename: str) -> str:
    """
    Get the MIME type for a file based on its extension.

    Args:
        filename: The filename

    Returns:
        MIME type string
    """
    extension = Path(filename).suffix.lower()
    
    mime_types = {
        # Document types
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.txt': 'text/plain',
        '.md': 'text/markdown',
        
        # Image types
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.webp': 'image/webp',
        '.gif': 'image/gif',
        
        # Audio types
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.m4a': 'audio/mp4',
        '.ogg': 'audio/ogg',
        '.flac': 'audio/flac',
        
        # Data types
        '.csv': 'text/csv'
    }
    
    return mime_types.get(extension, 'application/octet-stream')


def generate_unique_filename(directory: Path, base_name: str, extension: str) -> str:
    """
    Generate a unique filename in a directory.

    Args:
        directory: Target directory
        base_name: Base filename (without extension)
        extension: File extension (with dot)

    Returns:
        Unique filename
    """
    filename = f"{base_name}{extension}"
    counter = 1
    
    while (directory / filename).exists():
        filename = f"{base_name}_{counter}{extension}"
        counter += 1
    
    return filename