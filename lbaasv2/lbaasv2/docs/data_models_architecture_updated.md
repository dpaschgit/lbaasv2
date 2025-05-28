# LBaaS API Data Models and Architecture with Bluecat DDI and Ansible

## Overview
This document details the data models and architecture for the Load Balancing as a Service (LBaaS) API, incorporating requirements from stakeholder input, competitive analysis of industry solutions like AppViewX and Imperva, and specific integration with Bluecat DDI and Ansible deployment automation.

## Data Models

### Core Models

#### VipBase
```python
class VipBase:
    vip_fqdn: str                      # Fully Qualified Domain Name of the VIP
                                       # Validation: Must be a valid URL format
    vip_ip: Optional[str]              # IP address of the VIP (can be auto-assigned via IPAM)
                                       # Validation: If provided, must be valid IPv4 format
    app_id: str                        # Application identifier
                                       # Validation: Must be in format APP001 through APP010
    environment: str                   # Deployment environment
                                       # Validation: Must be one of: Dev, UAT, Prod
    datacenter: str                    # Datacenter where the VIP is provisioned
                                       # Validation: Must be one of: LADC, NYDC, EUDC, APDC
    region: str                        # Region where the VIP is provisioned
    primary_contact_email: EmailStr    # Primary contact email
                                       # Validation: Must be valid email format
    secondary_contact_email: Optional[EmailStr]  # Secondary contact email
                                       # Validation: If provided, must be valid email format
    team_distribution_email: Optional[EmailStr]  # Team distribution email
                                       # Validation: If provided, must be valid email format
    vip_type: VipType                  # L4 or L7 VIP
    monitor: Monitor                   # Health monitoring configuration
    persistence: Optional[Persistence] # Session persistence configuration
    ssl_cert_name: Optional[str]       # SSL certificate name/reference (not stored)
    mtls_ca_cert_name: Optional[str]   # mTLS CA certificate name/reference (not stored)
    pool: List[PoolMember]             # List of backend servers in the pool
                                       # Validation: Must contain at least 2 members
    owner: str                         # Owner or creator of the VIP
    port: int                          # Listening port for the VIP
                                       # Validation: Must be between 1 and 65535
    protocol: str                      # Protocol for the VIP
                                       # Validation: Must be one of: TCP, HTTP, HTTPS, UDP
    lb_method: str                     # Load balancing method
                                       # Validation: Must be one of: ROUND_ROBIN, LEAST_CONNECTIONS, PRIORITY_GROUP
    priority_group: Optional[PriorityGroup]  # Priority group configuration
    created_at: datetime               # Creation timestamp
    updated_at: datetime               # Last update timestamp
    created_by: str                    # User who created the VIP
    updated_by: str                    # User who last updated the VIP
    change_number: str                 # ServiceNow change number for this operation
                                       # Validation: Must match pattern CHG\d{7}
```

#### VipType (Enum)
```python
class VipType(Enum):
    L4 = "l4"                          # Layer 4 VIP
    L7 = "l7"                          # Layer 7 VIP
```

#### Monitor
```python
class Monitor:
    type: MonitorType                  # Type of health monitor
    port: int                          # Port to use for health monitoring
                                       # Validation: Must be between 1 and 65535
    alternate_port: Optional[int]      # Alternate port for TCP monitors
                                       # Validation: If provided, must be between 1 and 65535
    send: Optional[str]                # String to send for active health checks
    receive: Optional[str]             # Expected string to receive for successful health check
    interval: int                      # Interval between health checks in seconds
                                       # Validation: Must be positive integer
    timeout: int                       # Timeout for health check in seconds
                                       # Validation: Must be positive integer
    retries: int                       # Number of retries before marking as down
                                       # Validation: Must be positive integer
```

#### MonitorType (Enum)
```python
class MonitorType(Enum):
    TCP = "tcp"                        # TCP monitor
    UDP = "udp"                        # UDP monitor
    HTTP = "http"                      # HTTP monitor
    HTTPS = "https"                    # HTTPS monitor
    ECV = "ecv"                        # Enhanced Content Verification monitor
```

#### Persistence
```python
class Persistence:
    type: PersistenceType              # Type of session persistence
    timeout: int                       # Timeout for persistence record in seconds
                                       # Validation: Must be positive integer
    cookie_name: Optional[str]         # Cookie name for cookie persistence
    cookie_encryption: Optional[bool]  # Whether to encrypt the cookie
```

