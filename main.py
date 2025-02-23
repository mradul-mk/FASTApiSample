from fastapi import FastAPI, HTTPException
# Defined by Us
from models import User, UpdateUser, Role

# imports for MongoDB database connection
from motor.motor_asyncio import AsyncIOMotorClient
# import for fastAPI lifespan
from contextlib import asynccontextmanager

from typing import List

# import for data validation
from pydantic import BaseModel


# =====================================================
# Define a LifeSpan
# MONGO DB connection URI
Mongo_URI = "mongodb://localhost:27017"

async def startup_db_client(app):
    app.mongo_client =AsyncIOMotorClient(Mongo_URI)
    app.mongodb = app.mongo_client.get_database("college")
    print("MongoDB Connected")

async def shutdown_db_client(app):
    app.mongo_client.close()
    print("Mongo Db disconnected")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_db_client(app)
    yield
    await shutdown_db_client(app)

# =====================================================


# =====================================================
# Create Fast API object and CRUD APIs

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    print("In Read root")
    return {"Data": "Hello World"}

@app.post("/v1/create-user", response_model=User)
async def insert_user(user: User):
    result = await app.mongodb["Users"].insert_one(user.dict())
    inserted_user = await app.mongodb["Users"].find_one({"_id": result.inserted_id})
    return inserted_user

@app.get("/v1/get_all_users", response_model=List[User])
async def get_all_users():
    users = await app.mongodb["Users"].find().to_list(None)
    return users

@app.get("/v1/get_user/{email}", response_model=User)
async def get_user(email: str):
    user = await app.mongodb["Users"].find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@app.put("/v1/update_user/{email}", response_model=User)
async def update_user(email: str, update_data: UpdateUser):

    existing_user = await app.mongodb["Users"].find_one({"email":email})
    if not existing_user:
        raise HTTPException(status_code=404, detail="user not found")

    update_dict = update_data.model_dump(exclude_unset=True)

    if update_data.role is not None:
        current_roles = existing_user["roles"]
        new_role = update_data.role

        if new_role not in current_roles:
            update_result = await app.mongodb["Users"].update_one(
                {"email":email},
                {"$push": {"roles": new_role}}
            )
            if update_result.modified_count == 0:
                raise HTTPException(status_code=500, detail="Failed to append role")
        
        update_dict.pop("role", None)
    

    if update_dict:

        updated_result = await app.mongodb["Users"].update_one({"email":email}, 
                                                        {
                                                            "$set": update_dict
                                                        })
        if updated_result.modified_count == 0 and update_result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found or no update required")

    updated_email = update_data.email if update_data.email else email
    updated_user = await app.mongodb["Users"].find_one({"email":updated_email})
    if not updated_user:
        raise HTTPException(status_code=404, detail="Updated user not found")

    return updated_user


@app.delete("/v1/delete_user/{email}", response_model=dict)
async def delete_user(email: str):
    delete_result = await app.mongodb["Users"].delete_one({"email": email})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "Successfully deleted User"}