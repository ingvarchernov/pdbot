import random

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = "sqlite:///userdb.db"
engine = create_engine(DATABASE_URL)

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    userid = Column(Integer)
    usernames = Column(String)
    firstname = Column(String)
    group_id = Column(Integer, ForeignKey('groups.groupid'))


class Countclick(Base):
    __tablename__ = 'countclick'

    id = Column(Integer, primary_key=True, index=True)
    user_ids = Column(Integer, ForeignKey('users.userid'))
    username = Column(String, index=True)
    first_name = Column(String)
    group_id = Column(Integer, ForeignKey('groups.groupid'))
    amountclick = Column(Integer, default=0)


class Groups(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, index=True)
    groupid = Column(Integer)


Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
