# LBaaS API Rebuild Guide

## Introduction

This comprehensive guide provides step-by-step instructions for rebuilding the Load Balancing as a Service (LBaaS) API system from scratch. It is designed for both AI assistants and human developers to follow, ensuring a complete and accurate reconstruction of the system.

## Prerequisites

### Technical Requirements

1. **Development Environment**
   - Docker and Docker Compose
   - Kubernetes cluster (for production deployment)
   - Python 3.11+
   - Git

2. **Required Knowledge**
   - RESTful API design and implementation
   - FastAPI framework
   - MongoDB database
   - Docker containerization
   - Kubernetes orchestration
   - Load balancer concepts (F5 BIG-IP, AVI Networks, NGINX)
   - Integration patterns

3. **External Systems Access**
   - ServiceNow CMDB (or mock)
   - Bluecat DDI (or mock)
   - F5 BIG-IP with AS3 extension
   - AVI Networks controller
   - Certificate Authority

## Project Structure

```
lbaasv2/
├── api/                      # API layer
│   ├── controllers/          # API endpoint controllers
│   ├── models/               # API data models
│   ├── middleware/           # API middleware
│   ├── utils/                # Utility functions
│   └── main.py               # FastAPI application entry point
├── business/                 # Business logic layer
│   ├── services/             # Business services
│   ├── models/               # Business models
│   └── utils/                # Utility functions
├── integration/              # Integration layer
│   ├── cmdb/                 # ServiceNow CMDB integration
│   ├── f5/                   # F5 AS3 integration
│   ├── avi/                  # AVI Networks integration
│   ├── nginx/                # NGINX integration
│   ├── bluecat/              # Bluecat DDI integration
│   └── cert/                 # Certificate Authority integration
├── docker/                   # Docker configuration
│   ├── api/                  # API service Dockerfile and requirements
│   ├── business/             # Business service Dockerfile and requirements
│   ├── integration/          # Integration service Dockerfile and requirements
│   ├── mock/                 # Mock services Dockerfile and requirements
│   ├── ansible/              # Ansible service Dockerfile and requirements
│   └── monitoring/           # Monitoring service Dockerfile and requirements
├── ansible/                  # Ansible playbooks
│   ├── playbooks/            # Ansible playbooks
│   └── roles/                # Ansible roles
├── kubernetes/               # Kubernetes manifests
│   ├── api/                  # API service manifests
│   ├── business/             # Business service manifests
│   ├── integration/          # Integration service manifests
│   ├── database/             # Database manifests
│   ├── cache/                # Cache manifests
│   └── monitoring/           # Monitoring manifests
├── docs/                     # Documentation
│   ├── api_design.md         # API design documentation
│   ├── data_models_architecture.md # Data models and architecture documentation
│   ├── enhanced_data_models_architecture.md # Enhanced data models and architecture
│   ├── openapi_specification.yaml # OpenAPI specification
│   ├── enhanced_openapi_specification.yaml # Enhanced OpenAPI specification
│   ├── f5_avi_api_research.md # F5 AS3 and AVI API research
│   ├── competitive_analysis.md # Competitive analysis
│   └── windows_setup_guide.md # Windows setup guide
├── docker-compose.yml        # Docker Compose configuration
├── docker-compose-windows.yml # Windows-compatible Docker Compose configuration
└── README.md                 # Project README
```

## Step 1: Set Up Development Environment

### 1.1 Clone Repository Structure

Create the basic directory structure:

```bash
mkdir -p lbaasv2/{api/{controllers,models,middleware,utils},business/{services,models,utils},integration/{cmdb,f5,avi,nginx,bluecat,cert},docker/{api,business,integration,mock,ansible,monitoring},ansible/{playbooks,roles},kubernetes/{api,business,integration,database,cache,monitoring},docs}
```

### 1.2 Create README.md

Create a README.md file in the root directory with project overview, setup instructions, and usage guidelines. Reference the `/docs/README.md` file for content.

