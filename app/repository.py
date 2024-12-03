from sqlalchemy import text, insert, select, update, delete
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, EmailStr, Field
import asyncio
from fastapi import HTTPException, Response
from src.queries.core import registration, get_all_users, add_one_pet, get_my_pets
from src.database import async_engine, sync_engine, async_session_factory

from app.schemas import *


class TaskRepository:
    @classmethod
    async def make_registration(
        cls,
        data: SRegistration
    ):
        data_dict = data.model_dump()
        try:
            user_id = await registration(**data_dict)
            return user_id
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @classmethod
    async def get_users(cls):
        users = await get_all_users()  
        return users
    
    @classmethod
    async def my_pets(cls, owner_number: str):
        pets = await get_my_pets(owner_number)
        return pets
    
    @classmethod
    async def add_pet(
        cls,
        owner_phone: str,
        pet_data: SPetAdd,
        disease_data: Optional[List[SDiseaseAdd]] = None,
        feed_data: Optional[SFeedAdd] = None
    ):
        try:
            pet_id = await(add_one_pet(owner_phone, pet_data, disease_data, feed_data))
            return pet_id
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    
    
