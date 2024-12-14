from fastapi import APIRouter,  HTTPException, Response, status, Depends, Header
import subprocess
import os
from app.repository import TaskRepository
from app.auth import authenticate_user
import random, string
from src.config import settings
from app.schemas import *
from app.auth import *
from app.dependencies import *

router = APIRouter(tags= ["Что-то делаем"])

BACKUP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backups")) 

@router.post("/restore/")
def restore_backup(request: RestoreRequest):
  
    try:
        backup_file = os.path.join(BACKUP_DIR, request.backup_file)
        backup_file_container = f"/tmp/{os.path.basename(backup_file)}"

        if not os.path.exists(backup_file):
            raise HTTPException(status_code=404, detail=f"Backup file not found: {backup_file}")

        subprocess.run(["docker", "cp", backup_file, f"db:{backup_file_container}"], check=True)

        command = [
            "docker", "exec", "db",  
            "pg_restore", "-Fc",      
            "-U", settings.DB_USER,   
            "-d", settings.DB_NAME,  
            "-c",                    
            backup_file_container
        ]

        env = os.environ.copy()
        env["PGPASSWORD"] = settings.DB_PASS
        
        subprocess.run(command, env=env, check=True)

        return {"message": "База данных успешно восстановлена из резервной копии"}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@router.post("/backup/")
def create_backup(backup_name: str = None):
    
    BACKUP_DIR = os.path.join(os.path.dirname(__file__), "../backups")
    BACKUP_DIR = os.path.abspath(BACKUP_DIR)  

    
    os.makedirs(BACKUP_DIR, exist_ok=True)

    try:
        if not backup_name:
            backup_name = f"{settings.DB_NAME}_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}.dump"
        
        backup_file_container = f"/tmp/{backup_name}"
        
        command = [
            "docker", "exec", "db",  
            "pg_dump", "-Fc",        
            "-U", settings.DB_USER,  
            "-d", settings.DB_NAME,  
            "-f", backup_file_container  
        ]
        
        env = os.environ.copy()
        env["PGPASSWORD"] = settings.DB_PASS
        
        
        subprocess.run(command, env=env, check=True)
        
        
        local_backup_path = os.path.join(BACKUP_DIR, backup_name)
        subprocess.run(["docker", "cp", f"db:{backup_file_container}", local_backup_path], check=True)

        
        return {"message": "Бэкап базы данных успешно создан", "file": local_backup_path}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")



@router.put("/promos/{promo_id}/activate")
async def activate_promo(promo_id: int, user: SUserGet = Depends(get_current_user)):
    async with async_session_factory() as session:
        async with session.begin():
            activated_on = datetime.utcnow()
            query = text("""
                UPDATE promos
                SET activated_on = :activated_on
                WHERE promo_id = :promo_id
            """)
            await session.execute(query, {"activated_on": activated_on, "promo_id": promo_id})

    return {"message": "Промокод успешно активирован", "activated_on": activated_on}


@router.get("/users/{user_id}/promos", response_model=List[SPromoGet])
async def get_user_promos(user_id: int):
    async with async_session_factory() as session:
        async with session.begin():
            query = text(
                """
                SELECT *
                FROM promos
                WHERE owner_id = :user_id
                """
            )
            result = await session.execute(query, {"user_id": user_id})
            promos = result.fetchall()
            
        if not promos:
            raise HTTPException(status_code=404, detail="Промокоды для данного пользователя не найдены")

        promo_list = [SPromoGet(**dict(row._mapping)) for row in promos]
        
        return promo_list


@router.post("/users/{user_id}/generate_promo", response_model=SPromoGet)
async def generate_promo(user_id: int):
    promo_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    valid_from = datetime.utcnow()
    valid_to = valid_from + timedelta(days=30)

    query = text("""
        INSERT INTO promos (owner_id, promo, valid_from, valid_to, type) 
        VALUES (:owner_id, :promo, :valid_from, :valid_to, :type)
        RETURNING promo_id, owner_id, activated_on, valid_from, valid_to, type, promo
    """)

    async with async_session_factory() as session:
        async with session.begin():
            result = await session.execute(query, {
                "owner_id": user_id,
                "promo": promo_code,
                "valid_from": valid_from,
                "valid_to": valid_to,
                "type": "sale"
            })
            promo_data = result.fetchone()

    if not promo_data:
        raise HTTPException(status_code=400, detail="Ошибка генерации промокода")

    return SPromoGet(
        promo_id=promo_data.promo_id,
        owner_id=promo_data.owner_id,
        activated_on=promo_data.activated_on,
        valid_from=promo_data.valid_from,
        valid_to=promo_data.valid_to,
        type=promo_data.type,
        promo=promo_data.promo
    )


@router.get("/me/")
async def get_me(user_data: SUserGet = Depends(get_current_user)):
    return user_data


@router.get("/check_admin/")
async def get_me(user_data: SUserGet = Depends(get_current_user)) -> GetRights:
    
    # db_backup_20241206011022.dump
    
    check_admin_query = text("""SELECT * from statuses WHERE user_id = :user_id""")
    async with async_session_factory() as session:
        async with session.begin():
            
            result = await session.execute(check_admin_query, {"user_id": user_data.user_id})
            data = result.fetchone()
            
            rights_dict = data._mapping
            return GetRights(**rights_dict)

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
            
            delete_diseases_query = text("DELETE FROM pets_diseases WHERE pet_id = :pet_id")
            await session.execute(delete_diseases_query, {"pet_id": pet_id})
            
            delete_feeds_query = text("DELETE FROM pets_feeds WHERE pet_id = :pet_id")
            await session.execute(delete_feeds_query, {"pet_id": pet_id})

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