### 1.3 Set Up Docker Environment

1. Create Docker Compose files:
   - `docker-compose.yml` for Linux/Mac environments
   - `docker-compose-windows.yml` for Windows environments

2. Create Dockerfiles for each service:
   - API service: `/docker/api/Dockerfile`
   - Business service: `/docker/business/Dockerfile`
   - Integration service: `/docker/integration/Dockerfile`
   - Mock services: `/docker/mock/Dockerfile`
   - Ansible service: `/docker/ansible/Dockerfile`
   - Monitoring service: `/docker/monitoring/Dockerfile`

3. Create requirements.txt files for each service:
   - API service: `/docker/api/requirements.txt`
   - Business service: `/docker/business/requirements.txt`
   - Integration service: `/docker/integration/requirements.txt`
   - Mock services: `/docker/mock/requirements.txt`
   - Ansible service: `/docker/ansible/requirements.txt`

## Step 2: Implement API Layer

### 2.1 Create Data Models

Create the following data models in `/api/models/`:

1. **VIP Models**
   - `vip.py`: VipBase, VipCreate, VipUpdate, VipResponse, VipSummary
   - `monitor.py`: Monitor model
   - `persistence.py`: Persistence model
   - `pool.py`: PoolMember model

2. **Entitlement Models**
   - `entitlement.py`: EntitlementVerificationRequest, EntitlementVerificationResponse, EntitlementRecord

3. **Change Management Models**
   - `change.py`: ChangeRequest, ChangeVerificationResponse

4. **Environment Promotion Models**
   - `promotion.py`: PromotionRecord

5. **Transformer Models**
   - `transformer.py`: TransformerInfo, TransformerOutput

6. **IPAM/DNS Models**
   - `dns.py`: DnsRecordCreate, DnsRecord

7. **Certificate Models**
   - `certificate.py`: CertificateCreate, Certificate

8. **Monitoring Models**
   - `monitoring.py`: VipStatus, PoolStatus, HealthStatus, SystemMetrics

9. **Error Models**
   - `error.py`: Error model

Reference the `/docs/enhanced_data_models_architecture.md` and `/docs/enhanced_openapi_specification.yaml` files for detailed model definitions.

### 2.2 Implement API Controllers

Create the following controllers in `/api/controllers/`:

1. **VIP Controller**
   - `vip_controller.py`: CRUD operations for VIPs

2. **Entitlement Controller**
   - `entitlement_controller.py`: Entitlement verification operations

3. **Change Management Controller**
   - `change_controller.py`: Change management operations

4. **Environment Promotion Controller**
   - `promotion_controller.py`: Environment promotion operations

5. **Transformer Controller**
   - `transformer_controller.py`: Transformer operations

6. **IPAM/DNS Controller**
   - `ipam_dns_controller.py`: IPAM and DNS operations

7. **Certificate Controller**
   - `certificate_controller.py`: Certificate management operations

8. **Monitoring Controller**
   - `monitoring_controller.py`: Monitoring and health check operations

Reference the `/docs/enhanced_openapi_specification.yaml` file for detailed API endpoint definitions.

### 2.3 Implement API Middleware

Create the following middleware in `/api/middleware/`:

1. **Authentication Middleware**
   - `auth.py`: Basic authentication middleware

2. **Entitlement Middleware**
   - `entitlement.py`: Entitlement verification middleware

3. **Change Verification Middleware**
   - `change.py`: Change number verification middleware

4. **Rate Limiting Middleware**
   - `rate_limit.py`: Rate limiting middleware

5. **Logging Middleware**
   - `logging.py`: Request/response logging middleware

### 2.4 Implement API Utilities

Create the following utilities in `/api/utils/`:

1. **Validation Utilities**
   - `validation.py`: Input validation utilities

2. **Response Utilities**
   - `response.py`: Standardized response utilities

3. **Error Handling Utilities**
   - `error.py`: Error handling utilities

