import logging

from sqlalchemy import select

from core.base import User
from core.db import connection


def get_user_hashed_password(user_email: str) -> str:
    # По email пользователя получаю хэшированный пароль из таблицы User
    select_users_hashed_password = connection.execute(select(User.hashed_password). \
        where((User.email == user_email)))
    
    list_users_hashed_passwords = select_users_hashed_password.fetchall().copy()
    
    if list_users_hashed_passwords:
        return list_users_hashed_passwords[0][0]
    else:
        return 0


def check_user_email(user_email: str) -> bool:
    # Проверяю есть ли пользователь с данным user_email
    select_users_id = connection.execute(select(User.hashed_password). \
        where((User.email == user_email)))
    
    list_users_id = select_users_id.fetchall().copy()
    
    if list_users_id:
        return True
    else:
        return False


def check_user_name(user_name: str) -> bool:
    # Проверяю есть ли пользователь с данным user_name
    select_users_id = connection.execute(select(User.hashed_password). \
        where((User.name == user_name)))
    
    list_users_id = select_users_id.fetchall().copy()
    
    if list_users_id:
        return True
    else:
        return False
