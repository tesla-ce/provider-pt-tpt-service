"""
TPTFile module
"""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from .util import DB_SCHEMA, BASE


class TPTFile(BASE):
    """
    TPTFile class
    """
    __tablename__ = 'tpt_file'

    __table_args__ = {"schema": DB_SCHEMA}

    file_id = Column(Integer, primary_key=True)
    request_id = Column(ForeignKey(DB_SCHEMA + ".tpt_request.id"), primary_key=True)
    path = Column(String, nullable=False)
    size = Column(Integer, nullable=True)

    # Add a relationship between the files and the request
    request = relationship("TPTRequest", back_populates="files")

    def __repr__(self):
        return "<File (id='%s', req='%s', path='%s')>" % (self.file_id, self.request_id, self.path)

    def __str__(self):
        return self.__class__.__name__