### 2.5 Implement FastAPI Application

Create the FastAPI application entry point in `/api/main.py`:

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

# Import controllers
from controllers import (
    vip_controller,
    entitlement_controller,
    change_controller,
    promotion_controller,
    transformer_controller,
    ipam_dns_controller,
    certificate_controller,
    monitoring_controller,
)

# Import middleware
from middleware import auth, entitlement, change, rate_limit, logging

# Create FastAPI application
app = FastAPI(
    title="Load Balancing as a Service (LBaaS) API",
    description="API for managing load balancing services across multiple vendors (F5 BIG-IP via AS3, AVI Networks, and NGINX).",
    version="1.0.0",
)

# Add middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.add_middleware(logging.LoggingMiddleware)
app.add_middleware(rate_limit.RateLimitingMiddleware)

# Include routers
app.include_router(vip_controller.router, prefix="/api/v1", tags=["VIP Management"])
app.include_router(entitlement_controller.router, prefix="/api/v1", tags=["Entitlement"])
app.include_router(change_controller.router, prefix="/api/v1", tags=["Change Management"])
app.include_router(promotion_controller.router, prefix="/api/v1", tags=["Environment Promotion"])
app.include_router(transformer_controller.router, prefix="/api/v1", tags=["Transformer"])
app.include_router(ipam_dns_controller.router, prefix="/api/v1", tags=["IPAM/DNS"])
app.include_router(certificate_controller.router, prefix="/api/v1", tags=["Certificate"])
app.include_router(monitoring_controller.router, prefix="/api/v1", tags=["Monitoring"])

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Load Balancing as a Service (LBaaS) API",
        version="1.0.0",
        description="API for managing load balancing services across multiple vendors (F5 BIG-IP via AS3, AVI Networks, and NGINX).",
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "basicAuth": {"type": "http", "scheme": "basic"}
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Health check endpoint
@app.get("/health", tags=["Monitoring"])
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Step 3: Implement Business Layer

### 3.1 Create Business Models

Create the following business models in `/business/models/`:

1. **VIP Models**
   - `vip.py`: VipModel, MonitorModel, PersistenceModel, PoolMemberModel

2. **Entitlement Models**
   - `entitlement.py`: EntitlementModel

3. **Change Management Models**
   - `change.py`: ChangeRequestModel

4. **Environment Promotion Models**
   - `promotion.py`: PromotionModel

5. **Transformer Models**
   - `transformer.py`: TransformerModel, TransformerOutputModel

6. **IPAM/DNS Models**
   - `dns.py`: DnsRecordModel

7. **Certificate Models**
   - `certificate.py`: CertificateModel

### 3.2 Implement Business Services

Create the following services in `/business/services/`:

1. **VIP Service**
   - `vip_service.py`: VIP management service

2. **Entitlement Service**
   - `entitlement_service.py`: Entitlement verification service

3. **Change Management Service**
   - `change_service.py`: Change management service

4. **Environment Promotion Service**
   - `promotion_service.py`: Environment promotion service

5. **Transformer Service**
   - `transformer_service.py`: Transformer service

6. **IPAM/DNS Service**
   - `ipam_dns_service.py`: IPAM and DNS service

7. **Certificate Service**
   - `certificate_service.py`: Certificate management service

8. **Monitoring Service**
   - `monitoring_service.py`: Monitoring and health check service

### 3.3 Implement Business Utilities

Create the following utilities in `/business/utils/`:

1. **Database Utilities**
   - `database.py`: MongoDB database utilities

2. **Cache Utilities**
   - `cache.py`: Redis cache utilities

3. **Validation Utilities**
   - `validation.py`: Business validation utilities

4. **Logging Utilities**
   - `logging.py`: Business logging utilities

## Step 4: Implement Integration Layer

### 4.1 Implement ServiceNow CMDB Integration

Create the following files in `/integration/cmdb/`:

