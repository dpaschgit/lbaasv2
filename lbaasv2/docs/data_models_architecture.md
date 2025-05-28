# LBaaS API Data Models and Architecture

## Overview
This document details the data models and architecture for the Load Balancing as a Service (LBaaS) API, incorporating requirements from stakeholder input and competitive analysis of industry solutions like AppViewX and Imperva.

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

### IPAM/DNS Models

#### IPAllocationRequest
```python
class IPAllocationRequest:
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
```

#### IPAllocationResponse
```python
class IPAllocationResponse:
    ip_address: str                    # Allocated IP address
                                       # Validation: Must be valid IPv4 format
    subnet_mask: str                   # Subnet mask
    gateway: str                       # Gateway
                                       # Validation: Must be valid IPv4 format
    dns_servers: List[str]             # DNS servers
                                       # Validation: Each must be valid IPv4 format
    hostname: str                      # Hostname
```

#### DNSRecordRequest
```python
class DNSRecordRequest:
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
```

#### DNSRecordResponse
```python
class DNSRecordResponse:
    hostname: str                      # Hostname
    fqdn: str                          # Fully qualified domain name
                                       # Validation: Must be valid FQDN format
    ip_address: str                    # IP address
                                       # Validation: Must be valid IPv4 format
    record_type: str                   # Record type
                                       # Validation: Must be one of: A, CNAME, AAAA, TXT
    ttl: int                           # Time to live
                                       # Validation: Must be at least 60
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
- **IPAM Service**: Handles IP allocation and DNS registration
- **Change Management Service**: Validates change numbers

#### 3. Integration Layer
- **CMDB Connector**: Integrates with ServiceNow CMDB
- **IPAM Connector**: Integrates with IPAM/DNS systems
- **Load Balancer Connector**: Integrates with load balancer devices
- **Change Management Connector**: Integrates with ServiceNow change management

#### 4. Data Layer
- **MongoDB**: Stores VIP configurations and transformer outputs
- **Cache**: Caches frequently accessed data
- **Audit Log**: Records all operations

### Component Interactions

#### VIP Creation Flow
1. **API Gateway** receives request with JWT token
2. **Authentication Service** validates token
3. **Authorization Service** checks user role
4. **Validation Service** validates input data
5. **Change Management Service** validates change number
6. **Entitlement Service** verifies entitlements via CMDB
7. **IPAM Service** allocates IP and registers DNS if needed
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
8. **IPAM Service** allocates new IP and registers DNS in target environment
9. **VIP Service** creates new VIP in target environment
10. **Transformer Service** generates vendor-specific configurations
11. **MongoDB** stores new VIP configuration and transformer outputs
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
   - IPAM service
   - Change management service

3. **MongoDB Container**: Hosts the database
   - Persistent storage volume
   - Replica set for high availability

4. **Cache Container**: Hosts the cache
   - Redis for fast access
   - Persistent storage for durability

5. **Integration Container**: Hosts the integration layer
   - CMDB connector
   - IPAM connector
   - Load balancer connector
   - Change management connector

6. **Mock Services Container**: Hosts mock services for testing
   - ServiceNow mock
   - IPAM/DNS mock
   - Load balancer mock

#### Network Architecture
1. **API Network**: Connects API container to external clients
2. **Service Network**: Connects all service containers
3. **Database Network**: Connects service containers to database
4. **Integration Network**: Connects integration container to external systems

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

## Data Flow Diagrams

### 1. VIP Creation Flow
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
                ┌─────────┐     ┌─────────────┐
                │Transformer    │ IPAM/DNS    │
                │ Service │     │  Service    │
                └─────────┘     └─────────────┘
```

### 2. Entitlement Verification Flow
```
┌─────────┐     ┌─────────┐     ┌─────────────┐     ┌───────────┐
│  User   │────▶│  API    │────▶│ Validation  │────▶│  Change   │
└─────────┘     │ Gateway │     │  Service    │     │ Management│
                └─────────┘     └─────────────┘     └───────────┘
                     │                                    │
                     ▼                                    ▼
┌─────────┐     ┌─────────────┐     ┌───────────┐     ┌───────────┐
│  Cache  │◀───▶│ Entitlement │◀───▶│   CMDB    │◀───▶│ ServiceNow│
└─────────┘     │  Service    │     │ Connector │     └───────────┘
                └─────────────┘     └───────────┘
                     │
                     ▼
                ┌─────────┐
                │ Audit   │
                │  Log    │
                └─────────┘
```

### 3. Environment Promotion Flow
```
┌─────────┐     ┌─────────┐     ┌─────────────┐     ┌───────────┐
│  User   │────▶│  API    │────▶│ Validation  │────▶│  Change   │
└─────────┘     │ Gateway │     │  Service    │     │ Management│
                └─────────┘     └─────────────┘     └───────────┘
                     │                                    │
                     ▼                                    ▼
┌─────────┐     ┌─────────────┐     ┌───────────┐     ┌───────────┐
│ MongoDB │◀───▶│ Promotion   │◀───▶│   VIP     │◀───▶│ IPAM/DNS  │
└─────────┘     │  Service    │     │  Service  │     │  Service  │
                └─────────────┘     └───────────┘     └───────────┘
                     │                    │
                     ▼                    ▼
                ┌─────────────┐     ┌───────────┐
                │ Transformer │     │  Audit    │
                │  Service    │     │   Log     │
                └─────────────┘     └───────────┘
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

## API Gateway Configuration

### Routes
- **/api/v1/vips**: VIP management endpoints
- **/api/v1/entitlements**: Entitlement verification endpoints
- **/api/v1/transformers**: Transformer endpoints
- **/api/v1/promotion**: Environment promotion endpoints
- **/api/v1/ipam**: IPAM/DNS endpoints
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

## Conclusion

This document provides a comprehensive overview of the data models and architecture for the LBaaS API. The design incorporates best practices from industry leaders like AppViewX and Imperva, while addressing specific requirements for entitlement verification, change management, and multi-vendor support. The architecture is designed to be scalable, secure, and maintainable, with clear separation of concerns and well-defined interfaces between components.
