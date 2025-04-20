from passlib.context import CryptContext
from pydantic import EmailStr
from src.database import async_engine, sync_engine, async_session_factory
from sqlalchemy import text, insert, select, update, delete
from jose import jwt
from datetime import datetime, timedelta, timezone
from src.config import get_auth_data
from src.redis_client import store_token, get_redis_token, invalidate_token


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire})
    auth_data = get_auth_data()
    encode_jwt = jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])
    
    # Store token in Redis
    await store_token(str(data['sub']), encode_jwt)
    return encode_jwt


async def verify_token(token: str, user_id: str) -> bool:
    """Verify if token exists in Redis and matches"""
    stored_token = await get_redis_token(user_id)
    return stored_token == token


async def authenticate_user(mail: EmailStr, password: str):
    async with async_session_factory() as session:  
        async with session.begin():
            mail_check_query = text("""
                            SELECT user_id FROM passwords WHERE login = :mail
                        """)
            result = await session.execute(mail_check_query, {'mail': mail})
            user_id = result.scalar()
            
            password_check_query = text("""
                                        SELECT password_hash from passwords WHERE user_id = :user_id""")
            result = await session.execute(password_check_query, {"user_id": user_id})
            password_hash = result.scalar()
                
            if (user_id == None) or verify_password(plain_password=password, hashed_password=password_hash) is False:
                return None
            return user_id