"""
Utility functions for cross-platform compatibility.
"""

import sys
from pathlib import Path
from typing import List


def get_acceptable_encodings() -> List[str]:
    """
    Get a list of acceptable encodings for cross-platform compatibility.

    Returns:
        List of encoding names that are considered acceptable across platforms.
    """
    return [
        "utf-8",
        "utf-8-sig",
        "utf-16",
        "utf-16le",
        "utf-16be",
        "windows-1252",
        "windows-1254",
        "cp1252",
        "cp1254",
        "iso-8859-1",
        "latin-1",
        "ascii",  # Added 'ascii' as acceptable encoding
    ]


def is_acceptable_encoding(encoding: str) -> bool:
    """
    Check if an encoding is acceptable for cross-platform compatibility.

    Args:
        encoding: The encoding name to check.

    Returns:
        True if the encoding is acceptable, False otherwise.
    """
    return encoding.lower() in [enc.lower() for enc in get_acceptable_encodings()]


def normalize_encoding(encoding: str) -> str:
    """
    Normalize encoding name for consistency across platforms.

    Args:
        encoding: The encoding name to normalize.

    Returns:
        Normalized encoding name.
    """
    encoding_lower = encoding.lower()

    # Normalize common Windows encodings
    if encoding_lower in ["windows-1252", "cp1252"]:
        return "windows-1252"
    elif encoding_lower in ["windows-1254", "cp1254"]:
        return "windows-1254"
    elif encoding_lower in ["iso-8859-1", "latin-1"]:
        return "iso-8859-1"

    return encoding_lower


def get_platform_default_encoding() -> str:
    """
    Get the default encoding for the current platform.

    Returns:
        The default encoding name for the current platform.
    """
    if sys.platform.startswith("win"):
        return "windows-1252"  # Common Windows default
    else:
        return "utf-8"  # Common Unix/Linux default


def detect_file_encoding(file_path: Path) -> str:
    """
    Detect file encoding with platform-aware fallbacks.

    Args:
        file_path: Path to the file to detect encoding for.

    Returns:
        The detected encoding name.
    """
    try:
        import chardet

        with open(file_path, "rb") as f:
            raw_data = f.read()

            # Check for BOM first (most reliable)
            if raw_data.startswith(b"\xef\xbb\xbf"):
                return "utf-8-sig"
            elif raw_data.startswith(b"\xff\xfe") or raw_data.startswith(b"\xfe\xff"):
                return "utf-16"

            # Use chardet to detect encoding
            result = chardet.detect(raw_data)
            detected_encoding = result["encoding"]
            confidence = result["confidence"]

            # If confidence is high and it's a common encoding, use it
            if confidence > 0.8:
                # Normalize common Windows encodings to UTF-8 for consistency
                if detected_encoding and detected_encoding.lower() in [
                    "windows-1252",
                    "windows-1254",
                    "cp1252",
                    "cp1254",
                    "iso-8859-1",
                    "latin-1",
                ]:
                    # Try to decode as UTF-8 first, if it works, use UTF-8
                    try:
                        raw_data.decode("utf-8")
                        return "utf-8"
                    except UnicodeDecodeError:
                        # If UTF-8 fails, use the detected encoding
                        return normalize_encoding(detected_encoding)
                elif detected_encoding:
                    return normalize_encoding(detected_encoding)

            # Default to UTF-8
            return "utf-8"

    except ImportError:
        # Fallback: try UTF-8 first, then system default
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                f.read()
            return "utf-8"
        except UnicodeDecodeError:
            # Use system default encoding as last resort
            return get_platform_default_encoding()