#### PersistenceType (Enum)
```python
class PersistenceType(Enum):
    SOURCE_IP = "source_ip"            # Source IP persistence
    COOKIE = "cookie"                  # Cookie-based persistence
    SESSION = "session"                # Session-based persistence
```

#### PoolMember
```python
class PoolMember:
    ip: str                            # IP address of the backend server
                                       # Validation: Must be valid IPv4 format
    port: int                          # Port of the backend server
                                       # Validation: Must be between 1 and 65535
    weight: Optional[int]              # Weight for load balancing
                                       # Validation: If provided, must be positive integer
    priority_group: Optional[int]      # Priority group ID
                                       # Validation: If provided, must be positive integer
    backup: Optional[bool]             # Whether this is a backup server
    app_id: str                        # Application ID of the server
                                       # Validation: Must be in format APP001 through APP010
```

#### PriorityGroup
```python
class PriorityGroup:
    enabled: bool                      # Whether priority groups are enabled
    groups: List[PriorityGroupConfig]  # List of priority group configurations
                                       # Validation: Must contain at least one group if enabled
```

#### PriorityGroupConfig
```python
class PriorityGroupConfig:
    id: int                            # Priority group ID
                                       # Validation: Must be positive integer
    priority: int                      # Priority level (lower is higher priority)
                                       # Validation: Must be positive integer
    min_active_members: Optional[int]  # Minimum active members before failing over
                                       # Validation: If provided, must be positive integer
```

#### LBMethod (Enum)
```python
class LBMethod(Enum):
    ROUND_ROBIN = "round_robin"        # Round Robin load balancing
    LEAST_CONNECTIONS = "least_connections"  # Least Connections load balancing
    PRIORITY_GROUP = "priority_group"  # Priority Group-based load balancing
```

### Entitlement Models

#### EntitlementVerification
```python
class EntitlementVerification:
    server_ids: List[str]              # List of server IDs to verify entitlements for
                                       # Validation: Must contain at least one server ID
    app_ids: Optional[List[str]]       # Optional list of application IDs for verification
                                       # Validation: If provided, each must be in format APP001 through APP010
    change_number: str                 # ServiceNow change number for this operation
                                       # Validation: Must match pattern CHG\d{7}
```

#### EntitlementResult
```python
class EntitlementResult:
    server_id: str                     # Server ID
    app_id: str                        # Application ID
                                       # Validation: Must be in format APP001 through APP010
    entitled: bool                     # Whether the user is entitled to this server
    reason: Optional[str]              # Reason for entitlement decision
```

#### UserRole (Enum)
```python
class UserRole(Enum):
    ADMIN = "admin"                    # Administrator with access to all resources
    USER = "user"                      # Regular user with limited access
    AUDITOR = "auditor"                # Global audit account with read-only access
```

#### User
```python
class User:
    id: str                            # User ID
    username: str                      # Username
    email: EmailStr                    # Email address
                                       # Validation: Must be valid email format
    role: UserRole                     # User role
    app_ids: List[str]                 # List of application IDs the user has access to
                                       # Validation: Each must be in format APP001 through APP010
```

### Bluecat DDI Models

#### BluecatIPAllocationRequest
```python
class BluecatIPAllocationRequest:
    network: str                       # Network to allocate from
    hostname: str                      # Hostname for the IP
    app_id: str                        # Application ID
                                       # Validation: Must be in format APP001 through APP010
    environment: str                   # Environment
                                       # Validation: Must be one of: Dev, UAT, Prod
    datacenter: str                    # Datacenter
                                       # Validation: Must be one of: LADC, NYDC, EUDC, APDC
    region: str                        # Region
    change_number: str                 # ServiceNow change number for this operation
                                       # Validation: Must match pattern CHG\d{7}
    configuration_name: str            # Bluecat configuration name
    view_name: str                     # Bluecat DNS view name
    zone_name: str                     # Bluecat DNS zone name
```

