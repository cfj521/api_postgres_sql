from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import models
from database import engine, get_db
from pydantic import BaseModel
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PostgreSQL API")

# 全局异常处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "path": request.url.path
        }
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Database Error",
            "detail": str(exc),
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "path": request.url.path
        }
    )

# Pydantic模型
class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

# API路由
@app.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = models.User(email=user.email, username=user.username)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create user: {str(e)}"
        )

@app.get("/users/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        users = db.query(models.User).offset(skip).limit(limit).all()
        return users
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch users: {str(e)}"
        )

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if db_user is None:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found"
            )
        return db_user
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch user: {str(e)}"
        )

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if db_user is None:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found"
            )
        
        db_user.email = user.email
        db_user.username = user.username
        
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update user: {str(e)}"
        )

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if db_user is None:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found"
            )
        
        db.delete(db_user)
        db.commit()
        return {"message": "User deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to delete user: {str(e)}"
        ) 