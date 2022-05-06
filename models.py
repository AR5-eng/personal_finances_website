from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum

from core.db import Base


class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=15), nullable=False, unique=True)
    email = Column(String(length=30), nullable=False, unique=True)
    hashed_password = Column(String(length=100), nullable=False)
    is_banned = Column(Boolean, default=False)


class Currency(Base):
    __tablename__ = 'currency'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=5), nullable=False, unique=True)


class Account(Base):
    __tablename__ = 'account'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    name = Column(String(length=30), nullable=False)
    balance = Column(Float, nullable=False)
    currency_id = Column(Integer, ForeignKey('currency.id'), nullable=False)
    
    user = relationship('User', foreign_keys=[user_id])
    currency = relationship('Currency', foreign_keys=[currency_id])


class Type(Base):
    __tablename__ = 'type'  
    
    id = Column(Integer, primary_key=True, autoincrement=True)  
    name = Column(String(length=15), nullable=False, unique=True)
    
    
class Category(Base):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True, autoincrement=True) 
    name = Column(String(length=15), nullable=False, unique=True)
    
    
class Subcategory(Base):
    __tablename__ = 'subcategory'
    
    id = Column(Integer, primary_key=True, autoincrement=True) 
    name = Column(String(length=15), nullable=False, unique=True)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    
    category = relationship('Category', foreign_keys=[category_id])


class Operation(Base):
    __tablename__ = 'operation'
    
    id = Column(Integer, primary_key=True, autoincrement=True) 
    account_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    type_id = Column(Integer, ForeignKey('type.id'), nullable=False)
    subcategory_id = Column(Integer, ForeignKey('subcategory.id'), nullable=False)
    size = Column(Float, nullable=False)
    
    account = relationship('Account', foreign_keys=[account_id])
    type = relationship('Type', foreign_keys=[type_id])
    subcategory = relationship('Subcategory', foreign_keys=[subcategory_id])
    