1. **CMDB Client**
   - `client.py`: ServiceNow CMDB API client

2. **CMDB Models**
   - `models.py`: ServiceNow CMDB data models

3. **CMDB Service**
   - `service.py`: ServiceNow CMDB integration service

Reference the `/docs/enhanced_integration.md` file for detailed integration design.

### 4.2 Implement F5 AS3 Integration

Create the following files in `/integration/f5/`:

1. **F5 AS3 Client**
   - `client.py`: F5 AS3 API client

2. **F5 AS3 Models**
   - `models.py`: F5 AS3 data models

3. **F5 AS3 Service**
   - `service.py`: F5 AS3 integration service

4. **F5 AS3 Transformer**
   - `transformer.py`: F5 AS3 transformer

Reference the `/docs/f5_avi_api_research.md` file for detailed F5 AS3 API information.

### 4.3 Implement AVI Networks Integration

Create the following files in `/integration/avi/`:

1. **AVI Client**
   - `client.py`: AVI Networks API client

2. **AVI Models**
   - `models.py`: AVI Networks data models

3. **AVI Service**
   - `service.py`: AVI Networks integration service

4. **AVI Transformer**
   - `transformer.py`: AVI Networks transformer

Reference the `/docs/f5_avi_api_research.md` file for detailed AVI Networks API information.

### 4.4 Implement NGINX Integration

Create the following files in `/integration/nginx/`:

1. **NGINX Models**
   - `models.py`: NGINX configuration models

2. **NGINX Service**
   - `service.py`: NGINX integration service

3. **NGINX Transformer**
   - `transformer.py`: NGINX transformer

4. **NGINX Deployment**
   - `deployment.py`: NGINX deployment service

### 4.5 Implement Bluecat DDI Integration

Create the following files in `/integration/bluecat/`:

1. **Bluecat Client**
   - `client.py`: Bluecat DDI API client

2. **Bluecat Models**
   - `models.py`: Bluecat DDI data models

3. **Bluecat Service**
   - `service.py`: Bluecat DDI integration service

4. **IPAM Service**
   - `ipam.py`: IPAM service

5. **DNS Service**
   - `dns.py`: DNS service

### 4.6 Implement Certificate Authority Integration

Create the following files in `/integration/cert/`:

1. **Certificate Authority Client**
   - `client.py`: Certificate Authority API client

2. **Certificate Models**
   - `models.py`: Certificate data models

3. **Certificate Service**
   - `service.py`: Certificate Authority integration service

## Step 5: Implement Ansible Automation

### 5.1 Create Ansible Playbooks

Create the following playbooks in `/ansible/playbooks/`:

1. **NGINX Deployment Playbook**
   - `deploy_nginx.yml`: Playbook for deploying NGINX instances

2. **NGINX Configuration Playbook**
   - `configure_nginx.yml`: Playbook for configuring NGINX instances

3. **Monitoring Deployment Playbook**
   - `deploy_monitoring.yml`: Playbook for deploying Prometheus and Grafana

### 5.2 Create Ansible Roles

Create the following roles in `/ansible/roles/`:

1. **NGINX Role**
   - `nginx/`: Role for NGINX installation and configuration

2. **Monitoring Role**
   - `monitoring/`: Role for Prometheus and Grafana installation and configuration

## Step 6: Implement Kubernetes Deployment

### 6.1 Create Kubernetes Manifests

Create the following manifests in `/kubernetes/`:

1. **API Service Manifests**
   - `api/deployment.yaml`: API service deployment
   - `api/service.yaml`: API service service
   - `api/configmap.yaml`: API service configuration
   - `api/hpa.yaml`: API service horizontal pod autoscaler

2. **Business Service Manifests**
   - `business/deployment.yaml`: Business service deployment
   - `business/service.yaml`: Business service service
   - `business/configmap.yaml`: Business service configuration
   - `business/hpa.yaml`: Business service horizontal pod autoscaler

