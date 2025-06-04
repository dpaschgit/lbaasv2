"""
LBaaS API - Windows Compatible Main File with Enhanced OpenAPI Debug
This file includes internal dependency installation, Windows-compatible path handling,
and detailed debugging for OpenAPI specification loading
"""
import sys
import os
import subprocess
import platform
import traceback

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
from fastapi import FastAPI, Depends, HTTPException, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
import uvicorn
import json
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional, Dict, List
from pydantic import BaseModel
import yaml

# --- JWT Authentication Configuration ---
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-for-jwt")
ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

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

# --- OpenAPI Debug Endpoint ---
@app.get("/debug/openapi", tags=["Debug"])
async def debug_openapi():
    """Debug endpoint to check OpenAPI specification loading"""
    debug_info = {
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "current_directory": os.path.abspath(os.curdir),
        "openapi_paths_checked": [],
        "openapi_file_found": False,
        "openapi_file_path": None,
        "openapi_file_size": None,
        "openapi_load_success": False,
        "openapi_error": None,
        "environment_variables": {
            "OPENAPI_PATH": os.environ.get("OPENAPI_PATH", "Not set")
        }
    }
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try multiple possible locations for the OpenAPI spec
    possible_paths = [
        # Environment variable path
        os.environ.get("OPENAPI_PATH"),
        # Windows path with D: drive
        os.path.join("D:", os.sep, "MyCode", "lbaasv2", "docs", "enhanced_openapi_with_auth.yaml"),
        # Relative path from current directory
        os.path.join(current_dir, "docs", "enhanced_openapi_with_auth.yaml"),
        # One level up from current directory
        os.path.join(current_dir, "..", "docs", "enhanced_openapi_with_auth.yaml"),
        # Current directory
        os.path.join(current_dir, "enhanced_openapi_with_auth.yaml"),
        # Docker volume mount path
        "/app/docs/enhanced_openapi_with_auth.yaml",
    ]
    
    # Filter out None values
    possible_paths = [p for p in possible_paths if p]
    
    # Try each path
    for openapi_path in possible_paths:
        path_info = {
            "path": openapi_path,
            "exists": os.path.exists(openapi_path),
            "is_file": os.path.isfile(openapi_path) if os.path.exists(openapi_path) else False,
            "size": os.path.getsize(openapi_path) if os.path.exists(openapi_path) and os.path.isfile(openapi_path) else None,
            "readable": os.access(openapi_path, os.R_OK) if os.path.exists(openapi_path) else False
        }
        debug_info["openapi_paths_checked"].append(path_info)
        
        if path_info["exists"] and path_info["is_file"] and path_info["readable"]:
            debug_info["openapi_file_found"] = True
            debug_info["openapi_file_path"] = openapi_path
            debug_info["openapi_file_size"] = path_info["size"]
            
            try:
                with open(openapi_path, "r") as f:
                    content = f.read()
                    yaml_content = yaml.safe_load(content)
                    debug_info["openapi_load_success"] = True
                    debug_info["openapi_content_preview"] = {
                        "info": yaml_content.get("info", {}),
                        "paths_count": len(yaml_content.get("paths", {})),
                        "components_count": len(yaml_content.get("components", {}))
                    }
                    break
            except Exception as e:
                debug_info["openapi_error"] = {
                    "message": str(e),
                    "traceback": traceback.format_exc()
                }
    
    return debug_info

# --- Metrics Endpoint for Prometheus ---
@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Simple metrics endpoint for Prometheus monitoring"""
    # This is a basic implementation - in a real app, you'd use a proper metrics library
    return {
        "api_status": "healthy",
        "uptime_seconds": 0,  # You'd calculate this from app start time
        "request_count": 0,   # You'd increment this for each request
        "error_count": 0      # You'd increment this for each error
    }

# --- Custom OpenAPI Schema ---
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    # Check for environment variable first
    openapi_path = os.environ.get("OPENAPI_PATH")
    if openapi_path and os.path.exists(openapi_path):
        try:
            with open(openapi_path, "r") as f:
                app.openapi_schema = yaml.safe_load(f)
                print(f"Loaded custom OpenAPI schema from environment variable path: {openapi_path}")
                return app.openapi_schema
        except Exception as e:
            print(f"Error loading custom OpenAPI schema from environment variable path: {e}")
    
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
        # Docker volume mount path
        "/app/docs/enhanced_openapi_with_auth.yaml",
    ]
    
    # Try each path
    for openapi_path in possible_paths:
        if os.path.exists(openapi_path):
            try:
                with open(openapi_path, "r") as f:
                    content = f.read()
                    app.openapi_schema = yaml.safe_load(content)
                    print(f"Loaded custom OpenAPI schema from {openapi_path}")
                    print(f"Schema info: {app.openapi_schema.get('info', {}).get('title')}")
                    return app.openapi_schema
            except Exception as e:
                print(f"Error loading custom OpenAPI schema from {openapi_path}: {e}")
                print(traceback.format_exc())
    
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

# Override the default OpenAPI schema with our custom one
app.openapi = custom_openapi

# --- Error handling middleware ---
@app.middleware("http")
async def add_error_handling(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print(f"Error handling request {request.url}: {e}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
        )

if __name__ == "__main__":
    print(f"Starting LBaaS API on platform: {platform.system()}")
    print(f"Python version: {platform.python_version()}")
    print(f"Current directory: {os.path.abspath(os.curdir)}")
    
    # Print environment variables
    print("Environment variables:")
    for key, value in os.environ.items():
        if key.startswith("OPENAPI") or key.startswith("JWT"):
            print(f"  {key}: {value}")
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
