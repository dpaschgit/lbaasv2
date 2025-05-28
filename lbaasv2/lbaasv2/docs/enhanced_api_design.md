# Enhanced LBaaS API Design

## Overview
This document outlines the enhanced design for a Load Balancing as a Service (LBaaS) API. The API provides CRUD operations for Virtual IPs (VIPs), entitlement verification through ServiceNow CMDB integration, and a standard output format for vendor-specific transformers.

## API Endpoints

### VIP Management

#### 1. Create VIP
- **Endpoint**: `/api/v1/vips`
- **Method**: POST
- **Description**: Creates a new VIP configuration
- **Request Body**: VipBase model
- **Response**: VipCreate model
- **Authorization**: Requires valid authentication and entitlement verification (admin users bypass entitlement checks)
- **CMDB Integration**: Verifies user has rights to servers being added to VIP

#### 2. Get VIP
- **Endpoint**: `/api/v1/vips/{vip_id}`
- **Method**: GET
- **Description**: Retrieves a specific VIP configuration
- **Parameters**: vip_id (path)
- **Response**: VipBase model
- **Authorization**: Requires valid authentication (admin users can access all VIPs)

#### 3. List VIPs
- **Endpoint**: `/api/v1/vips`
- **Method**: GET
- **Description**: Lists all VIPs or filters by query parameters
- **Parameters**: Various filter options (query)
- **Response**: List of VipBase models
- **Authorization**: Requires valid authentication (admin users see all VIPs, regular users see only entitled VIPs)

#### 4. Update VIP
- **Endpoint**: `/api/v1/vips/{vip_id}`
- **Method**: PUT
- **Description**: Updates an existing VIP configuration
- **Parameters**: vip_id (path)
- **Request Body**: VipUpdate model
- **Response**: Updated VipBase model
- **Authorization**: Requires valid authentication and entitlement verification (admin users bypass entitlement checks)
- **CMDB Integration**: Verifies user has rights to servers being modified

#### 5. Delete VIP
- **Endpoint**: `/api/v1/vips/{vip_id}`
- **Method**: DELETE
- **Description**: Deletes a VIP configuration
- **Parameters**: vip_id (path)
- **Response**: Success message
- **Authorization**: Requires valid authentication (admin users can delete any VIP)

### Entitlement Verification

#### 1. Verify Entitlement
- **Endpoint**: `/api/v1/entitlements/verify`
- **Method**: POST
- **Description**: Verifies user entitlements for specific servers
- **Request Body**: List of server IDs
- **Response**: Entitlement verification result
- **CMDB Integration**: Queries ServiceNow CMDB for entitlement data based on appids

#### 2. Get User Entitlements
- **Endpoint**: `/api/v1/entitlements/user`
- **Method**: GET
- **Description**: Retrieves all servers a user has entitlements for
- **Response**: List of server IDs and details
- **CMDB Integration**: Queries ServiceNow CMDB for user entitlement data based on appids

### Load Balancer Transformers

#### 1. Get Transformer Output
- **Endpoint**: `/api/v1/transformers/{vip_id}/{vendor}`
- **Method**: GET
- **Description**: Retrieves vendor-specific transformer output for a VIP
- **Parameters**: vip_id (path), vendor (path)
- **Response**: Vendor-specific configuration in standard JSON format
- **Authorization**: Requires valid authentication

#### 2. List Supported Vendors
- **Endpoint**: `/api/v1/transformers/vendors`
- **Method**: GET
- **Description**: Lists all supported load balancer vendors
- **Response**: List of vendor names and capabilities
- **Authorization**: Requires valid authentication

### Environment Promotion

#### 1. Promote VIP Configuration
- **Endpoint**: `/api/v1/promotion/{vip_id}/{target_environment}`
- **Method**: POST
- **Description**: Promotes VIP configuration to target environment
- **Parameters**: vip_id (path), target_environment (path)
- **Request Body**: Promotion options
- **Response**: Promotion result
- **Authorization**: Requires valid authentication
- **Special Handling**: Handles environment-specific data points that should not be automatically promoted

### IPAM Integration

#### 1. Allocate IP Address
- **Endpoint**: `/api/v1/ipam/allocate`
- **Method**: POST
- **Description**: Allocates an IP address for a VIP
- **Request Body**: IP allocation request with network details
- **Response**: Allocated IP information
- **Authorization**: Requires valid authentication

#### 2. Release IP Address
- **Endpoint**: `/api/v1/ipam/release/{ip_address}`
- **Method**: DELETE
- **Description**: Releases an allocated IP address
- **Parameters**: ip_address (path)
- **Response**: Success message
- **Authorization**: Requires valid authentication