#### BluecatIPAllocationResponse
```python
class BluecatIPAllocationResponse:
    ip_address: str                    # Allocated IP address
                                       # Validation: Must be valid IPv4 format
    subnet_mask: str                   # Subnet mask
    gateway: str                       # Gateway
                                       # Validation: Must be valid IPv4 format
    dns_servers: List[str]             # DNS servers
                                       # Validation: Each must be valid IPv4 format
    hostname: str                      # Hostname
    fqdn: str                          # Fully qualified domain name
    object_id: str                     # Bluecat object ID
```

#### BluecatDNSRecordRequest
```python
class BluecatDNSRecordRequest:
    hostname: str                      # Hostname
    ip_address: str                    # IP address
                                       # Validation: Must be valid IPv4 format
    record_type: str                   # Record type (A, CNAME, etc.)
                                       # Validation: Must be one of: A, CNAME, AAAA, TXT
    ttl: int                           # Time to live
                                       # Validation: Must be at least 60
    app_id: str                        # Application ID
                                       # Validation: Must be in format APP001 through APP010
    change_number: str                 # ServiceNow change number for this operation
                                       # Validation: Must match pattern CHG\d{7}
    configuration_name: str            # Bluecat configuration name
    view_name: str                     # Bluecat DNS view name
    zone_name: str                     # Bluecat DNS zone name
    create_ptr: bool                   # Whether to create PTR record
```

#### BluecatDNSRecordResponse
```python
class BluecatDNSRecordResponse:
    hostname: str                      # Hostname
    fqdn: str                          # Fully qualified domain name
                                       # Validation: Must be valid FQDN format
    ip_address: str                    # IP address
                                       # Validation: Must be valid IPv4 format
    record_type: str                   # Record type
                                       # Validation: Must be one of: A, CNAME, AAAA, TXT
    ttl: int                           # Time to live
                                       # Validation: Must be at least 60
    object_id: str                     # Bluecat object ID
    ptr_record_id: Optional[str]       # PTR record ID if created
```

### Transformer Models

#### TransformerOutput
```python
class TransformerOutput:
    vip_id: str                        # VIP identifier
    vendor: str                        # Load balancer vendor
    configuration: Dict                # Vendor-specific configuration in standard JSON format
    generated_at: datetime             # Generation timestamp
    generated_by: str                  # User who generated the output
    change_number: str                 # ServiceNow change number for this operation
                                       # Validation: Must match pattern CHG\d{7}
```

#### VendorInfo
```python
class VendorInfo:
    name: str                          # Vendor name
    display_name: str                  # Display name
    capabilities: List[str]            # Supported capabilities
```

### Environment Promotion Models

#### PromotionOptions
```python
class PromotionOptions:
    override_environment_specific: bool  # Whether to override environment-specific data
    specific_overrides: Dict           # Specific fields to override during promotion
    change_number: str                 # ServiceNow change number for this operation
                                       # Validation: Must match pattern CHG\d{7}
```

#### PromotionResult
```python
class PromotionResult:
    success: bool                      # Whether the promotion was successful
    source_vip_id: str                 # Source VIP ID
    target_vip_id: str                 # Target VIP ID
    target_environment: str            # Target environment
                                       # Validation: Must be one of: Dev, UAT, Prod
    modified_fields: List[str]         # Fields that were modified during promotion
    warnings: List[str]                # Warnings during promotion
```

### Change Management Models

#### ChangeValidationRequest
```python
class ChangeValidationRequest:
    change_number: str                 # ServiceNow change number
                                       # Validation: Must match pattern CHG\d{7}
    operation_type: str                # Type of operation
                                       # Validation: Must be one of: CREATE, UPDATE, DELETE, READ
    resource_type: str                 # Type of resource
    resource_id: Optional[str]         # Resource identifier (optional)
```

#### ChangeValidationResponse
```python
class ChangeValidationResponse:
    valid: bool                        # Whether the change is valid
    state: str                         # State of the change
                                       # Validation: Must be one of: approved, scheduled, implementing, closed, rejected
    window_start: Optional[datetime]   # Start of change window
    window_end: Optional[datetime]     # End of change window
    owner: Optional[str]               # Owner of the change
    reason: Optional[str]              # Reason if invalid
```

### Ansible Deployment Models

