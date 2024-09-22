import sys
# для настройки баз данных
from sqlalchemy import Column, ForeignKey, Integer, String

# для определения таблицы и модели
from sqlalchemy.ext.declarative import declarative_base

# для создания отношений между таблицами
from sqlalchemy.orm import relationship

# для настроек
from sqlalchemy import create_engine

# создание экземпляра declarative_base
Base = declarative_base()

class TransistorOrm(Base):
    __tablename__ = "transistors"
    # __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    markname = Column(String)
    type_ = Column(Integer, ForeignKey('type_.id'))
    korpus = Column(Integer, ForeignKey('korpus.id'))
    descr = Column(String, nullable=True)
    amount = Column(Integer, default=0)
    path_file = Column(String, nullable=True)
    userid = Column(Integer, ForeignKey('users.id'))

    users = relationship('UserOrm', back_populates='userid')
    types = relationship("TypeOrm", back_populates='transistors')
    korpuss = relationship("KorpusOrm", back_populates='transistors')

class TypeOrm(Base):
    __tablename__ = "type_"

    id = Column(Integer, primary_key=True)
    type_name = Column(String)

    transistors = relationship("TransistorOrm", back_populates="types")


class KorpusOrm(Base):
    __tablename__ = "korpus"

    id = Column(Integer, primary_key=True)
    korpus_name = Column(String)

    transistors = relationship("TransistorOrm", back_populates="korpuss")



class UserOrm(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    status = Column(Integer, default=0)

    userid = relationship('TransistorOrm', back_populates='users')


# создает экземпляр create_engine в конце файла
engine = create_engine('sqlite:///database.db')

Base.metadata.create_all(engine)