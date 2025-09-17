from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.api.routes import auth, users, doctors
from app.schemas.user import ErrorResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

app = FastAPI(title="FastAPI Odoo Auth Wrapper")

# Handle validation errors (e.g., request data validation)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(code=422, message="Validation error", details=exc.errors()).model_dump()
    )

# Handle value errors (your business logic errors)
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(code=400, message=str(exc)).model_dump()
    )

# Handle HTTP exceptions (from dependencies like auth)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(code=exc.status_code, message=exc.detail).model_dump()
    )

# Handle all other unexpected errors
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(code=500, message="Internal server error").model_dump()
    )

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://umc-portal.sarahurowoli.xyz"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(doctors.router, prefix="/api")