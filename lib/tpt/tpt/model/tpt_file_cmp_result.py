"""
TPTFileCmpResult module
"""
from sqlalchemy import Column, Integer, Float, ForeignKeyConstraint, Enum
from tpt.commons import CmpTypeEnum, CmpResultStatusEnum
from .util import DB_SCHEMA, BASE


class TPTFileCmpResult(BASE):
    """
    TPTFileCmpResult module
    """
    __tablename__ = 'tpt_file_cmp_result'

    id = Column(Integer, primary_key=True)

    file_a_file_id = Column(Integer, primary_key=True)
    file_a_request_id = Column(Integer, primary_key=True)
    file_b_file_id = Column(Integer, primary_key=True)
    file_b_request_id = Column(Integer, primary_key=True)
    file_a_file_b_result = Column(Float, nullable=False)
    file_b_file_a_result = Column(Float, nullable=False)

    type = Column(Enum(CmpTypeEnum, native_enum=False), nullable=False, default=CmpTypeEnum.TEXT)

    status = Column(Enum(CmpResultStatusEnum, native_enum=False), nullable=False,
                    default=CmpResultStatusEnum.PENDING)

    relation = [DB_SCHEMA + '.tpt_file.file_id', DB_SCHEMA + '.tpt_file.request_id']
    __table_args__ = (
        ForeignKeyConstraint(['file_a_file_id', 'file_a_request_id'], relation),
        ForeignKeyConstraint(['file_b_file_id', 'file_b_request_id'], relation),
        {"schema": DB_SCHEMA})

    def __repr__(self):
        return "<Cmp Result (file='%s', req='%s')<->(file='%s', req='%s') => ('%s', '%s')>" % (
            self.file_a_file_id, self.file_a_request_id, self.file_b_file_id,
            self.file_b_request_id, self.file_a_file_b_result, self.file_b_file_a_result)

    def __str__(self):
        return self.__class__.__name__
