"""
Comparison type enum
"""
import enum


class CmpTypeEnum(enum.Enum):
    """
    Comparison type enum class
    """
    AUTO = "auto"
    C = "c"
    CPP = "c++"
    JAVA = "java"
    TEXT = "text"
    TEXT_ONLY = "text_only"
    M2 = "m2"
    MIRANDA = "miranda"
    PASCAL = "pascal"
    ASSEMBLER = "assembler"
