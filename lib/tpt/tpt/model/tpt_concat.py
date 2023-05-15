"""
TPTConcat module
"""
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey, Enum
from tpt.commons import CmpTypeEnum
from .util import DB_SCHEMA, BASE


class TPTConcat(BASE):
    """
    TPTConcat class
    """
    __tablename__ = 'tpt_concat'

    __table_args__ = {"schema": DB_SCHEMA}

    concat_id = Column(Integer, primary_key=True)
    request_id = Column(ForeignKey(DB_SCHEMA + ".tpt_request.id"), primary_key=True)
    type = Column(Enum(CmpTypeEnum, native_enum=False), nullable=False, default=CmpTypeEnum.TEXT)
    size = Column(Integer, nullable=True)

    # Add a relationship between the files and the request
    request = relationship("TPTRequest", back_populates="concats")

    def __repr__(self):
        return "<Concat (id='%s', req='%s', type='%s')>" % (self.concat_id, self.request_id,
                                                            self.type.value)

    def __str__(self):
        return self.__class__.__name__
