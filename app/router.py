from fastapi import APIRouter,  HTTPException, Response, status, Depends
from app.repository import TaskRepository
from app.auth import authenticate_user

from app.schemas import *
from app.auth import *
from app.dependencies import *

router = APIRouter(tags= ["Что-то делаем"])

@router.get("/me/")
async def get_me(user_data: SUserGet = Depends(get_current_user)):
    return user_data

@router.put("/edit_me/")
async def edit_me(data_to_update: SUserUpdate, user_data: SUserGet = Depends(get_current_user)):
    
    user_id = user_data.user_id  
    query = text("""
        UPDATE users
        SET
            name = :name,
            phone_number = :phone_number,
            mail = :mail,
            address = :address,
            birth = :birth,
            sex = :sex,
            tabel_number = :tabel_number,
            segment = :segment,
            function = :function
        WHERE user_id = :user_id
    """)
    
    update_fields = data_to_update.model_dump()
    update_fields["user_id"] = user_id
    async with async_session_factory() as session:
        async with session.begin():
            try:
                result = await session.execute(query, update_fields)
                    
                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Пользователь не найден")
                
                return {"detail": "Данные успешно обновлены"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Ошибка обновления данных: {str(e)}")
    





@router.get("/my_pets")
async def get_my_pets(pet_data: List[SPetGet] = Depends(get_current_pets)):
    return pet_data


@router.delete("/my_pets/{pet_id}")
async def delete_pet(pet_id: int, user: SUserGet = Depends(get_current_user)):

    async with async_session_factory() as session:
        async with session.begin():
            
            # Сначала удаляем связанные записи из pets_diseases и pets_feeds
            delete_diseases_query = text("DELETE FROM pets_diseases WHERE pet_id = :pet_id")
            await session.execute(delete_diseases_query, {"pet_id": pet_id})
            
            delete_feeds_query = text("DELETE FROM pets_feeds WHERE pet_id = :pet_id")
            await session.execute(delete_feeds_query, {"pet_id": pet_id})

            # Теперь удаляем сам питомца
            pet_query = text("DELETE FROM pets WHERE pet_id = :pet_id AND owner_id = :user_id")
            result = await session.execute(pet_query, {"pet_id": pet_id, "user_id": user.user_id})
    
    return {"message": "Питомец и его связанные записи успешно удалены"}



@router.post("/my_pets/add_pets")
async def add_pet(
    pet_data: SPetAdd,
    disease_data: Optional[List[SDiseaseAdd]] = None,
    feed_data: Optional[SFeedAdd] = None,
    user: SUserGet = Depends(get_current_user)
):
    pet_id = await add_pet_to_db(user.user_id, pet_data, disease_data, feed_data)
    return {"message": "Питомец успешно добавлен", "pet_id": pet_id}




@router.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}


@router.post("/login")
async def auth_user(response: Response,
                    user_data: SUserAuth):
    check = await authenticate_user(mail = user_data.mail, password= user_data.password)
    if check is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= "Неверная почта или пароль")
    access_token = create_access_token({"sub": str(check)})
    response.set_cookie(key = "users_access_token", value= access_token, httponly= True)
    return {'access_token': access_token, "refresh_token": None}



@router.post("/registration")
async def make_registration(
     data: SRegistration):
    
    user_id = await TaskRepository.make_registration(data)
    return {"message": "Регистрация успешна", "user_id": user_id} 



@router.get("/users")
async def get_users():
    users = await TaskRepository.get_users()
    return users


# @router.post("/add_pets")
# async def add_pet(
#     owner_phone: str,
#     pet_data: SPetAdd,
#     disease_data: Optional[List[SDiseaseAdd]] = None,
#     feed_data: Optional[SFeedAdd] = None
# ):
#     pet_id = await TaskRepository.add_pet(owner_phone, pet_data, disease_data , feed_data)
#     return {"message": "Питомец успешно добавлен", "pet_id": pet_id}


# @router.get("/my_pets")
# async def my_pets(
#     owner_phone: str
# ):
#     pets = await TaskRepository.my_pets(owner_phone)
#     return pets