#### AnsibleDeploymentRequest
```python
class AnsibleDeploymentRequest:
    deployment_type: str               # Type of deployment
                                       # Validation: Must be one of: NGINX, API, FULL
    environment: str                   # Target environment
                                       # Validation: Must be one of: Dev, UAT, Prod
    datacenter: str                    # Target datacenter
                                       # Validation: Must be one of: LADC, NYDC, EUDC, APDC
    version: str                       # Version to deploy
    change_number: str                 # ServiceNow change number for this operation
                                       # Validation: Must match pattern CHG\d{7}
    parameters: Dict                   # Additional parameters for deployment
```

#### AnsibleDeploymentResponse
```python
class AnsibleDeploymentResponse:
    deployment_id: str                 # Unique deployment identifier
    status: str                        # Deployment status
                                       # Validation: Must be one of: PENDING, RUNNING, COMPLETED, FAILED
    start_time: datetime               # Deployment start time
    end_time: Optional[datetime]       # Deployment end time
    logs_url: str                      # URL to deployment logs
    deployed_components: List[str]     # List of deployed components
```

#### AnsibleNginxDeploymentRequest
```python
class AnsibleNginxDeploymentRequest:
    vip_id: str                        # VIP identifier to deploy NGINX for
    environment: str                   # Target environment
                                       # Validation: Must be one of: Dev, UAT, Prod
    datacenter: str                    # Target datacenter
                                       # Validation: Must be one of: LADC, NYDC, EUDC, APDC
    nginx_version: str                 # NGINX version to deploy
    change_number: str                 # ServiceNow change number for this operation
                                       # Validation: Must match pattern CHG\d{7}
    vm_template: str                   # VM template to use for deployment
    cpu_count: int                     # Number of CPUs
                                       # Validation: Must be positive integer
    memory_mb: int                     # Memory in MB
                                       # Validation: Must be positive integer
    disk_gb: int                       # Disk size in GB
                                       # Validation: Must be positive integer
```

## Architecture

### System Components

#### 1. API Layer
- **API Gateway**: Entry point for all API requests
- **Authentication Service**: Handles JWT authentication
- **Authorization Service**: Handles role-based access control
- **Validation Service**: Validates all input data
- **API Controllers**: Handle specific API endpoints

#### 2. Business Logic Layer
- **VIP Service**: Manages VIP lifecycle
- **Entitlement Service**: Handles entitlement verification
- **Transformer Service**: Generates vendor-specific configurations
- **Promotion Service**: Manages environment promotion
- **Bluecat DDI Service**: Handles IP allocation and DNS registration via Bluecat
- **Change Management Service**: Validates change numbers
- **Ansible Deployment Service**: Manages deployments via Ansible

#### 3. Integration Layer
- **CMDB Connector**: Integrates with ServiceNow CMDB
- **Bluecat Connector**: Integrates with Bluecat DDI
- **Load Balancer Connector**: Integrates with load balancer devices
  - F5 AS3 Connector
  - AVI Connector
  - NGINX Connector
- **Change Management Connector**: Integrates with ServiceNow change management
- **Ansible Connector**: Integrates with Ansible for deployments
- **Certificate Authority Connector**: Integrates with certificate authority

#### 4. Data Layer
- **MongoDB**: Stores VIP configurations and transformer outputs
- **Cache**: Caches frequently accessed data
- **Audit Log**: Records all operations

#### 5. Monitoring Layer
- **Prometheus**: Collects metrics
- **Grafana**: Visualizes metrics
- **Alert Manager**: Manages alerts

### Component Interactions

#### VIP Creation Flow
1. **API Gateway** receives request with JWT token
2. **Authentication Service** validates token
3. **Authorization Service** checks user role
4. **Validation Service** validates input data
5. **Change Management Service** validates change number
6. **Entitlement Service** verifies entitlements via CMDB
7. **Bluecat DDI Service** allocates IP and registers DNS
8. **VIP Service** creates VIP configuration
9. **Transformer Service** generates vendor-specific configurations
10. **MongoDB** stores VIP configuration and transformer outputs
11. **Audit Log** records the operation
12. **API Gateway** returns response

#### Entitlement Verification Flow
1. **API Gateway** receives request with JWT token
2. **Authentication Service** validates token
3. **Authorization Service** checks user role
4. **Validation Service** validates input data
5. **Change Management Service** validates change number
6. **Entitlement Service** checks cache for recent results
7. If cache miss, **CMDB Connector** queries ServiceNow CMDB
8. **Entitlement Service** processes CMDB response
9. **Cache** stores results for future use
10. **Audit Log** records the operation
11. **API Gateway** returns response

