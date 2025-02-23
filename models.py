from typing import Optional, List
from pydantic import BaseModel
from enum import Enum

class Gender(str, Enum):
    male = "Male"
    female = "Female"

class Role(str, Enum):
    admin = "admin"
    user = "User"
    student = "Student"
    teacher = "Teacher"

class User(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str]= None
    gender: Gender
    roles: List[Role]
    email: str
    phone_Number: str
