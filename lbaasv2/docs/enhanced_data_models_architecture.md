# Enhanced LBaaS API Data Models and Architecture

## Overview

This document describes the data models and architecture for the Load Balancing as a Service (LBaaS) API. The architecture is designed to support multiple load balancer vendors (F5 BIG-IP via AS3, AVI Networks, and NGINX), provide entitlement verification through ServiceNow CMDB integration, and offer a standard output format for vendor-specific transformers.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  API Layer      │────▶│  Business Layer │────▶│  Integration    │
│  (FastAPI)      │     │  (Services)     │     │  Layer          │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  MongoDB        │     │  Redis Cache    │     │  External       │
│  Database       │     │                 │     │  Systems        │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Component Details

1. **API Layer**
   - FastAPI-based RESTful API
   - Swagger/OpenAPI documentation
   - Authentication and authorization
   - Request validation
   - Rate limiting and security controls

2. **Business Layer**
   - VIP management service
   - Entitlement verification service
   - Transformer service
   - Environment promotion service
   - Bluecat DDI integration service
   - Change management service
   - Ansible automation service

3. **Integration Layer**
   - ServiceNow CMDB connector
   - F5 AS3 connector
   - AVI API connector
   - NGINX deployment connector
   - Bluecat DDI connector
   - Certificate Authority connector

4. **Data Storage**
   - MongoDB for LBaaS configurations
   - Redis for caching and session management

5. **External Systems**
   - ServiceNow CMDB
   - F5 BIG-IP load balancers
   - AVI Networks load balancers
   - NGINX instances
   - Bluecat DDI
   - Certificate Authority
   - Prometheus/Grafana monitoring

### Containerization and Kubernetes Architecture

The LBaaS system is designed to be fully containerized and deployed on Kubernetes, with the following components:

```
┌─────────────────────────────────────────────────────────────────┐
│                      Kubernetes Cluster                         │
│                                                                 │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐│
│  │                 │   │                 │   │                 ││
│  │  API            │   │  Business       │   │  Integration    ││
│  │  Deployment     │   │  Deployment     │   │  Deployment     ││
│  │                 │   │                 │   │                 ││
│  └─────────────────┘   └─────────────────┘   └─────────────────┘│
│                                                                 │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐│
│  │                 │   │                 │   │                 ││
│  │  MongoDB        │   │  Redis          │   │  Prometheus     ││
│  │  StatefulSet    │   │  StatefulSet    │   │  & Grafana      ││
│  │                 │   │                 │   │                 ││
│  └─────────────────┘   └─────────────────┘   └─────────────────┘│
│                                                                 │
│  ┌─────────────────┐   ┌─────────────────┐                      │
│  │                 │   │                 │                      │
│  │  Ingress        │   │  Secrets        │                      │
│  │  Controller     │   │  Management     │                      │
│  │                 │   │                 │                      │
│  └─────────────────┘   └─────────────────┘                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Kubernetes Resources

- **Deployments**: For stateless services (API, Business, Integration)
- **StatefulSets**: For stateful services (MongoDB, Redis)
- **ConfigMaps**: For configuration data
- **Secrets**: For sensitive data (credentials, certificates)
- **Services**: For internal communication
- **Ingress**: For external access
- **HorizontalPodAutoscalers**: For automatic scaling
- **PersistentVolumeClaims**: For persistent storage
- **NetworkPolicies**: For network security

## Data Models

### Core Data Models

#### VipBase

```python
class VipBase:
    vip_fqdn: str                      # Fully Qualified Domain Name of the VIP
    vip_ip: Optional[str]              # IP address of the VIP (can be auto-assigned)
    app_id: str                        # Application identifier
    environment: str                   # Deployment environment (Dev, UAT, Prod)
    datacenter: str                    # Datacenter where the VIP is provisioned
    primary_contact_email: EmailStr    # Primary contact email
    secondary_contact_email: Optional[EmailStr]  # Secondary contact email
    team_distribution_email: Optional[EmailStr]  # Team distribution email
    monitor: Monitor                   # Health monitoring configuration
    persistence: Optional[Persistence] # Session persistence configuration
    ssl_cert_name: Optional[str]       # SSL certificate name/reference
    mtls_ca_cert_name: Optional[str]   # mTLS CA certificate name/reference
    pool: List[PoolMember]             # List of backend servers in the pool
    owner: str                         # Owner or creator of the VIP
    port: int                          # Listening port for the VIP
    protocol: str                      # Protocol for the VIP (e.g., TCP, HTTP, HTTPS)
    lb_method: Optional[str]           # Load balancing method
