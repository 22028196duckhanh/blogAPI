from api.oath2 import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas import BlogContentCreate, BlogContentResponse, db, UserInDB
from datetime import datetime
from bson import ObjectId

router = APIRouter(
    prefix="/blog",
    tags=["Blog Content"]
)

@router.post("/create", response_description="Create a new blog content", response_model=BlogContentResponse)
async def create_blog(blog_content: BlogContentCreate, current_user: UserInDB = Depends(get_current_user)):
    try:
        blog_content_data = blog_content.dict()
        blog_content_data["author_id"] = str(current_user.id)
        print(f"Current user ID: {blog_content_data['author_id']}")
        blog_content_data["author_name"] = current_user.name
        blog_content_data["created_at"] = datetime.utcnow()
        
        new_blog = await db["blogs"].insert_one(blog_content_data)
        print(f"New blog created with ID: {new_blog.inserted_id}")
        created_blog = await db["blogs"].find_one({"_id": new_blog.inserted_id})
        return created_blog
    except Exception as e:
        print(f"Error creating blog content: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.get("", response_description="Get blog content", response_model=list[BlogContentResponse])
async def get_blogs(limit: int = 5, order_by: str = "created_at", order: str = "desc"):
    try:
        cursor = db["blogs"].find().sort(order_by, -1 if order == "desc" else 1).limit(limit)
        blogs = [blog async for blog in cursor]
        return blogs
    except Exception as e:
        print(f"Error fetching blog content: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.get("/{blog_id}", response_description="Get a specific blog content", response_model=BlogContentResponse)
async def get_blog(blog_id: str):
    try:
        blog = await db["blogs"].find_one({"_id": ObjectId(blog_id)})

        if not blog:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {blog_id} not found")
        return blog
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(f"Error fetching blog {blog_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.put("/{blog_id}", response_description="Update a blog content", response_model=BlogContentResponse)
async def update_blog(blog_id: str, blog_content: BlogContentCreate, current_user: UserInDB = Depends(get_current_user)):
    try:
        exist_blog = await db["blogs"].find_one({"_id": ObjectId(blog_id)})
        if not exist_blog:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {blog_id} not found")

        if exist_blog["author_id"] != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update this blog")

        update_data = blog_content.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        updated_result = await db["blogs"].update_one(
            {"_id":  ObjectId(blog_id), "author_id": str(current_user.id)},
            {"$set": update_data}
        )
        
        updated_blog = await db["blogs"].find_one({"_id": ObjectId(blog_id)})
        return updated_blog

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(f"Error updating blog {blog_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog(blog_id: str, current_user: UserInDB = Depends(get_current_user)):
    try:       
        exist_blog = await db["blogs"].find_one({"_id": ObjectId(blog_id)})
        if not exist_blog:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

        if exist_blog["author_id"] != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this blog")

        delete_result = await db["blogs"].delete_one({"_id": ObjectId(blog_id), "author_id": str(current_user.id)})

        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found or you do not have permission")

        return HTTPException(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(f"Error deleting blog {blog_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")