3. **Integration Service Manifests**
   - `integration/deployment.yaml`: Integration service deployment
   - `integration/service.yaml`: Integration service service
   - `integration/configmap.yaml`: Integration service configuration
   - `integration/hpa.yaml`: Integration service horizontal pod autoscaler

4. **Database Manifests**
   - `database/statefulset.yaml`: MongoDB stateful set
   - `database/service.yaml`: MongoDB service
   - `database/configmap.yaml`: MongoDB configuration
   - `database/pvc.yaml`: MongoDB persistent volume claim

5. **Cache Manifests**
   - `cache/statefulset.yaml`: Redis stateful set
   - `cache/service.yaml`: Redis service
   - `cache/configmap.yaml`: Redis configuration
   - `cache/pvc.yaml`: Redis persistent volume claim

6. **Monitoring Manifests**
   - `monitoring/prometheus-deployment.yaml`: Prometheus deployment
   - `monitoring/prometheus-service.yaml`: Prometheus service
   - `monitoring/prometheus-configmap.yaml`: Prometheus configuration
   - `monitoring/grafana-deployment.yaml`: Grafana deployment
   - `monitoring/grafana-service.yaml`: Grafana service
   - `monitoring/grafana-configmap.yaml`: Grafana configuration

7. **Ingress Manifests**
   - `ingress.yaml`: Ingress controller configuration

## Step 7: Implement Mock Services

### 7.1 Create ServiceNow CMDB Mock

Create a mock ServiceNow CMDB service in `/docker/mock/servicenow/`:

1. **Mock API**
   - `api.py`: Mock ServiceNow CMDB API

2. **Mock Data**
   - `data.py`: Mock ServiceNow CMDB data

### 7.2 Create Bluecat DDI Mock

Create a mock Bluecat DDI service in `/docker/mock/bluecat/`:

1. **Mock API**
   - `api.py`: Mock Bluecat DDI API

2. **Mock Data**
   - `data.py`: Mock Bluecat DDI data

### 7.3 Create Certificate Authority Mock

Create a mock Certificate Authority service in `/docker/mock/cert/`:

1. **Mock API**
   - `api.py`: Mock Certificate Authority API

2. **Mock Data**
   - `data.py`: Mock Certificate Authority data

## Step 8: Implement Monitoring

### 8.1 Configure Prometheus

Create Prometheus configuration in `/docker/monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'api'
    static_configs:
      - targets: ['api:8000']
  - job_name: 'business'
    static_configs:
      - targets: ['business:8001']
  - job_name: 'integration'
    static_configs:
      - targets: ['integration:8002']
```

### 8.2 Configure Grafana

Create Grafana dashboards in `/docker/monitoring/grafana/`:

1. **System Health Dashboard**
   - `system_health.json`: System health dashboard

2. **VIP Performance Dashboard**
   - `vip_performance.json`: VIP performance dashboard

3. **Error Rate Dashboard**
   - `error_rate.json`: Error rate dashboard

4. **Resource Utilization Dashboard**
   - `resource_utilization.json`: Resource utilization dashboard

## Step 9: Testing

### 9.1 Create Unit Tests

Create unit tests for each component:

1. **API Tests**
   - `/api/tests/`: Unit tests for API layer

2. **Business Tests**
   - `/business/tests/`: Unit tests for business layer

3. **Integration Tests**
   - `/integration/tests/`: Unit tests for integration layer

### 9.2 Create Integration Tests

Create integration tests for end-to-end testing:

1. **End-to-End Tests**
   - `/tests/e2e/`: End-to-end tests

2. **Performance Tests**
   - `/tests/performance/`: Performance tests

## Step 10: Documentation

### 10.1 Create API Documentation

Ensure the OpenAPI specification is complete and accurate:

1. **OpenAPI Specification**
   - `/docs/enhanced_openapi_specification.yaml`: OpenAPI specification

2. **API Design Documentation**
   - `/docs/enhanced_api_design.md`: API design documentation