#### Environment Promotion Flow
1. **API Gateway** receives request with JWT token
2. **Authentication Service** validates token
3. **Authorization Service** checks user role
4. **Validation Service** validates input data
5. **Change Management Service** validates change number
6. **VIP Service** retrieves source VIP configuration
7. **Promotion Service** applies environment-specific transformations
8. **Bluecat DDI Service** allocates new IP and registers DNS in target environment
9. **VIP Service** creates new VIP in target environment
10. **Transformer Service** generates vendor-specific configurations
11. **MongoDB** stores new VIP configuration and transformer outputs
12. **Audit Log** records the operation
13. **API Gateway** returns response

#### NGINX Deployment Flow
1. **API Gateway** receives request with JWT token
2. **Authentication Service** validates token
3. **Authorization Service** checks user role
4. **Validation Service** validates input data
5. **Change Management Service** validates change number
6. **VIP Service** retrieves VIP configuration
7. **Ansible Deployment Service** prepares deployment parameters
8. **Ansible Connector** executes deployment playbook
9. **Ansible Connector** monitors deployment status
10. **VIP Service** updates VIP configuration with deployment details
11. **MongoDB** stores updated VIP configuration
12. **Audit Log** records the operation
13. **API Gateway** returns response

### Deployment Architecture

#### Docker Container Structure
1. **API Container**: Hosts the API layer
   - Python 3.11 with FastAPI
   - JWT authentication
   - Input validation
   - API endpoints

2. **Business Logic Container**: Hosts the business logic layer
   - VIP service
   - Entitlement service
   - Transformer service
   - Promotion service
   - Bluecat DDI service
   - Change management service
   - Ansible deployment service

3. **MongoDB Container**: Hosts the database
   - Persistent storage volume
   - Replica set for high availability

4. **Cache Container**: Hosts the cache
   - Redis for fast access
   - Persistent storage for durability

5. **Integration Container**: Hosts the integration layer
   - CMDB connector
   - Bluecat connector
   - Load balancer connector
   - Change management connector
   - Ansible connector
   - Certificate authority connector

6. **Mock Services Container**: Hosts mock services for testing
   - ServiceNow mock
   - Bluecat DDI mock
   - Load balancer mock

7. **Monitoring Container**: Hosts monitoring services
   - Prometheus
   - Grafana
   - Alert Manager

#### Ansible Deployment Architecture
1. **Ansible Control Node**: Container with Ansible installed
   - Playbooks for deploying LBaaS components
   - Playbooks for deploying NGINX load balancers
   - Inventory management
   - Role-based deployment

2. **Ansible Playbooks**:
   - **LBaaS Deployment**: Deploys all LBaaS containers
   - **NGINX Deployment**: Deploys NGINX load balancers
   - **F5 Configuration**: Configures F5 load balancers
   - **AVI Configuration**: Configures AVI load balancers
   - **Monitoring Setup**: Configures Prometheus and Grafana

3. **Ansible Roles**:
   - **Docker**: Manages Docker installation and configuration
   - **MongoDB**: Manages MongoDB deployment and configuration
   - **Redis**: Manages Redis deployment and configuration
   - **API**: Manages API container deployment
   - **Business Logic**: Manages business logic container deployment
   - **Integration**: Manages integration container deployment
   - **NGINX**: Manages NGINX deployment and configuration
   - **Monitoring**: Manages Prometheus and Grafana deployment

#### Network Architecture
1. **API Network**: Connects API container to external clients
2. **Service Network**: Connects all service containers
3. **Database Network**: Connects service containers to database
4. **Integration Network**: Connects integration container to external systems
5. **Monitoring Network**: Connects monitoring containers

#### High Availability Design
1. **Multiple API Instances**: Load balanced API containers
2. **Service Redundancy**: Multiple instances of each service
3. **Database Replication**: MongoDB replica set
4. **Cache Clustering**: Redis cluster
5. **Health Monitoring**: Container health checks
6. **Auto-recovery**: Automatic container restart

