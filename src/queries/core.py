from sqlalchemy import text, insert, select, update, delete
from datetime import datetime
from src.database import async_session_factory
from app.auth import *



async def get_all_users():
    async with async_session_factory() as session: 
            query = text("SELECT * FROM users")
            result = await session.execute(query)
            users_data = result.fetchall()
            users = [dict(row._mapping) for row in users_data] 
            return users


async def get_my_pets(owner_phone: str):
    async with async_session_factory() as session:
        owner_id_query = text("""SELECT user_id from users WHERE phone_number = :phone_number""")
        result = await session.execute(owner_id_query, {'phone_number': owner_phone})
        owner_id= result.scalar()
        
        if not owner_id:
            raise ValueError("Пользователь с данным номером телефона не найден.")
        
        owners_pet_query = text("""SELECT * from pets WHERE owner_id = :owner_id""")
        result = await session.execute(owners_pet_query, {'owner_id': owner_id})
        pets_data = result.fetchall()
        pets = [dict(row._mapping) for row in pets_data]
        return pets

        

async def registration(user_data, password_data):
    async with async_session_factory() as session:  
        async with session.begin():  
            try:
                mail_check_query = text("""
                    SELECT user_id FROM passwords WHERE login = :mail
                """)
                
                result = await session.execute(mail_check_query, {'mail': user_data['mail']})
                existing_user = result.scalar()

                if existing_user:
                    raise ValueError("Пользователь с такой почтой уже существует.")
                
                password_data['password'] = get_password_hash(password_data['password'])
                user_insert_query = text("""
                    INSERT INTO users (name, phone_number, mail, address, birth, sex, tabel_number, segment, function)
                    VALUES (:name, :phone_number, :mail, :address, :birth, :sex, :tabel_number, :segment, :function)
                    RETURNING user_id
                """)
                result = await session.execute(user_insert_query, user_data)
                user_id = result.scalar()

                password_insert_query = text("""
                    INSERT INTO passwords (user_id, login, password_hash)
                    VALUES (:user_id, :login, :password_hash)
                """)
                await session.execute(password_insert_query, 
                                      {'password_hash': password_data['password'],
                                       'login': user_data['mail'],
                                       'user_id': user_id})
                
                rights_inser_query = text("""INSERT INTO statuses (user_id, status_type)
                                          VALUES (:user_id, :status_type)""")
                
                await session.execute(rights_inser_query,{"user_id": user_id, "status_type": "user"} )
                await session.commit()

                print("Пользователь успешно зарегистрирован!")
                return user_id

            except Exception as e:
                print(f"Ошибка регистрации пользователя: {e}")
                raise  e
            
     
            
async def add_one_pet(owner_phone, pet_data, disease_data = None, feed_data = None):
    async with async_session_factory() as session:
        async with session.begin():
            try:
                owner_query = text("""
                    SELECT user_id FROM users WHERE phone_number = :phone_number
                """)
                result = await session.execute(owner_query, {'phone_number': owner_phone})
                owner_id = result.scalar()

                if not owner_id:
                    raise ValueError("Пользователь с данным номером телефона не найден.")

                pet_insert_query = text("""
                    INSERT INTO pets (owner_id, name, sex, animal, breed, birth, weight, sterilized)
                    VALUES (:owner_id, :name, :sex, :animal, :breed, :birth, :weight, :sterilized)
                    RETURNING pet_id
                """)
                result = await session.execute(pet_insert_query, {
                    'owner_id': owner_id,
                    'name': pet_data.name,
                    'sex': pet_data.sex.value,  
                    'animal': pet_data.animal,
                    'breed': pet_data.breed,
                    'birth': pet_data.birth,
                    'weight': pet_data.weight,
                    'sterilized': pet_data.sterilized
                })
                pet_id = result.scalar()

                if disease_data:
                    disease_insert_query = text("""
                        INSERT INTO pets_diseases (pet_id, disease_name, disease_danger)
                        VALUES (:pet_id, :disease_name, :disease_danger)
                    """)
                    for disease in disease_data:
                        if disease.disease_name:
                            await session.execute(disease_insert_query, {
                                'pet_id': pet_id,
                                'disease_name': disease.disease_name,
                                'disease_danger': disease.disease_danger
                            })
                if feed_data:
                    feed_insert_query = text("""
                        INSERT INTO pets_feeds (pet_id, feed_name, feed_type)
                        VALUES (:pet_id, :feed_name, :feed_type)
                    """)
                    if feed_data.feed_name:
                        await session.execute(feed_insert_query, {
                            'pet_id': pet_id,
                            'feed_name': feed_data.feed_name,
                            'feed_type': feed_data.feed_type.value if feed_data.feed_type else None
                        })

                return pet_id

            except Exception as e:
                print(f"Ошибка добавления питомца: {e}")
                raise