```

#### Monitor

```python
class Monitor:
    type: str                          # Monitor type (TCP, UDP, HTTP, HTTPS)
    interval: int                      # Check interval in seconds
    timeout: int                       # Timeout in seconds
    send_string: Optional[str]         # String to send (for HTTP/HTTPS)
    receive_string: Optional[str]      # Expected response string
    url_path: Optional[str]            # URL path for HTTP/HTTPS monitors
    alternate_port: Optional[int]      # Alternate port for monitoring
```

#### Persistence

```python
class Persistence:
    type: str                          # Persistence type (source_ip, cookie, session)
    cookie_name: Optional[str]         # Cookie name for cookie persistence
    timeout: int                       # Persistence timeout in seconds
```

#### PoolMember

```python
class PoolMember:
    server_address: str                # Server IP address
    server_port: int                   # Server port
    weight: Optional[int]              # Server weight for priority groups
    enabled: bool                      # Whether the server is enabled
    monitor: Optional[str]             # Server-specific monitor
```

#### EntitlementVerification

```python
class EntitlementVerification:
    app_id: str                        # Application ID to verify
    user_id: str                       # User ID requesting access
    environment: str                   # Target environment
    datacenter: str                    # Target datacenter
    server_addresses: List[str]        # Server addresses to verify
    change_number: str                 # ServiceNow change number
```

#### ChangeRequest

```python
class ChangeRequest:
    change_number: str                 # ServiceNow change number
    requested_by: str                  # User requesting the change
    start_time: datetime               # Scheduled start time
    end_time: datetime                 # Scheduled end time
    description: str                   # Change description
    status: str                        # Change status
```

#### TransformerOutput

```python
class TransformerOutput:
    vip_id: str                        # VIP identifier
    vendor: str                        # Target vendor (F5, AVI, NGINX)
    config: Dict                       # Vendor-specific configuration
    timestamp: datetime                # Generation timestamp
    version: str                       # Configuration version
```

### Vendor-Specific Models

#### F5AS3Configuration

```python
class F5AS3Configuration:
    class_: str = "AS3"                # AS3 class
    action: str = "deploy"             # Action to perform
    persist: bool = True               # Persist configuration
    declaration: Dict                  # AS3 declaration
```

#### AVIConfiguration

```python
class AVIConfiguration:
    virtual_service: Dict              # Virtual service configuration
    pool: Dict                         # Pool configuration
    health_monitor: Dict               # Health monitor configuration
    application_profile: Dict          # Application profile configuration
    persistence_profile: Optional[Dict] # Persistence profile configuration
    ssl_key_certificate: Optional[Dict] # SSL certificate configuration
```

#### NGINXConfiguration

```python
class NGINXConfiguration:
    config_file: str                   # NGINX configuration file content
    ssl_cert: Optional[str]            # SSL certificate content
    ssl_key: Optional[str]             # SSL key content
    deployment_config: Dict            # Kubernetes/Docker deployment configuration
```

### Integration Models

#### ServiceNowCMDBRecord

```python
class ServiceNowCMDBRecord:
    device_id: str                     # Device ID
    device_ip: str                     # Device IP address
    owner1: str                        # Primary owner
    owner2: Optional[str]              # Secondary owner
    owner_email_distro: str            # Owner email distribution list
    environment: str                   # Environment
    datacenter: str                    # Datacenter
    region: str                        # Region
    app_id: str                        # Application ID
```

#### BluecatDDIRecord

```python
class BluecatDDIRecord:
    fqdn: str                          # Fully qualified domain name
    ip_address: str                    # IP address
    record_type: str                   # Record type (A, CNAME, etc.)
    ttl: int                           # Time to live
    view: str                          # DNS view
    zone: str                          # DNS zone
