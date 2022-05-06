import hashlib
from os import getenv
from typing import Optional
import http

from dotenv import load_dotenv
from fastapi import Cookie, FastAPI, Form
from fastapi.responses import Response, RedirectResponse

from requests.select_requests import get_user_hashed_password, check_user_email, \
    check_user_name
from requests.insert_requests import add_user

app = FastAPI()


load_dotenv()
SALT = getenv('SALT')
ACCESS_TOKEN_EXPIRE_MINUTES = getenv('ACCESS_TOKEN_EXPIRE_MINUTES')


def hash_password(password: str) -> str:
    password_with_salt = password + SALT
    hashed_password = hashlib.sha256(password_with_salt.encode()).hexdigest()
    
    return hashed_password


def check_password(email: str, password: str) -> bool:
    hashed_password_from_db = get_user_hashed_password(email)
    
    if hashed_password_from_db == 0: # Если пользователь ввел неправильный email
        return False
    else:
        hashed_password = hash_password(password)
        
        if hashed_password_from_db == hashed_password:
                return True
        else: 
            return False   
    

# Пользователь заходит в аккаунт
@app.get('/')
async def get_login_user(jwt: Optional[str] = Cookie(default=None)):
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
async def process_login_page(email: str = Form(...), password: str = Form(...)):
    is_password_right = check_password(email, password)
    
    if is_password_right == True:
        return Response('ok!', media_type='text/html')
    else:
        return RedirectResponse(url='/', status_code=http.HTTPStatus.FOUND)


@app.post('/process-signup')    
async def process_signup_page(name: str = Form(...), email: str = Form(...), password: str = Form(...)):    
    if (check_user_name(name) == False) and (check_user_email(email) == False):
        hashed_password = hash_password(password)
        add_user(name, email, hashed_password)
        
        return RedirectResponse(url='/', status_code=http.HTTPStatus.FOUND)
    else:
        return RedirectResponse(url='/signup', status_code=http.HTTPStatus.FOUND)
