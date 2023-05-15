"""
TPTRequest module
"""
from sqlalchemy import Column, Integer, Float, String, ForeignKey, Boolean, DateTime, func, Enum
from sqlalchemy.orm import relationship
from tpt.commons import ReqStatusEnum
from .util import DB_SCHEMA, BASE


class TPTRequest(BASE):
    """
    TPTRequest class
    """
    __tablename__ = 'tpt_request'

    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(Integer, primary_key=True)
    original_request_id = Column(String)
    user_id = Column(String, nullable=False)
    activity_id = Column(ForeignKey(DB_SCHEMA + ".tpt_activity.activity_id"), nullable=False)
    status = Column(Enum(ReqStatusEnum, native_enum=False), nullable=False,
                    default=ReqStatusEnum.PENDING)

    pending_update = Column(Boolean, nullable=False, default=False)
    path = Column(String, nullable=True)
    files_result = Column(Float, nullable=False, default=0)
    concats_result = Column(Float, nullable=False, default=0)
    msg = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Add a relationship between the request and the files
    files = relationship("TPTFile", back_populates="request")

    # Add a relationship between the request and the concatenations
    concats = relationship("TPTConcat", back_populates="request")

    # Add a relationship between the request and the activity
    activity = relationship("TPTActivity", back_populates="requests")

    def __repr__(self):
        return "<Request (id='%s', originalrequestid='%s', user='%s', status='%s')>" \
               % (self.id, self.original_request_id, self.user_id, self.status)

    def __str__(self):
        return self.__class__.__name__
