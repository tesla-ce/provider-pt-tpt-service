"""
Folder type type enum
"""
import enum


class FolderTypeEnum(enum.Enum):
    """
    Folder type type enum class
    """
    TEMP_SOURCE = "src"
    TEMP_EXTRACTED = "ext"
    STORE_BASE = ""
    STORE_FILES = "files"
    STORE_CONCATS = "concats"