#### Security Architecture
1. **Network Segmentation**: Separate networks for different components
2. **TLS Encryption**: HTTPS for all external communication
3. **JWT Authentication**: Secure token-based authentication
4. **Role-Based Access**: Fine-grained access control
5. **Secrets Management**: Environment variables or secrets manager
6. **Audit Logging**: Comprehensive logging of all operations

## Bluecat DDI Integration

### Overview
The LBaaS API integrates with Bluecat DDI for IP address management and DNS registration. This integration enables automated allocation of IP addresses and registration of DNS records for VIPs.

### Integration Components
1. **Bluecat Connector**: Integrates with Bluecat API
   - Authentication with Bluecat API
   - IP address allocation
   - DNS record management
   - Error handling and retry logic

2. **Bluecat DDI Service**: Business logic for Bluecat operations
   - IP address allocation workflow
   - DNS record registration workflow
   - Validation of Bluecat responses
   - Caching of Bluecat data

### Integration Workflows

#### IP Address Allocation
1. **Request Validation**: Validate IP allocation request
2. **Authentication**: Authenticate with Bluecat API
3. **Network Lookup**: Find appropriate network in Bluecat
4. **IP Allocation**: Allocate IP address from network
5. **DNS Registration**: Register A record for allocated IP
6. **Response Processing**: Process Bluecat response
7. **Error Handling**: Handle errors and retry if necessary

#### DNS Record Management
1. **Request Validation**: Validate DNS record request
2. **Authentication**: Authenticate with Bluecat API
3. **Zone Lookup**: Find appropriate zone in Bluecat
4. **Record Creation**: Create DNS record in zone
5. **PTR Creation**: Create PTR record if requested
6. **Response Processing**: Process Bluecat response
7. **Error Handling**: Handle errors and retry if necessary

### Configuration Requirements
1. **Bluecat API Endpoint**: URL of Bluecat API
2. **Authentication Credentials**: Username and password for Bluecat API
3. **Configuration Name**: Name of Bluecat configuration
4. **View Name**: Name of Bluecat DNS view
5. **Zone Names**: Names of Bluecat DNS zones
6. **Network IDs**: IDs of networks for IP allocation

## Ansible Deployment Integration

### Overview
The LBaaS API integrates with Ansible for automated deployment of components, particularly for deploying NGINX load balancers when needed based on environment choices.

### Integration Components
1. **Ansible Connector**: Integrates with Ansible API
   - Authentication with Ansible API
   - Playbook execution
   - Deployment monitoring
   - Error handling and retry logic

2. **Ansible Deployment Service**: Business logic for Ansible operations
   - Deployment workflow
   - Parameter preparation
   - Validation of Ansible responses
   - Status tracking

### Integration Workflows

#### NGINX Deployment
1. **Request Validation**: Validate NGINX deployment request
2. **Parameter Preparation**: Prepare parameters for Ansible playbook
3. **Playbook Selection**: Select appropriate Ansible playbook
4. **Playbook Execution**: Execute Ansible playbook
5. **Deployment Monitoring**: Monitor deployment status
6. **Response Processing**: Process Ansible response
7. **Error Handling**: Handle errors and retry if necessary

#### LBaaS Component Deployment
1. **Request Validation**: Validate LBaaS deployment request
2. **Parameter Preparation**: Prepare parameters for Ansible playbook
3. **Playbook Selection**: Select appropriate Ansible playbook
4. **Playbook Execution**: Execute Ansible playbook
5. **Deployment Monitoring**: Monitor deployment status
6. **Response Processing**: Process Ansible response
7. **Error Handling**: Handle errors and retry if necessary

### Configuration Requirements
1. **Ansible API Endpoint**: URL of Ansible API
2. **Authentication Credentials**: Username and password for Ansible API
3. **Playbook Paths**: Paths to Ansible playbooks
4. **Inventory Path**: Path to Ansible inventory
5. **Role Paths**: Paths to Ansible roles
6. **Variable Files**: Paths to Ansible variable files

## Data Flow Diagrams

