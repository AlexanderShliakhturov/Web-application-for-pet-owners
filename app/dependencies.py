from sqlalchemy import text

from fastapi import Request, HTTPException, status, Depends
from jose import jwt, JWTError
from datetime import datetime, timezone
from src.config import get_auth_data
from app.schemas import *
from src.database import async_session_factory




def get_token(request: Request):
    token = request.cookies.get('users_access_token')
    if not token:
        token = request.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            token = token.split(" ")[1]
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
    return token


async def get_current_user(token: str = Depends(get_token)):
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валидный!')

    expire = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен истек')

    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не найден ID пользователя')

    async with async_session_factory() as session:
        async with session.begin():
            user_query = text("SELECT * FROM users WHERE user_id = :user_id")
            result = await session.execute(user_query, {"user_id": int(user_id)})
            user = result.fetchone()
            
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
    
    user_dict = user._mapping

    return SUserGet(**user_dict)




async def get_current_pets(user: SUserGet = Depends(get_current_user)) -> List[SPetGet]:
    async with async_session_factory() as session:
        async with session.begin():
            # Запрос для получения всех питомцев пользователя
            pets_query = text("""
                SELECT pet_id, name, sex, animal, breed, birth, weight, sterilized 
                FROM pets 
                WHERE owner_id = :user_id
            """)
            result = await session.execute(pets_query, {"user_id": user.user_id})
            pets = result.fetchall()
            
            if not pets:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Питомцы не найдены')

            pet_list = []
            for pet in pets:
                pet_dict = pet._mapping
                pet_id = pet_dict["pet_id"]

                # Запрос для получения заболеваний питомца
                diseases_query = text("""
                    SELECT disease_name, disease_danger 
                    FROM pets_diseases 
                    WHERE pet_id = :pet_id
                """)
                diseases_result = await session.execute(diseases_query, {"pet_id": pet_id})
                diseases = [SDiseaseAdd(**disease._mapping) for disease in diseases_result.fetchall()]

                # Запрос для получения кормов питомца
                feeds_query = text("""
                    SELECT feed_name, feed_type 
                    FROM pets_feeds 
                    WHERE pet_id = :pet_id
                """)
                feeds_result = await session.execute(feeds_query, {"pet_id": pet_id})
                feeds = [SFeedAdd(**feed._mapping) for feed in feeds_result.fetchall()]

                # Добавление данных о питомце, болезнях и кормах в список
                pet_list.append(
                    SPetGet(
                        **pet_dict,
                        diseases=diseases if diseases else None,
                        feeds=feeds if feeds else None
                    )
                )
    
    return pet_list




async def add_pet_to_db(
    owner_id: int,
    pet_data: SPetAdd,
    disease_data: Optional[List[SDiseaseAdd]] = None,
    feed_data: Optional[SFeedAdd] = None,
) -> int:
    async with async_session_factory() as session:
        async with session.begin():
            pet_query = text("""
                INSERT INTO pets (owner_id, name, sex, animal, breed, birth, weight, sterilized)
                VALUES (:owner_id, :name, :sex, :animal, :breed, :birth, :weight, :sterilized)
                RETURNING pet_id
            """)
            result = await session.execute(pet_query, {
                "owner_id": owner_id,
                "name": pet_data.name,
                "sex": pet_data.sex.value,
                "animal": pet_data.animal,
                "breed": pet_data.breed,
                "birth": pet_data.birth,
                "weight": pet_data.weight,
                "sterilized": pet_data.sterilized
            })
            pet_id = result.scalar()

            if disease_data:
                disease_query = text("""
                    INSERT INTO pets_diseases (pet_id, disease_name, disease_danger)
                    VALUES (:pet_id, :disease_name, :disease_danger)
                """)
                for disease in disease_data:
                    await session.execute(disease_query, {
                        "pet_id": pet_id,
                        "disease_name": disease.disease_name,
                        "disease_danger": disease.disease_danger
                    })

            if feed_data:
                feed_query = text("""
                    INSERT INTO pets_feeds (pet_id, feed_name, feed_type)
                    VALUES (:pet_id, :feed_name, :feed_type)
                """)
                await session.execute(feed_query, {
                    "pet_id": pet_id,
                    "feed_name": feed_data.feed_name,
                    "feed_type": feed_data.feed_type.value if feed_data.feed_type else None
                })

    return pet_id