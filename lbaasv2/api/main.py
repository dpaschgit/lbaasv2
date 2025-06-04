"""
LBaaS API - Windows Compatible Main File
This file includes internal dependency installation and Windows-compatible path handling
"""
import sys
import os
import subprocess
import platform

# Function to ensure dependencies are installed
def ensure_dependencies():
    required_packages = [
        "fastapi",
        "uvicorn",
        "pyyaml",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart"
    ]
    
    try:
        # Try importing key packages to check if they're installed
        import fastapi
        import uvicorn
        import yaml
        import jose
        import passlib
        print("All required packages are already installed.")
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Attempting to install required packages...")
        
        try:
            # Use subprocess to run pip install
            for package in required_packages:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print("Successfully installed all required packages.")
            return True
        except Exception as e:
            print(f"Failed to install packages: {e}")
            print("Please install the following packages manually:")
            for package in required_packages:
                print(f"  - {package}")
            return False

# Ensure dependencies are installed before proceeding
if not ensure_dependencies():
    print("Cannot continue without required dependencies.")
    sys.exit(1)

# Now import the required packages
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import uvicorn
import json
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional, Dict, List
from pydantic import BaseModel
import yaml

# --- JWT Authentication Configuration ---
SECRET_KEY = "your-secret-key-for-jwt"  # Replace with a strong, random key in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# --- User Models ---
class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool = False
    role: str = "user"
    app_ids: Optional[List[str]] = None

class UserInDB(User):
    hashed_password: str

# --- Mock User Database ---
MOCK_USERS_DB = {
    "user1": {
        "username": "user1",
        "email": "user1@example.com",
        "full_name": "User One",
        "hashed_password": pwd_context.hash("user1"),
        "disabled": False,
        "role": "user",
        "app_ids": ["APP001", "SHARED01"]
    },
    "user2": {
        "username": "user2",
        "email": "user2@example.com",
        "full_name": "User Two",
        "hashed_password": pwd_context.hash("user2"),
        "disabled": False,
        "role": "user",
        "app_ids": ["APP002"]
    },
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Admin User",
        "hashed_password": pwd_context.hash("admin"),
        "disabled": False,
        "role": "admin",
        "app_ids": ["APP001", "APP002", "APP003", "SHARED01"]
    }
}

# --- Authentication Helper Functions ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    if username in MOCK_USERS_DB:
        user_dict = MOCK_USERS_DB[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Load Balancing as a Service (LBaaS) API",
    description="API for managing Load Balancing as a Service (LBaaS) resources",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# from controllers.vip_controller import router as vip_router
# from controllers.entitlement_controller import router as entitlement_router
# from controllers.transformer_controller import router as transformer_router
# from controllers.promotion_controller import router as promotion_router
# from controllers.bluecat_controller import router as bluecat_router
# from controllers.ansible_controller import router as ansible_router
# from controllers.mock_controller import router as mock_router
# app.include_router(vip_router, prefix="/api/v1/vips", tags=["VIPs"])
# app.include_router(entitlement_router, prefix="/api/v1/entitlements", tags=["Entitlements"])
# app.include_router(transformer_router, prefix="/api/v1/transformers", tags=["Transformers"])
# app.include_router(promotion_router, prefix="/api/v1/promotion", tags=["Promotion"])
# app.include_router(bluecat_router, prefix="/api/v1/bluecat", tags=["Bluecat DDI"])
# app.include_router(ansible_router, prefix="/api/v1/ansible", tags=["Ansible"])
# app.include_router(mock_router, prefix="/api/v1/mock", tags=["Mock Services"])

# --- Authentication Endpoints ---
@app.post("/api/v1/auth/token", tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/auth/users/me", response_model=User, tags=["Authentication"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# --- Basic Endpoints ---
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the LBaaS API"}

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}

# --- Custom OpenAPI Schema ---
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try multiple possible locations for the OpenAPI spec
    possible_paths = [
        # Windows path with D: drive
        os.path.join("D:", os.sep, "MyCode", "lbaasv2", "docs", "enhanced_openapi_with_auth.yaml"),
        # Relative path from current directory
        os.path.join(current_dir, "docs", "enhanced_openapi_with_auth.yaml"),
        # One level up from current directory
        os.path.join(current_dir, "..", "docs", "enhanced_openapi_with_auth.yaml"),
        # Current directory
        os.path.join(current_dir, "enhanced_openapi_with_auth.yaml"),
    ]
    
    # Try each path
    for openapi_path in possible_paths:
        if os.path.exists(openapi_path):
            try:
                with open(openapi_path, "r") as f:
                    app.openapi_schema = yaml.safe_load(f)
                    print(f"Loaded custom OpenAPI schema from {openapi_path}")
                    return app.openapi_schema
            except Exception as e:
                print(f"Error loading custom OpenAPI schema from {openapi_path}: {e}")
    
    # If we get here, none of the paths worked
    print("OpenAPI schema file not found. Checked paths:")
    for path in possible_paths:
        print(f"  - {path}")
    
    # Fall back to generated schema
    print("Falling back to generated OpenAPI schema")
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    print(f"Starting LBaaS API on platform: {platform.system()}")
    print(f"Python version: {platform.python_version()}")
    print(f"Current directory: {os.path.abspath(os.curdir)}")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
