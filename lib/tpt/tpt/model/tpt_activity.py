"""
TPTActivty module
"""
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, DateTime, func, Enum, Boolean
from tpt.commons import ActContextEnum, CmpTypeEnum
from .util import DB_SCHEMA, BASE


class TPTActivity(BASE):
    """
    TPTActivty class
    """
    __tablename__ = 'tpt_activity'
    __table_args__ = {"schema": DB_SCHEMA}

    activity_id = Column(String, primary_key=True)
    course_id = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    activity_type = Column(Enum(CmpTypeEnum, native_enum=False), nullable=False,
                           default=CmpTypeEnum.TEXT_ONLY)
    context = Column(Enum(ActContextEnum, native_enum=False), nullable=False,
                     default=ActContextEnum.ACTIVITY)
    config = Column(String, nullable=True)

    requests = relationship("TPTRequest", back_populates="activity")

    archive = Column(Boolean, nullable=False, default=False)
    locked = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return "<Activity (id='%s')>" % self.activity_id

    def __str__(self):
        return self.__class__.__name__
