from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Boolean,
    MetaData,
    PrimaryKeyConstraint,
    String,
    Table,
    text,
    DateTime
)



class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement= True)
    name = Column(String)
    phone_number = Column(String, unique= True)
    mail = Column(String, unique= True)
    address = Column(String)
    birth = Column(DateTime)
    sex = Column(String)
    tabel_number = Column(Integer, unique= True)
    segment = Column(String)
    function = Column(String)

    pets = relationship('Pet', back_populates='owner')
    statuses = relationship('Status', back_populates='user')
    password = relationship('Password', back_populates='user', uselist=False)
    promos = relationship('Promo', back_populates='owner')


class Pet(Base):
    __tablename__ = 'pets'

    pet_id = Column(Integer, primary_key=True, autoincrement= True)
    name = Column(String)
    sex = Column(String)
    owner_id = Column(Integer, ForeignKey('users.user_id'))
    animal = Column(String)
    breed = Column(String)
    birth = Column(DateTime)
    weight = Column(Integer)
    sterilized = Column(Boolean)

    owner = relationship('User', back_populates='pets')
    diseases = relationship('PetDisease', back_populates='pet')
    feeds = relationship('PetFeed', back_populates='pet')


class Password(Base):
    __tablename__ = 'passwords'

    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True, autoincrement= True)
    login = Column(String, unique= True)
    password_hash = Column(String, unique=True)

    user = relationship('User', back_populates='password')


class PetFeed(Base):
    __tablename__ = 'pets_feeds'

    pet_id = Column(Integer, ForeignKey('pets.pet_id'), primary_key=True, autoincrement= True)
    
    feed_name = Column(String)   
    feed_type = Column(String)

    pet = relationship('Pet', back_populates='feeds')


class Promo(Base):
    __tablename__ = 'promos'

    owner_id = Column(Integer, ForeignKey('users.user_id'))
    promo_id = Column(Integer, primary_key=True, autoincrement= True)
    activated_on = Column(DateTime)
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)
    type = Column(String)
    promo = Column(String, unique= True)  
 
    owner = relationship('User', back_populates='promos')


class Status(Base):
    __tablename__ = 'statuses'

    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True, autoincrement= True)
    status_type = Column(String)

    user = relationship('User', back_populates='statuses')


class PetDisease(Base):
    __tablename__ = 'pets_diseases'
    
    incident_id = Column(Integer, primary_key= True, autoincrement=True)
    pet_id = Column(Integer, ForeignKey('pets.pet_id'))
    disease_name = Column(String)
    disease_danger = Column(Integer)

    pet = relationship('Pet', back_populates='diseases')
