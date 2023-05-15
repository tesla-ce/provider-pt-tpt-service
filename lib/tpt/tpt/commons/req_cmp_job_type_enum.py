"""
Request comparison jobs type
"""
import enum


class ReqCmpJobTypeEnum(enum.Enum):
    """
    Request comparison jobs type class
    """
    FILES = "files" # comparing files
    CONCATS = "concats"  # comparing concats
    BOTH = "both"  # comparing both types
