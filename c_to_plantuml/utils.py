#!/usr/bin/env python3
"""
Utility functions for C to PlantUML converter
"""

import logging
from pathlib import Path
from typing import Dict, Optional

# Try to import chardet, fallback to basic encoding detection if not available
try:
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False


def detect_file_encoding(file_path: Path) -> str:
    """Detect file encoding with platform-aware fallbacks"""
    try:
        if CHARDET_AVAILABLE:
            # Try to detect encoding with chardet
            with open(file_path, "rb") as f:
                raw_data = f.read(1024)  # Read first 1KB for detection
                if raw_data:
                    result = chardet.detect(raw_data)
                    if result and result["confidence"] > 0.7:
                        return result["encoding"]

        # Fallback encodings in order of preference
        fallback_encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
        
        for encoding in fallback_encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    f.read(1024)  # Test read
                return encoding
            except (UnicodeDecodeError, UnicodeError):
                continue

        # Final fallback
        return "utf-8"
        
    except Exception as e:
        logging.warning(f"Failed to detect encoding for {file_path}: {e}")
        return "utf-8"


def get_filename_from_path(file_path: str) -> str:
    """Extract filename from a file path (handles both absolute and relative paths)"""
    return Path(file_path).name


def find_file_by_filename(filename: str, file_dict: Dict[str, any]) -> Optional[str]:
    """
    Find a file in a dictionary by matching its filename.
    
    Args:
        filename: The filename to search for (e.g., "header.h")
        file_dict: Dictionary with file paths as keys
        
    Returns:
        The matching file path key, or None if not found
    """
    # First try exact match
    if filename in file_dict:
        return filename
    
    # Try matching by filename
    for file_path in file_dict.keys():
        if Path(file_path).name == filename:
            return file_path
    
    return None


def normalize_file_path(file_path: str, project_root: str = None) -> str:
    """
    Normalize file path for consistent handling.
    For tracking purposes, we prefer relative paths when possible.
    
    Args:
        file_path: The file path to normalize
        project_root: Optional project root for relative path conversion
        
    Returns:
        Normalized file path
    """
    path_obj = Path(file_path)
    
    # If we have a project root and the path is absolute, try to make it relative
    if project_root and path_obj.is_absolute():
        try:
            relative_path = path_obj.relative_to(Path(project_root))
            return str(relative_path)
        except ValueError:
            # Path is not relative to project root, keep as is
            pass
    
    return str(path_obj)


def create_file_key(file_path: str, project_root: str = None) -> str:
    """
    Create a consistent file key for tracking.
    Uses filename for uniqueness since filenames are unique in the project.
    
    Args:
        file_path: The file path
        project_root: Optional project root for normalization
        
    Returns:
        A consistent file key (filename)
    """
    return get_filename_from_path(file_path)
