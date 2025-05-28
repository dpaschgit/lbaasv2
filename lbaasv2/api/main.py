from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import uvicorn
import os
import json

# Import controllers
# from controllers.vip_controller import router as vip_router
# from controllers.entitlement_controller import router as entitlement_router
# from controllers.transformer_controller import router as transformer_router
# from controllers.promotion_controller import router as promotion_router
# from controllers.bluecat_controller import router as bluecat_router
# from controllers.ansible_controller import router as ansible_router
# from controllers.mock_controller import router as mock_router

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

# Security scheme
security = HTTPBearer()

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    # This is a placeholder for actual authentication logic
    # In a real implementation, you would validate the JWT token
    # and return the user information
    return {"username": "test_user", "role": "user"}

# Include routers
# app.include_router(vip_router, prefix="/api/v1/vips", tags=["VIPs"])
# app.include_router(entitlement_router, prefix="/api/v1/entitlements", tags=["Entitlements"])
# app.include_router(transformer_router, prefix="/api/v1/transformers", tags=["Transformers"])
# app.include_router(promotion_router, prefix="/api/v1/promotion", tags=["Promotion"])
# app.include_router(bluecat_router, prefix="/api/v1/bluecat", tags=["Bluecat DDI"])
# app.include_router(ansible_router, prefix="/api/v1/ansible", tags=["Ansible"])
# app.include_router(mock_router, prefix="/api/v1/mock", tags=["Mock Services"])

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the LBaaS API"}

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    # Try to load from file
    openapi_path = os.path.join(os.path.dirname(__file__), "../docs/openapi_specification_updated.yaml")
    if os.path.exists(openapi_path):
        with open(openapi_path, "r") as f:
            import yaml
            app.openapi_schema = yaml.safe_load(f)
            return app.openapi_schema
    
    # Fall back to generated schema
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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
