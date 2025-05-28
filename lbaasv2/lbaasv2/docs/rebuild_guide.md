# LBaaS API Rebuild Guide

## 1. Introduction

This document provides a comprehensive guide for rebuilding the Load Balancing as a Service (LBaaS) API project. It is intended for use by either an AI assistant or a human developer with the necessary technical expertise. The goal is to reconstruct the system based on the design specifications, architecture, and requirements outlined in the accompanying documentation.

Refer to the main project `README.md` for an overview and the `docs` directory for detailed design documents.

## 2. Prerequisites

Before starting the rebuild process, ensure the following prerequisites are met:

- **Programming Languages**: Python 3.11+
- **Frameworks**: FastAPI
- **Databases**: MongoDB, Redis
- **Containerization**: Docker, Docker Compose
- **Automation**: Ansible
- **Version Control**: Git
- **DDI**: Access to a Bluecat DDI instance (or a mock)
- **ITSM**: Access to a ServiceNow instance (or a mock for CMDB and Change Management)
- **Load Balancers**: Access to F5 BIG-IP (with AS3), AVI Vantage, and a virtualization platform (like vSphere) for NGINX deployment (or mocks)
- **Development Environment**: A suitable development environment (e.g., Linux, macOS, or Windows with WSL2) with necessary SDKs and tools installed.
- **Project Files**: Access to the complete `lbaasv2` project archive, including all documentation in the `docs` directory.

## 3. Step-by-Step Rebuild Process

Follow these steps sequentially to rebuild the LBaaS API project.

### Step 3.1: Set Up Project Structure

Recreate the project directory structure as defined in the main `README.md` file. This structure organizes the code by layers (API, Business Logic, Integration) and includes directories for Docker configuration, Ansible playbooks, documentation, tests, and mock services.

```
lbaasv2/
├── api/
├── business/
├── integration/
├── mock/
├── ansible/
├── docker/
├── docs/
├── tests/
├── docker-compose.yml
└── README.md
```

### Step 3.2: Implement Core Data Models

Define the Pydantic models for all data structures used within the application. These models represent VIP configurations, entitlement requests/responses, Bluecat DDI objects, Ansible deployment details, etc.

- **Reference**: `docs/data_models_architecture_updated.md` (Section: Data Models)
- **Location**: Implement these models primarily within the `api/models/` directory or shared model files accessible by different layers.
- **Key Models**: `VipBase`, `Monitor`, `Persistence`, `PoolMember`, `EntitlementVerification`, `BluecatIPAllocationRequest`, `AnsibleDeploymentRequest`, etc.
- **Validation**: Ensure all validation rules specified in the data models document (e.g., regex patterns, enums, range checks) are implemented using Pydantic validators.

### Step 3.3: Build the API Layer (FastAPI)

Develop the main API application using FastAPI.

- **Reference**: `docs/openapi_specification_updated.yaml` for endpoint definitions, request/response schemas, and security requirements.
- **Location**: `api/` directory.
- **Key Files**:
    - `api/main.py`: FastAPI application setup, middleware configuration (CORS), router inclusion, health checks.
    - `api/controllers/`: Implement API endpoint logic for each resource type (VIPs, Entitlements, Bluecat, Ansible, etc.). Use FastAPI routers.
    - `api/middleware/`: Implement custom middleware if needed (e.g., request logging, specialized authentication).
- **Authentication**: Implement JWT bearer token authentication and basic auth (for testing) as defined in the OpenAPI spec.
- **Authorization**: Implement role-based access control (Admin, User, Auditor) based on the authenticated user.
- **Dependencies**: Use FastAPI dependency injection for authentication, database connections, and service access.

### Step 3.4: Implement Business Logic Services

Create services within the business logic layer to encapsulate the core functionality.

- **Reference**: `docs/data_models_architecture_updated.md` (Section: Architecture -> Business Logic Layer)
- **Location**: `business/` directory, organized by domain (e.g., `business/vip/`, `business/entitlement/`).
- **Key Services**:
    - `VipService`: Handles CRUD operations, validation logic specific to VIPs.
    - `EntitlementService`: Manages entitlement checks, interacts with CMDB connector.
    - `TransformerService`: Generates vendor-specific LB configurations.
    - `PromotionService`: Handles VIP promotion between environments.
    - `BluecatDDIService`: Orchestrates IPAM/DNS operations via the Bluecat connector.
    - `ChangeManagementService`: Validates ServiceNow change numbers.
    - `AnsibleDeploymentService`: Manages Ansible playbook execution.
- **Interaction**: Services should interact with each other and with the integration layer connectors.

### Step 3.5: Develop Integration Connectors

Build connectors to interface with external systems.

- **Reference**: `docs/data_models_architecture_updated.md` (Section: Architecture -> Integration Layer), `docs/enhanced_integration.md`
- **Location**: `integration/` directory, organized by external system (e.g., `integration/cmdb/`, `integration/bluecat/`).
- **Key Connectors**:
    - `CMDBConnector`: Interacts with ServiceNow CMDB API.
    - `BluecatConnector`: Interacts with Bluecat DDI API.
    - `LoadBalancerConnector`: Abstract base or specific connectors for F5 (AS3), AVI, NGINX.
    - `ChangeManagementConnector`: Interacts with ServiceNow Change Management API.
    - `AnsibleConnector`: Interacts with Ansible (e.g., triggering playbooks via Ansible Runner or AWX/Tower API).
    - `CertificateAuthorityConnector`: Interacts with the chosen CA.
- **Error Handling**: Implement robust error handling and retry mechanisms for external API calls.

### Step 3.6: Set Up Docker Containers

Create Dockerfiles for each service/layer that needs to be containerized.