```

## API Endpoints

### VIP Management

- `POST /api/v1/vips`: Create a new VIP
- `GET /api/v1/vips`: List all VIPs
- `GET /api/v1/vips/{vip_id}`: Get a specific VIP
- `PUT /api/v1/vips/{vip_id}`: Update a VIP
- `DELETE /api/v1/vips/{vip_id}`: Delete a VIP

### Entitlement Verification

- `POST /api/v1/entitlements/verify`: Verify entitlements for servers
- `GET /api/v1/entitlements/app/{app_id}`: Get entitlements for an application
- `GET /api/v1/entitlements/user/{user_id}`: Get entitlements for a user

### Change Management

- `POST /api/v1/changes/verify`: Verify a change number
- `GET /api/v1/changes/{change_number}`: Get change details
- `PUT /api/v1/changes/{change_number}/status`: Update change status

### Environment Promotion

- `POST /api/v1/promotion/{vip_id}/{target_env}`: Promote VIP to target environment
- `GET /api/v1/promotion/history/{vip_id}`: Get promotion history for a VIP

### Transformer Management

- `GET /api/v1/transformers`: List available transformers
- `GET /api/v1/transformers/{vendor}`: Get transformer details for a vendor
- `POST /api/v1/transformers/{vendor}/transform`: Transform configuration for a vendor

### IPAM/DNS Integration

- `POST /api/v1/ipam/allocate`: Allocate an IP address
- `DELETE /api/v1/ipam/release/{ip_address}`: Release an IP address
- `POST /api/v1/dns/record`: Create a DNS record
- `DELETE /api/v1/dns/record/{fqdn}`: Delete a DNS record

### Certificate Management

- `POST /api/v1/certificates`: Create/upload a certificate
- `GET /api/v1/certificates`: List all certificates
- `GET /api/v1/certificates/{cert_id}`: Get a specific certificate
- `DELETE /api/v1/certificates/{cert_id}`: Delete a certificate

### Monitoring and Health

- `GET /api/v1/health`: Get system health
- `GET /api/v1/metrics`: Get system metrics
- `GET /api/v1/vips/{vip_id}/status`: Get VIP status
- `GET /api/v1/pools/{pool_id}/status`: Get pool status

## Integration Flows

### VIP Creation Flow

1. User submits VIP creation request with change number
2. API validates request format and required fields
3. System verifies change number with ServiceNow
4. System verifies entitlements for servers with CMDB
5. System allocates IP address from Bluecat IPAM if not provided
6. System creates DNS record in Bluecat DNS
7. System determines target load balancer based on environment and datacenter
8. System transforms configuration for target load balancer
9. System applies configuration to target load balancer
10. System stores configuration in MongoDB
11. System returns success response with VIP details

### Entitlement Verification Flow

1. User submits entitlement verification request
2. System queries ServiceNow CMDB for device ownership
3. System verifies user's app_id against device ownership
4. System checks if user has admin role (bypass entitlement check)
5. System returns verification result

### Environment Promotion Flow

1. User submits promotion request with change number
2. System verifies change number with ServiceNow
3. System retrieves source VIP configuration
4. System modifies environment-specific parameters
5. System verifies entitlements for target environment
6. System allocates new IP address in target environment if needed
7. System creates DNS record in target environment
8. System transforms configuration for target load balancer
9. System applies configuration to target load balancer
10. System stores new configuration in MongoDB
11. System returns success response with promoted VIP details

## Security Considerations

### Authentication and Authorization

- Basic authentication for initial implementation
- Role-based access control (RBAC)
- Admin users have access to all resources
- Regular users limited by app_id and environment entitlements
- All API endpoints require authentication
- Sensitive operations require change number verification

### Data Protection

- No storage of SSL certificates or keys
- Sensitive data encrypted at rest
- TLS for all communications
- Secure credential storage for external system access

### Compliance

- Black Duck security scanning for all code
- Audit logging for all operations
- Compliance with financial institution security requirements

## Monitoring and Observability

### Prometheus Integration

- Metrics collection for all services
- Custom metrics for VIP status and performance
- Alert rules for critical conditions

### Grafana Dashboards

- System health dashboard
- VIP performance dashboard
- Error rate dashboard
- Resource utilization dashboard

## Deployment Architecture

### Docker Containerization

- All components containerized
- Docker Compose for local development
- Kubernetes for production deployment

### Kubernetes Deployment

- Separate namespaces for different environments
- Resource limits and requests
- Horizontal Pod Autoscaling
- Liveness and readiness probes
- ConfigMaps and Secrets for configuration

### CI/CD Pipeline

- Automated testing
- Black Duck security scanning
- Container image building and versioning
- Kubernetes manifest generation
- Deployment automation

## Vendor-Specific Integration Details

### F5 BIG-IP (AS3)

- **Authentication**: Basic or token-based authentication
- **Configuration Model**: Declarative JSON via AS3 API
- **Endpoint**: `/mgmt/shared/appsvcs/declare`
- **Methods**: POST for all operations (with different actions)
- **Actions**: deploy, dry-run, patch, redeploy, retrieve, remove
- **Tenant Isolation**: Tenant-based configuration isolation
- **Monitoring**: Built-in health monitors (HTTP, HTTPS, TCP, UDP)
- **SSL Handling**: Certificate references, no certificate storage

### AVI Networks

- **Authentication**: Session-based with CSRF token
- **Configuration Model**: RESTful CRUD operations
- **Endpoints**: Various `/api/` endpoints for different resources
- **Methods**: GET, POST, PUT, DELETE
- **Tenant Isolation**: X-Avi-Tenant header
- **Monitoring**: Health monitors with various protocols
- **SSL Handling**: Certificate management via API

### NGINX

- **Deployment**: Ansible-based deployment in Kubernetes
- **Configuration Model**: Configuration file generation
- **SSL Handling**: Certificate mounting via Kubernetes secrets
- **Monitoring**: Prometheus exporter for metrics
- **Scaling**: Kubernetes-based scaling

### Bluecat DDI Integration

- **Authentication**: API key or username/password
- **IPAM**: IP address allocation and management
- **DNS**: DNS record creation and management
- **API Endpoints**: REST API for IPAM and DNS operations
- **Automation**: Automated IP allocation and DNS record creation

## MongoDB Schema Design

### Collections

1. **vips**: Stores VIP configurations
   - Indexed by: id, app_id, environment, datacenter

2. **transformers_output**: Stores vendor-specific configurations
   - Indexed by: vip_id, vendor, version

3. **entitlements_cache**: Caches entitlement verification results
   - Indexed by: app_id, user_id, server_address
   - TTL index for automatic expiration

4. **change_requests**: Stores change request details
   - Indexed by: change_number, status

5. **audit_logs**: Stores audit logs for all operations
   - Indexed by: timestamp, operation_type, user_id

### Example VIP Document

```json
{
  "_id": "vip_123456",
  "vip_fqdn": "app.example.com",
  "vip_ip": "10.0.1.10",
  "app_id": "APP001",
  "environment": "PROD",
  "datacenter": "NYDC",
  "primary_contact_email": "admin@example.com",
  "secondary_contact_email": "backup@example.com",
  "team_distribution_email": "team@example.com",
  "monitor": {
    "type": "HTTP",
    "interval": 5,
    "timeout": 16,
    "send_string": "GET /health HTTP/1.1\\r\\nHost: app.example.com\\r\\n\\r\\n",
    "receive_string": "200 OK",
    "url_path": "/health",
    "alternate_port": null
  },
  "persistence": {
    "type": "cookie",
    "cookie_name": "session_id",
    "timeout": 3600
  },
  "ssl_cert_name": "app_example_com",
  "mtls_ca_cert_name": null,
  "pool": [
    {
      "server_address": "192.0.1.10",
      "server_port": 80,
      "weight": 100,
      "enabled": true,
      "monitor": null
    },
    {
      "server_address": "192.0.1.11",
      "server_port": 80,
      "weight": 100,
      "enabled": true,
      "monitor": null
    }
  ],
  "owner": "user123",
  "port": 443,
  "protocol": "HTTPS",
  "lb_method": "ROUND_ROBIN",
  "created_at": "2025-05-28T12:00:00Z",
  "updated_at": "2025-05-28T12:00:00Z",
  "version": 1,
  "status": "active",
  "last_change_number": "CHG0012345"
}
```

## Redis Cache Design

### Cache Keys

1. **Session Cache**:
   - Key: `session:{session_id}`
   - Value: Session data
   - TTL: 30 minutes

2. **Entitlement Cache**:
   - Key: `entitlement:{app_id}:{user_id}:{server_address}`
   - Value: Boolean (entitled or not)
   - TTL: 15 minutes

3. **CMDB Cache**:
   - Key: `cmdb:{device_id}`
   - Value: CMDB record
   - TTL: 60 minutes

4. **Change Request Cache**:
   - Key: `change:{change_number}`
   - Value: Change request details
   - TTL: 5 minutes

5. **Rate Limiting**:
   - Key: `ratelimit:{user_id}:{endpoint}`
   - Value: Counter
   - TTL: 1 minute

## Conclusion

This document provides a comprehensive overview of the LBaaS API data models and architecture. The system is designed to be scalable, resilient, and vendor-agnostic, supporting multiple load balancer technologies through a common API interface. The architecture leverages modern containerization and orchestration technologies, with a focus on security, monitoring, and automation.
