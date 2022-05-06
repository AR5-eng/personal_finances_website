from sqlalchemy.dialects.postgresql import insert

from core.base import User
from core.db import connection


def add_user(user_name: str, user_email: str, user_hashed_password: str) -> None:
    connection.execute(insert(User).values(
        name=user_name,
        email=user_email,
        hashed_password=user_hashed_password
    ))
