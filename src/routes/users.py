import pickle

import cloudinary

from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config
from src.entity.models import User
from src.database.db import get_db
from src.repository import users as repository_users
from src.schemas.user import UserResponse
from src.services.auth import auth_service


router = APIRouter(prefix='/users', tags=['users'])
configurating = cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True
    )
import cloudinary.uploader

@router.get('/me', response_model=UserResponse,
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    """
    The get_current_user function is a dependency that will be injected into the
        get_current_user endpoint. It uses the auth_service to retrieve the current user,
        and returns it if found.
    
    :param user: User: Get the user object from the database
    :return: A user object
    :doc-author: Trelent
    """
    return user

@router.patch('/avatar', 
              response_model=UserResponse,
              dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def update_avatar(file: UploadFile = File(), 
                           user: User = Depends(auth_service.get_current_user), 
                           db: AsyncSession = Depends(get_db)):
    
    """
    The update_avatar function updates the avatar of a user.
    
    :param file: UploadFile: Get the file from the request
    :param user: User: Get the current user from the database
    :param db: AsyncSession: Get the database session
    :return: The user object, but the swagger documentation says it returns a string
    :doc-author: Trelent
    """
    public_id = f"lection_26/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop='fill', version=res.get("version"))
    
    user = await repository_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    return user