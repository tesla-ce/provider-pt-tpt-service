"""
TPTStatistics module
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, func, Enum
from tpt.commons import StatisticTypeEnum
from .util import DB_SCHEMA, BASE


class TPTStatistics(BASE):
    """
    TPTStatistics class
    """
    __tablename__ = 'tpt_statistics'

    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(Integer, primary_key=True)
    item_id = Column(String, nullable=True)
    type = Column(Enum(StatisticTypeEnum, native_enum=False), nullable=False,
                  default=StatisticTypeEnum.ELAPSED_TIME)

    name = Column(String, nullable=True)
    value = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return "<TPTStatistics (id='%s', item_id='%s', type='%s', name='%s', value='%s')>" \
               % (self.id, self.item_id, self.type, self.name, self.value)

    def __str__(self):
        return self.__class__.__name__
