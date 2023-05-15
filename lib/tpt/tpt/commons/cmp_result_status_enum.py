"""
Comparison result status enum
"""
import enum


class CmpResultStatusEnum(enum.Enum):
    """
    Comparison result status enum class
    """
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
