#!/usr/bin/env python3
"""
Utility helpers used by the C to PlantUML converter.

Currently, only file encoding detection is required at runtime.
"""

import logging
from pathlib import Path

# Try to import chardet, fallback to basic encoding detection if not available
try:
    import chardet

    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False


def detect_file_encoding(file_path: Path) -> str:
    """Detect file encoding with platform-aware fallbacks."""
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