#### 3. Register DNS Record
- **Endpoint**: `/api/v1/ipam/dns`
- **Method**: POST
- **Description**: Registers a DNS record for a VIP
- **Request Body**: DNS record details
- **Response**: DNS registration result
- **Authorization**: Requires valid authentication

## Data Models

### VipBase
```
class VipBase:
    vip_fqdn: str                      # Fully Qualified Domain Name of the VIP
    vip_ip: Optional[str]              # IP address of the VIP (can be auto-assigned via IPAM)
    app_id: str                        # Application identifier
    environment: str                   # Deployment environment (e.g., Dev, UAT, Prod)
    datacenter: str                    # Datacenter where the VIP is provisioned
    region: str                        # Region where the VIP is provisioned
    primary_contact_email: EmailStr    # Primary contact email
    secondary_contact_email: Optional[EmailStr]  # Secondary contact email
    team_distribution_email: Optional[EmailStr]  # Team distribution email
    vip_type: VipType                  # L4 or L7 VIP
    monitor: Monitor                   # Health monitoring configuration
    persistence: Optional[Persistence] # Session persistence configuration
    ssl_cert_name: Optional[str]       # SSL certificate name/reference (not stored)
    mtls_ca_cert_name: Optional[str]   # mTLS CA certificate name/reference (not stored)
    pool: List[PoolMember]             # List of backend servers in the pool
    owner: str                         # Owner or creator of the VIP
    port: int                          # Listening port for the VIP
    protocol: str                      # Protocol for the VIP (e.g., TCP, HTTP, HTTPS)
    lb_method: str                     # Load balancing method
    priority_group: Optional[PriorityGroup]  # Priority group configuration
```

### VipType (Enum)
```
class VipType(Enum):
    L4 = "l4"                          # Layer 4 VIP
    L7 = "l7"                          # Layer 7 VIP
```

### Monitor
```
class Monitor:
    type: MonitorType                  # Type of health monitor (TCP, UDP, HTTP)
    port: int                          # Port to use for health monitoring
    alternate_port: Optional[int]      # Alternate port for TCP monitors
    send: Optional[str]                # String to send for active health checks
    receive: Optional[str]             # Expected string to receive for successful health check
    interval: int                      # Interval between health checks in seconds
    timeout: int                       # Timeout for health check in seconds
    retries: int                       # Number of retries before marking as down
```

### MonitorType (Enum)
```
class MonitorType(Enum):
    TCP = "tcp"                        # TCP monitor
    UDP = "udp"                        # UDP monitor
    HTTP = "http"                      # HTTP monitor
    HTTPS = "https"                    # HTTPS monitor
    ECV = "ecv"                        # Enhanced Content Verification monitor
```

### Persistence
```
class Persistence:
    type: PersistenceType              # Type of session persistence
    timeout: int                       # Timeout for persistence record in seconds
    cookie_name: Optional[str]         # Cookie name for cookie persistence
    cookie_encryption: Optional[bool]  # Whether to encrypt the cookie
```

### PersistenceType (Enum)
```
class PersistenceType(Enum):
    SOURCE_IP = "source_ip"            # Source IP persistence
    COOKIE = "cookie"                  # Cookie-based persistence
    SESSION = "session"                # Session-based persistence
```

### PoolMember
```
class PoolMember:
    ip: str                            # IP address of the backend server
    port: int                          # Port of the backend server
    weight: Optional[int]              # Weight for load balancing
    priority_group: Optional[int]      # Priority group ID
    backup: Optional[bool]             # Whether this is a backup server
    app_id: str                        # Application ID of the server
```

### PriorityGroup
```
class PriorityGroup:
    enabled: bool                      # Whether priority groups are enabled
    groups: List[PriorityGroupConfig]  # List of priority group configurations
```

### PriorityGroupConfig
```
class PriorityGroupConfig:
    id: int                            # Priority group ID
    priority: int                      # Priority level (lower is higher priority)
    min_active_members: Optional[int]  # Minimum active members before failing over
```

### LBMethod (Enum)
```
class LBMethod(Enum):
    ROUND_ROBIN = "round_robin"        # Round Robin load balancing
    LEAST_CONNECTIONS = "least_connections"  # Least Connections load balancing
    PRIORITY_GROUP = "priority_group"  # Priority Group-based load balancing
```

### EntitlementVerification
```
class EntitlementVerification:
    server_ids: List[str]              # List of server IDs to verify entitlements for
    app_ids: Optional[List[str]]       # Optional list of application IDs for verification
```

### EntitlementResult
```
class EntitlementResult:
    server_id: str                     # Server ID
    app_id: str                        # Application ID
    entitled: bool                     # Whether the user is entitled to this server
    reason: Optional[str]              # Reason for entitlement decision
```

