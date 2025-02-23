from typing import Optional, List
from pydantic import BaseModel
from enum import Enum

class Gender(str, Enum):
    male = "Male"
    female = "Female"

class Role(str, Enum):
    student = "Student"
    admin = "admin"
    user = "User"
    teacher = "Teacher"

class User(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str]= None
    gender: Gender
    roles: List[Role]
    email: str
    phone_Number: str

class UpdateUser(BaseModel):
    role: Optional[Role]= None
    email: Optional[str]= None
    phone_Number: Optional[str]= None
