from dotenv import load_dotenv
load_dotenv()

from bson import ObjectId
from pkg_resources import load_entry_point
import os
from pydantic import BaseModel, Field, EmailStr

from typing import Any
from pydantic import GetJsonSchemaHandler
from pydantic_core import core_schema
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))

db = client.blog_api

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetJsonSchemaHandler
    ) -> core_schema.CoreSchema:

        def validate_from_str(value: str) -> ObjectId:
            if not ObjectId.is_valid(value):
                raise ValueError("Invalid ObjectId")
            return ObjectId(value)

        from_input_schema = core_schema.chain_schema(
            [
                core_schema.is_instance_schema(ObjectId),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=from_input_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: str(x)),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        return {"type": "string", "example": "60c72b2f9b1e8a001f8e4b22"}
        

class UserCreate(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "jdoe@example.com",
                "password": "a_strong_password"
            }
        }


class UserInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    apiKey: str = Field(...)


class UserResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: str = Field(...)
    email: EmailStr = Field(...)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "id": "60c72b2f9b1e8a001f8e4b22",
                "name": "John Doe",
                "email": "jdoe@example.com"
            }
        }
        
class TokenData(BaseModel):
    id: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "60c72b2f9b1e8a001f8e4b22"
            }
        }
        
class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "jdoe@example.com"
            }
        }
        
class NewPassword(BaseModel):
    new_password: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "new_password": "a_new_strong_password"
            }
        }
        
class BlogContentCreate(BaseModel):
    title: str = Field(...)
    content: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "My First Blog Post",
                "content": "This is the content of my first blog post."
            }
        }
        
class BlogContentResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    content: str
    author_id: str
    author_name: str
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "60c72b2f9b1e8a001f8e4b22",
                "title": "My First Blog Post",
                "content": "This is the content of my first blog post.",
                "authorId": "60c72b2f9b1e8a001f8e4b22",
                "authorName": "John Doe",
                "createdAt": "2023-10-01T12:00:00Z"
            }
        }