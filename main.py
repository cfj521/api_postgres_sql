from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
from database import get_db
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from urllib.parse import unquote
import base64
import json

app = FastAPI(title="PostgreSQL API")

# 解密SQL语句
def decrypt_sql(encrypted_sql: str) -> str:
    """解密SQL语句"""
    try:
        return base64.b64decode(encrypted_sql.encode()).decode()
    except Exception as e:
        raise ValueError(f"Invalid base64 encoding: {str(e)}")

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

# SQL请求模型
class SQLRequest(BaseModel):
    query: str
    params: Dict[str, Any] = {}

# 添加 GET 方法的端点
@app.get("/sql")
async def execute_sql_get(query: str, db: Session = Depends(get_db)):
    try:
        # URL 解码
        decoded_query = unquote(query)
        
        # 解密SQL语句
        sql_query = decrypt_sql(decoded_query)
        
        # 执行SQL查询
        result = db.execute(text(sql_query))
        
        # 如果是SELECT查询，返回结果
        if sql_query.strip().upper().startswith('SELECT'):
            columns = result.keys()
            rows = result.fetchall()
            results = [dict(zip(columns, row)) for row in rows]
            return {
                "status": "success",
                "data": results
            }
        else:
            # 对于非SELECT查询，提交事务并返回影响的行数
            db.commit()
            return {
                "status": "success",
                "message": "Query executed successfully",
                "affected_rows": result.rowcount
            }
            
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Decryption failed: {str(e)}"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"SQL execution failed: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