### 1. VIP Creation Flow with Bluecat DDI
```
┌─────────┐     ┌─────────┐     ┌─────────────┐     ┌───────────┐
│  User   │────▶│  API    │────▶│ Validation  │────▶│  Change   │
└─────────┘     │ Gateway │     │  Service    │     │ Management│
                └─────────┘     └─────────────┘     └───────────┘
                     │                                    │
                     ▼                                    ▼
┌─────────┐     ┌─────────┐     ┌─────────────┐     ┌───────────┐
│ MongoDB │◀────│  VIP    │◀────│ Entitlement │◀────│ ServiceNow│
└─────────┘     │ Service │     │  Service    │     └───────────┘
                └─────────┘     └─────────────┘
                     │                │
                     ▼                ▼
                ┌─────────┐     ┌─────────────┐     ┌───────────┐
                │Transformer    │ Bluecat DDI │◀────│  Bluecat  │
                │ Service │     │  Service    │     │    API    │
                └─────────┘     └─────────────┘     └───────────┘
```

### 2. NGINX Deployment Flow with Ansible
```
┌─────────┐     ┌─────────┐     ┌─────────────┐     ┌───────────┐
│  User   │────▶│  API    │────▶│ Validation  │────▶│  Change   │
└─────────┘     │ Gateway │     │  Service    │     │ Management│
                └─────────┘     └─────────────┘     └───────────┘
                     │                                    │
                     ▼                                    ▼
┌─────────┐     ┌─────────┐     ┌─────────────┐     ┌───────────┐
│ MongoDB │◀───▶│  VIP    │◀───▶│  Ansible    │◀───▶│  Ansible  │
└─────────┘     │ Service │     │ Deployment  │     │    API    │
                └─────────┘     │  Service    │     └───────────┘
                     │          └─────────────┘
                     ▼                
                ┌─────────┐     
                │ Audit   │     
                │  Log    │     
                └─────────┘     
```

## Database Schema

### MongoDB Collections

#### 1. vips
- **_id**: ObjectId (Primary Key)
- **vip_id**: String (Unique identifier)
- **vip_fqdn**: String
- **vip_ip**: String
- **app_id**: String
- **environment**: String
- **datacenter**: String
- **region**: String
- **primary_contact_email**: String
- **secondary_contact_email**: String (Optional)
- **team_distribution_email**: String (Optional)
- **vip_type**: String (Enum: "l4", "l7")
- **monitor**: Object
  - **type**: String (Enum: "tcp", "udp", "http", "https", "ecv")
  - **port**: Number
  - **alternate_port**: Number (Optional)
  - **send**: String (Optional)
  - **receive**: String (Optional)
  - **interval**: Number
  - **timeout**: Number
  - **retries**: Number
- **persistence**: Object (Optional)
  - **type**: String (Enum: "source_ip", "cookie", "session")
  - **timeout**: Number
  - **cookie_name**: String (Optional)
  - **cookie_encryption**: Boolean (Optional)
- **ssl_cert_name**: String (Optional)
- **mtls_ca_cert_name**: String (Optional)
- **pool**: Array
  - **ip**: String
  - **port**: Number
  - **weight**: Number (Optional)
  - **priority_group**: Number (Optional)
  - **backup**: Boolean (Optional)
  - **app_id**: String
- **owner**: String
- **port**: Number
- **protocol**: String
- **lb_method**: String
- **priority_group**: Object (Optional)
  - **enabled**: Boolean
  - **groups**: Array
    - **id**: Number
    - **priority**: Number
    - **min_active_members**: Number (Optional)
- **created_at**: Date
- **updated_at**: Date
- **created_by**: String
- **updated_by**: String
- **change_number**: String
- **is_current**: Boolean (Indicates if this is the current version)
- **version**: Number (Version number)
- **bluecat_ip_allocation_id**: String (Reference to Bluecat IP allocation)
- **bluecat_dns_record_id**: String (Reference to Bluecat DNS record)
- **nginx_deployment_id**: String (Reference to NGINX deployment, if applicable)

#### 2. transformer_outputs
- **_id**: ObjectId (Primary Key)
- **vip_id**: String (Reference to vips collection)
- **vendor**: String
- **configuration**: Object (Vendor-specific configuration)
- **generated_at**: Date
- **generated_by**: String
- **change_number**: String

#### 3. entitlements_cache
- **_id**: ObjectId (Primary Key)
- **user_id**: String
- **server_id**: String
- **app_id**: String
- **entitled**: Boolean
- **reason**: String (Optional)
- **cached_at**: Date
- **expires_at**: Date

