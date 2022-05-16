import hashlib
from os import getenv
from typing import Optional
import http
import time

import jwt
from dotenv import load_dotenv
from fastapi import Cookie, FastAPI, Form
from fastapi.responses import Response, RedirectResponse

from requests.select_requests import get_user_hashed_password, check_user_email, \
    check_user_name, get_info_about_user
from requests.insert_requests import add_user


load_dotenv()
SECRET_KEY = getenv('SECRET_KEY')
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

app = FastAPI()


def hash_password(password: str) -> str:
    # Хеширует пароль
    password_with_secret_key = password + SECRET_KEY
    hashed_password = hashlib.sha256(password_with_secret_key.encode()).hexdigest()
    
    return hashed_password


def check_password(email: str, password: str) -> bool:
    # Сверяет пароль пользователя с тем, что лежит в базе
    hashed_password_from_db = get_user_hashed_password(email)
    
    if hashed_password_from_db == 0: # Если пользователь ввел неправильный email
        return False
    else:
        hashed_password = hash_password(password)
        
        if hashed_password_from_db == hashed_password:
                return True
        else: 
            return False   


def create_jwt(email: str) -> str:
    # Создает jwt-токен
    info_about_user = get_info_about_user(email)
    payload = {'user_id': info_about_user[0],
               'user_name': info_about_user[1],
               'expiry': time.time() + ACCESS_TOKEN_EXPIRE_MINUTES*60}

    return jwt.encode(payload=payload, key=SECRET_KEY, algorithm='HS256')


def read_jwt(jwtoken: str) -> dict:
    # Декодирует jwt-токен
    unsigned_token = jwt.decode(jwt=jwtoken, key=SECRET_KEY, 
                                algorithms='HS256')
    
    return unsigned_token


def get_login_page_if_expired() -> RedirectResponse:
    # Перенаправляет на страницу login
    response = RedirectResponse(url='/', status_code=http.HTTPStatus.FOUND)
    response.delete_cookie(key='jwt')
        
    return response

    
# Пользователь заходит в аккаунт
@app.get('/')
async def get_login_user(jwt: Optional[str] = Cookie(default=None)):    
    if jwt: # Если токен присутствует
        unsigned_token = read_jwt(jwt)
        
        if unsigned_token['expiry'] < time.time(): # Если время токена истекло
            return get_login_page_if_expired()
        else: # Если время токена не истекло, открывает текущую страницу 
            return RedirectResponse(url=f"/home/{unsigned_token['user_id']}", 
                                    status_code=http.HTTPStatus.FOUND)
    else:
        with open('templates/login.html', 'r') as f:
            login_page = f.read()
        
        return Response(login_page, media_type='text/html')
    
    
# Страница регистрации
@app.get('/signup')
async def get_signup_user():
    with open('templates/signup.html', 'r') as f:
        signup_page = f.read()
        
    return Response(signup_page, media_type='text/html')


# Обработка информации после страницы login
@app.post('/process-login')
async def process_login_page(email: str = Form(...), 
                             password: str = Form(...)):
    is_password_right = check_password(email, password)
    
    if is_password_right == True:
        jwtoken = create_jwt(email)
        response = RedirectResponse(url=f"/home/{read_jwt(jwtoken)['user_id']}", 
                                    status_code=http.HTTPStatus.FOUND)
        response.set_cookie(key='jwt', value=jwtoken)
        
        return response
    else:
        return RedirectResponse(url='/', status_code=http.HTTPStatus.FOUND)


# Обработка информации после страницы регистрации
@app.post('/process-signup')    
async def process_signup_page(name: str = Form(...), email: str = Form(...), 
                              password: str = Form(...)):    
    if (check_user_name(name) == False) and (check_user_email(email) == False):
        hashed_password = hash_password(password)
        add_user(name, email, hashed_password)
        
        return RedirectResponse(url='/', status_code=http.HTTPStatus.FOUND)
    else:
        return RedirectResponse(url='/signup', 
                                status_code=http.HTTPStatus.FOUND)
    
    
@app.get('/home/{user_id}')
async def get_home_page(user_id: int, jwt: Optional[str] = Cookie(default=None)):
    unsigned_token = read_jwt(jwt)
    
    if jwt:
        if unsigned_token['expiry'] < time.time(): # Если время токена истекло
            return get_login_page_if_expired()
        else:
            return {'user_id': user_id}
    else: 
        return RedirectResponse(url='/', status_code=http.HTTPStatus.FOUND)