- **Reference**: `docs/data_models_architecture_updated.md` (Section: Deployment Architecture -> Docker Container Structure)
- **Location**: `docker/` directory, with subdirectories for each container (e.g., `docker/api/`, `docker/business/`).
- **Key Dockerfiles**:
    - `docker/api/Dockerfile`: For the FastAPI application.
    - `docker/business/Dockerfile`: For the business logic services (if separated).
    - `docker/integration/Dockerfile`: For the integration connectors (if separated).
    - `docker/mock/Dockerfile`: For the mock services container.
    - `docker/monitoring/Dockerfile`: For Prometheus/Grafana setup.
    - `docker/ansible/Dockerfile`: For the Ansible control node.
- **Base Images**: Use appropriate base images (e.g., `python:3.11-slim`).
- **Dependencies**: Ensure all necessary dependencies are installed via `requirements.txt` or package manager commands.
- **Configuration**: Copy application code and configure entry points/commands.

### Step 3.7: Configure Docker Compose

Define the multi-container application setup using Docker Compose.

- **Reference**: `docs/data_models_architecture_updated.md` (Section: Deployment Architecture), Example `docker-compose.yml` provided in the project root.
- **Location**: `docker-compose.yml` in the project root.
- **Services**: Define services for each container (API, Business Logic, Integration, MongoDB, Redis, Mock, Monitoring, Ansible).
- **Networking**: Configure Docker networks for inter-container communication.
- **Volumes**: Define volumes for persistent data (MongoDB, Redis, Prometheus, Grafana).
- **Environment Variables**: Manage configuration and secrets using environment variables (potentially sourced from `.env` files).
- **Dependencies**: Define service dependencies using `depends_on`.

### Step 3.8: Implement Mock Services

Develop mock services for external dependencies to facilitate testing and local development.

- **Location**: `mock/` directory.
- **Key Mocks**:
    - ServiceNow CMDB/Change Management mock.
    - Bluecat DDI mock.
    - F5/AVI/NGINX load balancer mocks.
- **Implementation**: Can be simple FastAPI applications or use tools like MockServer.
- **Containerization**: Include a service definition in `docker-compose.yml` to run the mocks.

### Step 3.9: Set Up Monitoring

Configure Prometheus and Grafana for monitoring the LBaaS application.

- **Reference**: `docs/data_models_architecture_updated.md` (Section: Monitoring and Observability)
- **Location**: `docker/monitoring/` directory.
- **Configuration**:
    - `prometheus.yml`: Configure Prometheus scrape targets (API, Business Logic containers).
    - Grafana Dashboards: Create dashboards (can be provisioned via configuration files) to visualize key metrics.
- **Instrumentation**: Instrument the Python services (API, Business Logic) to expose Prometheus metrics (e.g., using `prometheus-fastapi-instrumentator` or `prometheus-client`).

### Step 3.10: Write Ansible Playbooks

Develop Ansible playbooks for deployment automation.

- **Reference**: `docs/data_models_architecture_updated.md` (Section: Ansible Deployment Integration)
- **Location**: `ansible/` directory.
- **Key Playbooks**:
    - `ansible/playbooks/deploy_nginx.yml`: Deploys and configures an NGINX instance for a VIP.
    - Playbooks for deploying the LBaaS application containers (optional, could also be managed by other CI/CD tools).
    - Playbooks for configuring F5/AVI (optional, could be handled by transformers).
- **Roles**: Organize tasks into reusable Ansible roles (`ansible/roles/`).
- **Inventory**: Manage target hosts in `ansible/inventory/`.
- **Variables**: Define environment-specific variables in `ansible/vars/`.

### Step 3.11: Implement Testing

Develop a comprehensive test suite.

- **Location**: `tests/` directory.
- **Unit Tests**: Use `pytest` to test individual functions and classes in isolation. Mock dependencies where necessary.
- **Integration Tests**: Test the interaction between different components (e.g., API layer calling Business Logic service, service calling Integration connector against mock services). Use `httpx` for API testing.
- **End-to-End (E2E) Tests**: Test complete user workflows through the API, potentially interacting with the full stack running via Docker Compose.

### Step 3.12: Deployment

Prepare the application for deployment.

- **Reference**: `docs/data_models_architecture_updated.md` (Section: Deployment Architecture)
- **Container Registry**: Push built Docker images to a container registry (e.g., Docker Hub, AWS ECR, Google GCR).
- **Orchestration**: Use Ansible or another CI/CD tool (e.g., Jenkins, GitLab CI, GitHub Actions) to deploy the containers defined in `docker-compose.yml` (or Kubernetes manifests if applicable) to the target environments (Dev, UAT, Prod).
- **Configuration Management**: Manage environment-specific configurations securely (e.g., using environment variables, secrets management tools like HashiCorp Vault).

## 4. Referencing Existing Documentation

Throughout the rebuild process, constantly refer to the detailed documentation provided in the `lbaasv2/docs/` directory:

- **`README.md`**: Project overview, structure, quick start.
- **`enhanced_requirements_design.md`**: Detailed functional and non-functional requirements.
- **`data_models_architecture_updated.md`**: Core reference for data structures, component architecture, interactions, Bluecat/Ansible integration, and deployment strategy.
- **`openapi_specification_updated.yaml`**: Definitive source for API endpoints, request/response formats, and validation rules.
- **`enhanced_integration.md`**: Specific details on integrating with external systems like ServiceNow and Bluecat.
- **`competitive_analysis.md`**: Insights into features and approaches of similar industry solutions.

## 5. Conclusion

Following this guide and referencing the detailed documentation should enable a skilled AI or developer to successfully rebuild the LBaaS API project. Consistency with the defined architecture, data models, and API specifications is crucial for a successful reconstruction. Remember to adapt specific implementation details (like external API authentication methods) based on the target environment and available credentials.