#### 4. audit_logs
- **_id**: ObjectId (Primary Key)
- **timestamp**: Date
- **user_id**: String
- **action**: String
- **resource_type**: String
- **resource_id**: String
- **change_number**: String
- **status**: String
- **details**: Object

#### 5. bluecat_allocations
- **_id**: ObjectId (Primary Key)
- **vip_id**: String (Reference to vips collection)
- **ip_address**: String
- **hostname**: String
- **fqdn**: String
- **object_id**: String (Bluecat object ID)
- **configuration_name**: String
- **view_name**: String
- **zone_name**: String
- **created_at**: Date
- **created_by**: String
- **change_number**: String

#### 6. bluecat_dns_records
- **_id**: ObjectId (Primary Key)
- **vip_id**: String (Reference to vips collection)
- **hostname**: String
- **fqdn**: String
- **ip_address**: String
- **record_type**: String
- **ttl**: Number
- **object_id**: String (Bluecat object ID)
- **ptr_record_id**: String (Optional)
- **configuration_name**: String
- **view_name**: String
- **zone_name**: String
- **created_at**: Date
- **created_by**: String
- **change_number**: String

#### 7. ansible_deployments
- **_id**: ObjectId (Primary Key)
- **deployment_id**: String (Unique identifier)
- **vip_id**: String (Reference to vips collection, if applicable)
- **deployment_type**: String
- **environment**: String
- **datacenter**: String
- **version**: String
- **status**: String
- **start_time**: Date
- **end_time**: Date (Optional)
- **logs_url**: String
- **deployed_components**: Array
- **playbook**: String
- **inventory**: String
- **parameters**: Object
- **created_by**: String
- **change_number**: String

## API Gateway Configuration

### Routes
- **/api/v1/vips**: VIP management endpoints
- **/api/v1/entitlements**: Entitlement verification endpoints
- **/api/v1/transformers**: Transformer endpoints
- **/api/v1/promotion**: Environment promotion endpoints
- **/api/v1/bluecat**: Bluecat DDI endpoints
- **/api/v1/ansible**: Ansible deployment endpoints
- **/api/v1/mock**: Mock service endpoints

### Middleware
1. **Authentication**: JWT validation
2. **Authorization**: Role-based access control
3. **Validation**: Request validation
4. **Logging**: Request/response logging
5. **Rate Limiting**: Request rate limiting
6. **Error Handling**: Standardized error responses

### Security
1. **TLS**: HTTPS encryption
2. **CORS**: Cross-Origin Resource Sharing configuration
3. **CSP**: Content Security Policy
4. **XSS Protection**: Cross-Site Scripting protection
5. **CSRF Protection**: Cross-Site Request Forgery protection

## Monitoring and Observability

### Prometheus Metrics
1. **VIP Status**: Status of each VIP
2. **Pool Member Status**: Status of each pool member
3. **Request Count**: Number of requests per VIP
4. **Connection Count**: Number of active connections per VIP
5. **Throughput**: Throughput per VIP
6. **API Request Count**: Number of API requests
7. **API Response Time**: Response time of API endpoints
8. **Error Count**: Number of errors
9. **Deployment Status**: Status of deployments

### Grafana Dashboards
1. **VIP Overview**: Overview of all VIPs
2. **Pool Member Health**: Health of all pool members
3. **Traffic Overview**: Traffic overview for all VIPs
4. **API Performance**: Performance of API endpoints
5. **Deployment Status**: Status of deployments
6. **System Health**: Health of LBaaS components

### Alerting
1. **VIP Down**: Alert when VIP is down
2. **Pool Member Down**: Alert when pool member is down
3. **High Error Rate**: Alert when error rate is high
4. **High Response Time**: Alert when response time is high
5. **Deployment Failure**: Alert when deployment fails
6. **Certificate Expiry**: Alert when certificate is about to expire

## Conclusion

This document provides a comprehensive overview of the data models and architecture for the LBaaS API, with specific focus on Bluecat DDI integration and Ansible deployment automation. The design incorporates best practices from industry leaders like AppViewX and Imperva, while addressing specific requirements for entitlement verification, change management, and multi-vendor support. The architecture is designed to be scalable, secure, and maintainable, with clear separation of concerns and well-defined interfaces between components.