### 10.2 Create Architecture Documentation

Ensure the architecture documentation is complete and accurate:

1. **Data Models and Architecture Documentation**
   - `/docs/enhanced_data_models_architecture.md`: Data models and architecture documentation

2. **Integration Documentation**
   - `/docs/enhanced_integration.md`: Integration documentation

### 10.3 Create User Documentation

Create user documentation:

1. **User Guide**
   - `/docs/user_guide.md`: User guide

2. **API Reference**
   - `/docs/api_reference.md`: API reference

3. **Troubleshooting Guide**
   - `/docs/troubleshooting.md`: Troubleshooting guide

## Step 11: Deployment

### 11.1 Local Development Deployment

Deploy the system locally using Docker Compose:

```bash
# Linux/Mac
docker-compose up -d

# Windows
docker-compose -f docker-compose-windows.yml up -d
```

### 11.2 Kubernetes Deployment

Deploy the system to Kubernetes:

```bash
kubectl apply -f kubernetes/
```

## Implementation Details

### MongoDB Schema Design

Reference the MongoDB schema design in `/docs/enhanced_data_models_architecture.md` for detailed collection and document structures.

### Redis Cache Design

Reference the Redis cache design in `/docs/enhanced_data_models_architecture.md` for detailed cache key structures and TTL values.

### F5 AS3 Integration

Reference the F5 AS3 API research in `/docs/f5_avi_api_research.md` for detailed integration information.

### AVI Networks Integration

Reference the AVI Networks API research in `/docs/f5_avi_api_research.md` for detailed integration information.

### Bluecat DDI Integration

Reference the Bluecat DDI integration design in `/docs/enhanced_integration.md` for detailed integration information.

### ServiceNow CMDB Integration

Reference the ServiceNow CMDB integration design in `/docs/enhanced_integration.md` for detailed integration information.

## Security Considerations

### Authentication and Authorization

Implement basic authentication for initial implementation, with role-based access control (RBAC):

1. **Admin Role**: Access to all resources
2. **User Role**: Limited by app_id and environment entitlements

### Data Protection

1. **No Storage of SSL Certificates or Keys**: Only store references to certificates
2. **Encryption at Rest**: Encrypt sensitive data in MongoDB
3. **TLS for All Communications**: Use HTTPS for all API endpoints
4. **Secure Credential Storage**: Use Kubernetes secrets for external system credentials

### Compliance

1. **Black Duck Security Scanning**: Implement in CI/CD pipeline
2. **Audit Logging**: Log all operations for compliance
3. **Financial Institution Security Requirements**: Follow industry best practices

## Monitoring and Observability

### Prometheus Integration

1. **Metrics Collection**: Collect metrics from all services
2. **Custom Metrics**: Implement custom metrics for VIP status and performance
3. **Alert Rules**: Configure alert rules for critical conditions

### Grafana Dashboards

1. **System Health Dashboard**: Monitor overall system health
2. **VIP Performance Dashboard**: Monitor VIP performance
3. **Error Rate Dashboard**: Monitor error rates
4. **Resource Utilization Dashboard**: Monitor resource utilization

## Conclusion

This rebuild guide provides comprehensive instructions for reconstructing the LBaaS API system from scratch. By following these steps, you can create a fully functional system that meets all the requirements and integrates with all the necessary external systems.

For detailed information on specific components, refer to the documentation in the `/docs/` directory.

## References

1. [Enhanced Data Models and Architecture](/docs/enhanced_data_models_architecture.md)
2. [Enhanced OpenAPI Specification](/docs/enhanced_openapi_specification.yaml)
3. [F5 AS3 and AVI API Research](/docs/f5_avi_api_research.md)
4. [Enhanced Integration Design](/docs/enhanced_integration.md)
5. [Competitive Analysis](/docs/competitive_analysis.md)
6. [Windows Setup Guide](/docs/windows_setup_guide.md)
