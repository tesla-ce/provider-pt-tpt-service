"""
Request status
"""
import enum


class ReqStatusEnum(enum.Enum):
    """
    Request status class
    """
    PENDING_EXTRACT = "pending_extract"
    PENDING = "pending"
    PREPARED = "prepared"
    PROCESSING = "processing"
    PROCESSED = "processed"
    UPDATING = "updating"
    ERROR = "error"
    PERMISSION_ERROR = "permission_error"
