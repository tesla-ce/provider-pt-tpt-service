"""
TPTConcatCmpResult module
"""
from sqlalchemy import Column, Integer, Float, ForeignKeyConstraint, Enum
from tpt.commons import CmpTypeEnum, CmpResultStatusEnum
from .util import DB_SCHEMA, BASE


class TPTConcatCmpResult(BASE):
    """
    TPTConcatCmpResult class
    """
    __tablename__ = 'tpt_concat_cmp_result'

    # id = Column(Integer, primary_key=True, autoincrement=True)

    concat_a_concat_id = Column(Integer, primary_key=True)
    concat_a_request_id = Column(Integer, primary_key=True)
    concat_b_concat_id = Column(Integer, primary_key=True)
    concat_b_request_id = Column(Integer, primary_key=True)
    concat_a_concat_b_result = Column(Float, nullable=False)
    concat_b_concat_a_result = Column(Float, nullable=False)

    type = Column(Enum(CmpTypeEnum, native_enum=False), nullable=False, default=CmpTypeEnum.TEXT)

    status = Column(Enum(CmpResultStatusEnum, native_enum=False), nullable=False,
                    default=CmpResultStatusEnum.PENDING)

    relation = [DB_SCHEMA + '.tpt_concat.concat_id', DB_SCHEMA + '.tpt_concat.request_id']
    __table_args__ = (
        ForeignKeyConstraint(['concat_a_concat_id', 'concat_a_request_id'], relation),
        ForeignKeyConstraint(['concat_b_concat_id', 'concat_b_request_id'], relation),
        {"schema": DB_SCHEMA})

    def __repr__(self):
        return "<Cmp Result (concat='%s', req='%s')<->(concat='%s', req='%s') => ('%s', '%s')>" % (
            self.concat_a_concat_id, self.concat_a_request_id, self.concat_b_concat_id,
            self.concat_b_request_id, self.concat_a_concat_b_result, self.concat_b_concat_a_result)

    def __str__(self):
        return self.__class__.__name__
