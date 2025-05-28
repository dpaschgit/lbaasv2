# LBaaS API Design

## Overview
This document outlines the design for a Load Balancing as a Service (LBaaS) API. The API provides CRUD operations for Virtual IPs (VIPs), entitlement verification through ServiceNow CMDB integration, and a standard output format for vendor-specific transformers.

## API Endpoints

### VIP Management

#### 1. Create VIP
- **Endpoint**: `/api/v1/vips`
- **Method**: POST
- **Description**: Creates a new VIP configuration
- **Request Body**: VipBase model
- **Response**: VipCreate model
- **Authorization**: Requires valid authentication and entitlement verification
- **CMDB Integration**: Verifies user has rights to servers being added to VIP

#### 2. Get VIP
- **Endpoint**: `/api/v1/vips/{vip_id}`
- **Method**: GET
- **Description**: Retrieves a specific VIP configuration
- **Parameters**: vip_id (path)
- **Response**: VipBase model
- **Authorization**: Requires valid authentication

#### 3. List VIPs
- **Endpoint**: `/api/v1/vips`
- **Method**: GET
- **Description**: Lists all VIPs or filters by query parameters
- **Parameters**: Various filter options (query)
- **Response**: List of VipBase models
- **Authorization**: Requires valid authentication

#### 4. Update VIP
- **Endpoint**: `/api/v1/vips/{vip_id}`
- **Method**: PUT
- **Description**: Updates an existing VIP configuration
- **Parameters**: vip_id (path)
- **Request Body**: VipUpdate model
- **Response**: Updated VipBase model
- **Authorization**: Requires valid authentication and entitlement verification
- **CMDB Integration**: Verifies user has rights to servers being modified

#### 5. Delete VIP
- **Endpoint**: `/api/v1/vips/{vip_id}`
- **Method**: DELETE
- **Description**: Deletes a VIP configuration
- **Parameters**: vip_id (path)
- **Response**: Success message
- **Authorization**: Requires valid authentication

### Entitlement Verification

#### 1. Verify Entitlement
- **Endpoint**: `/api/v1/entitlements/verify`
- **Method**: POST
- **Description**: Verifies user entitlements for specific servers
- **Request Body**: List of server IDs
- **Response**: Entitlement verification result
- **CMDB Integration**: Queries ServiceNow CMDB for entitlement data

#### 2. Get User Entitlements
- **Endpoint**: `/api/v1/entitlements/user`
- **Method**: GET
- **Description**: Retrieves all servers a user has entitlements for
- **Response**: List of server IDs and details
- **CMDB Integration**: Queries ServiceNow CMDB for user entitlement data

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

## Data Models

### VipBase
```
class VipBase:
    vip_fqdn: str                      # Fully Qualified Domain Name of the VIP
    vip_ip: Optional[str]              # IP address of the VIP (can be auto-assigned)
    app_id: str                        # Application identifier
    environment: str                   # Deployment environment (e.g., Dev, UAT, Prod)
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

### VipCreate (extends VipBase)
```
class VipCreate(VipBase):
    pass  # Inherits all fields from VipBase
```

### VipUpdate (extends BaseModel)
```
class VipUpdate:
    vip_fqdn: Optional[str]
    vip_ip: Optional[str]
    app_id: Optional[str]
    environment: Optional[str]
    datacenter: Optional[str]
    primary_contact_email: Optional[EmailStr]
    secondary_contact_email: Optional[EmailStr]
    team_distribution_email: Optional[EmailStr]
    monitor: Optional[Monitor]
    persistence: Optional[Persistence]
    ssl_cert_name: Optional[str]
    mtls_ca_cert_name: Optional[str]
    pool: Optional[List[PoolMember]]
    owner: Optional[str]
    port: Optional[int]
    protocol: Optional[str]
    lb_method: Optional[str]
```

### Monitor
```
class Monitor:
    type: str                          # Type of health monitor (e.g., HTTP, TCP, ICMP)
    port: int                          # Port to use for health monitoring
    send: Optional[str]                # String to send for active health checks
    receive: Optional[str]             # Expected string to receive for successful health check
```

### Persistence
```
class Persistence:
    type: str                          # Type of session persistence
    timeout: int                       # Timeout for persistence record in seconds
```

### PoolMember
```
class PoolMember:
    ip: str                            # IP address of the backend server
    port: int                          # Port of the backend server
```

### EntitlementVerification
```
class EntitlementVerification:
    server_ids: List[str]              # List of server IDs to verify entitlements for
```

### EntitlementResult
```
class EntitlementResult:
    server_id: str                     # Server ID
    entitled: bool                     # Whether the user is entitled to this server
    reason: Optional[str]              # Reason for entitlement decision
```

### PromotionOptions
```
class PromotionOptions:
    override_environment_specific: bool  # Whether to override environment-specific data
    specific_overrides: Dict[str, Any]   # Specific fields to override during promotion
```

## Common JSON Output Format

The API will use a standardized JSON schema for all load balancer translators, making it easier to add support for new load balancer vendors in the future. The schema includes:

1. **VIP Configuration**: Basic VIP settings like FQDN, IP, port, protocol
2. **Pool Configuration**: Backend server details
3. **Health Monitoring**: Health check settings
4. **Persistence**: Session persistence settings
5. **SSL/TLS**: Certificate references and settings
6. **Load Balancing Method**: Algorithm used for load distribution

## Docker Containerization

The LBaaS API will be containerized using Docker for easy deployment and scaling:

1. **Base Image**: Python 3.11 slim
2. **Dependencies**: All required Python packages specified in requirements.txt
3. **MongoDB**: Separate container for the MongoDB database
4. **API Gateway**: Optional container for API gateway functionality
5. **Docker Compose**: Configuration for multi-container deployment
6. **Environment Variables**: Configuration via environment variables
7. **Volume Mounts**: Persistent storage for MongoDB data
8. **Network Configuration**: Internal network for container communication
9. **Health Checks**: Container health monitoring
10. **Scalability**: Support for horizontal scaling

## ServiceNow CMDB Integration

The API will integrate with ServiceNow CMDB for entitlement verification:

1. **Authentication**: Service account for CMDB access
2. **API Calls**: REST API calls to query CMDB data
3. **Caching**: Cache CMDB responses to reduce API calls
4. **Error Handling**: Graceful handling of CMDB unavailability
5. **Logging**: Audit logging of all CMDB queries

## Security Considerations

1. **Authentication**: JWT-based authentication
2. **Authorization**: Role-based access control
3. **Input Validation**: Strict validation of all inputs
4. **Rate Limiting**: Protection against abuse
5. **Audit Logging**: Comprehensive logging of all operations
6. **Secure Communication**: HTTPS for all API endpoints
7. **Secrets Management**: Secure handling of credentials and secrets