### UserRole (Enum)
```
class UserRole(Enum):
    ADMIN = "admin"                    # Administrator with access to all resources
    USER = "user"                      # Regular user with limited access
```

### User
```
class User:
    id: str                            # User ID
    username: str                      # Username
    email: EmailStr                    # Email address
    role: UserRole                     # User role
    app_ids: List[str]                 # List of application IDs the user has access to
```

### IPAllocationRequest
```
class IPAllocationRequest:
    network: str                       # Network to allocate from
    hostname: str                      # Hostname for the IP
    app_id: str                        # Application ID
    environment: str                   # Environment
    datacenter: str                    # Datacenter
    region: str                        # Region
```

### IPAllocationResponse
```
class IPAllocationResponse:
    ip_address: str                    # Allocated IP address
    subnet_mask: str                   # Subnet mask
    gateway: str                       # Gateway
    dns_servers: List[str]             # DNS servers
    hostname: str                      # Hostname
```

### DNSRecordRequest
```
class DNSRecordRequest:
    hostname: str                      # Hostname
    ip_address: str                    # IP address
    record_type: str                   # Record type (A, CNAME, etc.)
    ttl: int                           # Time to live
    app_id: str                        # Application ID
```

### DNSRecordResponse
```
class DNSRecordResponse:
    hostname: str                      # Hostname
    fqdn: str                          # Fully qualified domain name
    ip_address: str                    # IP address
    record_type: str                   # Record type
    ttl: int                           # Time to live
```

## Common JSON Output Format

The API will use a standardized JSON schema for all load balancer translators, making it easier to add support for new load balancer vendors in the future. The schema includes:

1. **VIP Configuration**:
   - Basic VIP settings (FQDN, IP, port, protocol)
   - VIP type (L4 or L7)
   - Application ID

2. **Pool Configuration**:
   - Backend server details
   - Priority groups
   - Server weights

3. **Health Monitoring**:
   - Monitor type (TCP, UDP, HTTP, ECV)
   - Monitor settings
   - Alternate port configuration

4. **Persistence**:
   - Persistence type (source IP, cookie, session)
   - Timeout settings
   - Cookie configuration

5. **SSL/TLS**:
   - Certificate references (not stored)
   - mTLS settings

6. **Load Balancing Method**:
   - Algorithm (Round Robin, Least Connections)
   - Priority group configuration

## Docker Containerization

The LBaaS API will be containerized using Docker for easy deployment and scaling:

1. **Base Image**: Python 3.11 slim
2. **Dependencies**: All required Python packages specified in requirements.txt
3. **MongoDB**: Separate container for the MongoDB database
4. **API Gateway**: Optional container for API gateway functionality
5. **IPAM/DNS**: Container for opensource IPAM/DNS for lab testing
6. **Docker Compose**: Configuration for multi-container deployment
7. **Environment Variables**: Configuration via environment variables
8. **Volume Mounts**: Persistent storage for MongoDB data
9. **Network Configuration**: Internal network for container communication
10. **Health Checks**: Container health monitoring
11. **Scalability**: Support for horizontal scaling

## ServiceNow CMDB Integration

The API will integrate with ServiceNow CMDB for entitlement verification:

1. **Data Structure**:
   - Device information
   - Device IP
   - Owner information (owner1, owner2)
   - Owner email distribution list
   - Environment
   - Datacenter
   - Region
   - Application ID

2. **Authentication**: Service account for CMDB access
3. **API Calls**: REST API calls to query CMDB data
4. **Caching**: Cache CMDB responses to reduce API calls
5. **Error Handling**: Graceful handling of CMDB unavailability
6. **Logging**: Audit logging of all CMDB queries

## IPAM/DNS Integration

The API will integrate with an opensource IPAM/DNS solution for lab testing:

1. **IP Allocation**: Allocate IP addresses for VIPs
2. **IP Release**: Release IP addresses when VIPs are deleted
3. **DNS Registration**: Register DNS records for VIPs
4. **DNS Removal**: Remove DNS records when VIPs are deleted
5. **API Compatibility**: Ensure API calls are compatible with real products

## Security Considerations

1. **Authentication**: JWT-based authentication
2. **Authorization**:
   - Role-based access control
   - Admin users have access to all resources
   - Regular users have access based on application IDs
3. **Input Validation**: Strict validation of all inputs
4. **Rate Limiting**: Protection against abuse
5. **Audit Logging**: Comprehensive logging of all operations
6. **Secure Communication**: HTTPS for all API endpoints
7. **Secrets Management**: Secure handling of credentials and secrets
8. **Certificate Handling**: References only, no storage of actual certificates
