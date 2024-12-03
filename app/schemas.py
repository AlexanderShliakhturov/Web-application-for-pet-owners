from datetime import datetime, date 
from typing import Optional, List, Dict
from pydantic import BaseModel, ValidationError, EmailStr, Field, field_validator
from enum import Enum
import re


#Класс для поля sex, которое может быть либо male либо female 
class SexEnum(str, Enum):
    male = "male"
    female = "female"
    
class FeedEnum(str, Enum):
    wet = "Влажный"
    dry = "Сухой"

class SDiseaseAdd(BaseModel):
    disease_name: Optional[str] = Field(None, min_length = 1, max_length=50)
    disease_danger: Optional[int] = Field(None)
    
class SFeedAdd(BaseModel):
    feed_name: Optional[str] = Field(None, min_length = 1, max_length=50)
    feed_type: Optional[FeedEnum] = Field(None)

#дописал pet_id
class SPetGet(BaseModel):
    pet_id: int
    name: str = Field(..., min_length=1, max_length=100)
    sex: SexEnum = Field(..., description="Пол: male или female")
    animal: str = Field(..., max_length=50)
    breed: Optional[str] = Field(..., max_length=50)
    birth: date
    weight: int
    sterilized: bool
    
    diseases: Optional[List[SDiseaseAdd]] = Field(None)
    feeds: Optional[List[SFeedAdd]] = Field(None)

    
class SUserUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., min_length=5, max_length=20)
    mail: EmailStr
    address: Optional[str] = Field(...,min_length= 5, max_length=200)
    birth: date
    sex: SexEnum = Field(..., description="Пол: male или female")
    tabel_number: Optional[int]
    segment: Optional[str] = Field(..., min_length= 1, max_length=50)
    function: Optional[str] = Field(..., min_length= 1, max_length=50)
    
class SPetUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    sex: SexEnum = Field(..., description="Пол: male или female")
    animal: str = Field(...,min_length=1, max_length=50)
    breed: Optional[str] = Field(..., min_length=1, max_length=50)
    birth: date
    weight: int
    sterilized: bool
    
    @field_validator("birth")
    @classmethod
    def validate_birth(cls, values: date):
        if values and values >= datetime.now().date():
            raise ValueError('Дата рождения должна быть в прошлом')
        return values


class SUserGet(BaseModel):
    user_id: int
    name: str
    phone_number: str
    mail: EmailStr
    address: str
    birth: date
    sex: SexEnum
    tabel_number: int
    segment: str
    function: str


class SUserAdd(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., min_length=5, max_length=20)
    mail: EmailStr
    address: Optional[str] = Field(...,min_length= 5, max_length=200)
    birth: date
    sex: SexEnum = Field(..., description="Пол: male или female")
    tabel_number: Optional[int]
    segment: Optional[str] = Field(..., min_length= 1, max_length=50)
    function: Optional[str] = Field(..., min_length= 1, max_length=50)
    
    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, values: str) -> str:
        if not re.match(r'^\+\d{1,15}$', values):
            raise ValueError('Номер телефона должен начинаться с "+" и содержать от 1 до 15 цифр')
        return values

    @field_validator("birth")
    @classmethod
    def validate_birth(cls, values: date):
        if values and values >= datetime.now().date():
            raise ValueError('Дата рождения должна быть в прошлом')
        return values
    

    
class SPetAdd(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    sex: SexEnum = Field(..., description="Пол: male или female")
    animal: str = Field(...,min_length=1, max_length=50)
    breed: Optional[str] = Field(..., min_length=1, max_length=50)
    birth: date
    weight: int
    sterilized: bool
    
    @field_validator("birth")
    @classmethod
    def validate_birth(cls, values: date):
        if values and values >= datetime.now().date():
            raise ValueError('Дата рождения должна быть в прошлом')
        return values
    

class SPasswordAdd(BaseModel):
    password: str = Field(..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")

class SRegistration(BaseModel):
    user_data: SUserAdd
    password_data: SPasswordAdd
  
class SUserAuth(BaseModel):
    mail: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")
    
 