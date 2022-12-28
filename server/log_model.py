# coding: utf-8
from sqlalchemy import Column, Float, ForeignKey, Integer, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class LogEntry(Base):
    __tablename__ = "Logs"

    id = Column(Integer, primary_key=True)
    Timestamp = Column(Text, nullable=False)
    Level = Column(Text)
    RenderedMessage = Column(Text)
    Properties = Column(Text)
