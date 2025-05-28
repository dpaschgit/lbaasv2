# Enhanced LBaaS API Requirements and Design

## Overview
This document integrates findings from competitive analysis of industry-leading solutions (AppViewX and Imperva) with our existing requirements to create a comprehensive design for a Load Balancing as a Service (LBaaS) API. The design focuses on automation, integration, security, and scalability to deliver a robust service offering.

## Core Requirements

### 1. VIP Management (CRUD Operations)
- **Create new VIPs** with specified configurations
  - Support for both L4 and L7 VIPs
  - Multiple persistence options: Source IP, session, and cookie
  - Various load balancing methods: Round Robin, Least Connections, and Priority Groups
  - Comprehensive monitoring: TCP, UDP, and HTTP ECV monitors with alternate port support
  - mTLS support without storing certificates
- **Read/Retrieve** existing VIP configurations
- **Update** VIP configurations
- **Delete** VIPs
- **All operations require valid change numbers** validated against ServiceNow

### 2. Entitlement Verification
- Query ServiceNow CMDB for entitlement verification
- Prevent users from adding servers they don't have rights to behind a VIP
- Validate user permissions before allowing VIP modifications
- CMDB structure: device:device IP: owner1:owner2:owner email distro: environment; datacenter: region
- Admin users bypass entitlement restrictions with access to all resources
- All devices and users have assigned or accessible application IDs (appids)

### 3. Standard Output Format
- Common, vendor-agnostic JSON output format
- Support for transformers for different load balancer vendors
- Easy addition of new load balancer products/vendors
- API-compliant calls to MongoDB and ServiceNow

### 4. Storage Requirements
- Store LBaaS configurations in a dedicated MongoDB database
- Keep configurations separate from ServiceNow CMDB data
- Store both latest and last configuration for each VIP
- Store translator outputs in MongoDB (not in files)

### 5. Integration Requirements
- ServiceNow CMDB for entitlement verification
- IPAM/DNS integration for IP allocation and DNS registration
- API gateway for load balancer device communication
- Support for multiple vendor-specific transformers
- Change management integration for all CRUD operations

### 6. Documentation Requirements
- Complete Swagger/OpenAPI documentation for all endpoints
- Request/response examples
- Authentication and authorization methods documentation
- Validation rules documentation

### 7. Deployment Requirements
- Docker-based containerization
- Scalable architecture
- High availability design
- Support for multiple environments (Dev, UAT, Prod)

## Enhanced Features from Competitive Analysis

### 1. Automation Workflows
- Template-based VIP creation
- Environment promotion with special handling for environment-specific data
- Approval workflows integrated with change management
- Rollback capabilities for failed operations
- Scheduled operations support

### 2. Advanced Health Monitoring
- Multiple health check types (TCP, UDP, HTTP, HTTPS, ECV)
- Customizable check intervals and thresholds
- Automatic failover configuration
- Detailed health metrics collection
- Both passive and active monitoring options

### 3. Multi-vendor Support
- Vendor-agnostic data models
- Extensible architecture for adding new vendors
- Standardized output format for all vendors
- Vendor capability discovery

### 4. Security Enhancements
- Role-based access control with admin override
- Certificate lifecycle management (references only)
- Security policy enforcement
- Comprehensive audit logging
- Secure API access with JWT authentication

### 5. Compliance and Governance
- Configuration validation against best practices
- Compliance checking for industry standards
- Change management integration with validation
- Detailed audit trails for all operations
- Configuration drift detection

## API Design

### Authentication and Authorization
- JWT-based authentication
- Role-based access control
- Admin role with full access
- Regular users with entitlement-based access
- ServiceNow integration for change validation

### VIP Management Endpoints

#### 1. Create VIP
- **Endpoint**: `/api/v1/vips`
- **Method**: POST
- **Required Parameters**: 
  - change_number (query)
- **Request Body**: VipCreate model
- **Response**: VipBase model
- **Features**:
  - Entitlement verification
  - Change number validation
  - IPAM integration for IP allocation
  - DNS registration
  - Validation of all input fields

#### 2. Get VIP
- **Endpoint**: `/api/v1/vips/{vip_id}`
- **Method**: GET
- **Required Parameters**: 
  - vip_id (path)
  - change_number (query)
- **Response**: VipBase model
- **Features**:
  - Role-based access control
  - Change number validation

#### 3. List VIPs
- **Endpoint**: `/api/v1/vips`
- **Method**: GET
- **Required Parameters**: 
  - change_number (query)
- **Optional Parameters**:
  - app_id, environment, datacenter, region, owner, vip_type (query)
- **Response**: List of VipBase models
- **Features**:
  - Filtering options
  - Role-based access control
  - Change number validation

#### 4. Update VIP
- **Endpoint**: `/api/v1/vips/{vip_id}`
- **Method**: PUT
- **Required Parameters**: 
  - vip_id (path)
  - change_number (query)
- **Request Body**: VipUpdate model
- **Response**: Updated VipBase model
- **Features**:
  - Entitlement verification
  - Change number validation
  - Validation of all input fields
  - Previous configuration preservation

#### 5. Delete VIP
- **Endpoint**: `/api/v1/vips/{vip_id}`
- **Method**: DELETE
- **Required Parameters**: 
  - vip_id (path)
  - change_number (query)
- **Response**: Success message
- **Features**:
  - Role-based access control
  - Change number validation
  - IPAM/DNS cleanup

### Entitlement Verification Endpoints

#### 1. Verify Entitlement
- **Endpoint**: `/api/v1/entitlements/verify`
- **Method**: POST
- **Required Parameters**: 
  - change_number (query)
- **Request Body**: EntitlementVerification model
- **Response**: EntitlementResultList model
- **Features**:
  - ServiceNow CMDB integration
  - App ID-based verification
  - Detailed reason for entitlement decisions

#### 2. Get User Entitlements
- **Endpoint**: `/api/v1/entitlements/user`
- **Method**: GET
- **Required Parameters**: 
  - change_number (query)
- **Response**: UserEntitlements model
- **Features**:
  - ServiceNow CMDB integration
  - App ID-based listing
  - Role-based access control

### Load Balancer Transformers

#### 1. Get Transformer Output
- **Endpoint**: `/api/v1/transformers/{vip_id}/{vendor}`
- **Method**: GET
- **Required Parameters**: 
  - vip_id (path)
  - vendor (path)
  - change_number (query)
- **Response**: TransformerOutput model
- **Features**:
  - Vendor-specific configuration generation
  - Standard JSON format
  - Role-based access control

#### 2. List Supported Vendors
- **Endpoint**: `/api/v1/transformers/vendors`
- **Method**: GET
- **Required Parameters**: 
  - change_number (query)
- **Response**: VendorList model
- **Features**:
  - Vendor capability discovery
  - Detailed vendor information

### Environment Promotion

#### 1. Promote VIP Configuration
- **Endpoint**: `/api/v1/promotion/{vip_id}/{target_environment}`
- **Method**: POST
- **Required Parameters**: 
  - vip_id (path)
  - target_environment (path)
  - change_number (query)
- **Request Body**: PromotionOptions model
- **Response**: PromotionResult model
- **Features**:
  - Special handling for environment-specific data
  - Validation in target environment
  - Detailed promotion results

### IPAM Integration

#### 1. Allocate IP Address
- **Endpoint**: `/api/v1/ipam/allocate`
- **Method**: POST
- **Required Parameters**: 
  - change_number (query)
- **Request Body**: IPAllocationRequest model
- **Response**: IPAllocationResponse model
- **Features**:
  - Integration with IPAM system
  - Random name generation
  - Network validation

#### 2. Release IP Address
- **Endpoint**: `/api/v1/ipam/release/{ip_address}`
- **Method**: DELETE
- **Required Parameters**: 
  - ip_address (path)
  - change_number (query)
- **Response**: Success message
- **Features**:
  - IPAM system integration
  - Validation of IP ownership

#### 3. Register DNS Record
- **Endpoint**: `/api/v1/ipam/dns`
- **Method**: POST
- **Required Parameters**: 
  - change_number (query)
- **Request Body**: DNSRecordRequest model
- **Response**: DNSRecordResponse model
- **Features**:
  - DNS system integration
  - FQDN validation
  - Alias creation

### Change Management

#### 1. Validate Change
- **Endpoint**: `/api/v1/mock/servicenow/change`
- **Method**: POST
- **Request Body**: Change validation request
- **Response**: ChangeValidationResponse model
- **Features**:
  - ServiceNow integration
  - Change window validation
  - Change state validation

## Data Validation Rules

### VipBase Validation
1. **vip_fqdn**: Must be a valid URL format
2. **vip_ip**: Optional, but if provided must be valid IP format
3. **app_id**: Must be in format APP001 through APP010
4. **environment**: Must be one of: Dev, UAT, Prod
5. **datacenter**: Must be one of: LADC, NYDC, EUDC, APDC
6. **primary_contact_email**: Must be valid email format
7. **secondary_contact_email**: Optional, but if provided must be valid email format
8. **team_distribution_email**: Optional, but if provided must be valid email format
9. **pool**: Must contain at least 2 members
10. **port**: Must be a valid port number (1-65535)
11. **protocol**: Must be one of: TCP, HTTP, HTTPS, UDP
12. **lb_method**: Must be one of: ROUND_ROBIN, LEAST_CONNECTIONS, PRIORITY_GROUP

## Integration Architecture

### ServiceNow CMDB Integration
1. **Authentication**: Service account with OAuth 2.0
2. **Data Structure**: Device, owner, environment, datacenter, region, app_id
3. **Caching**: Cache CMDB responses to reduce API calls
4. **Error Handling**: Graceful handling of CMDB unavailability
5. **Change Validation**: Validate change numbers against ServiceNow

### IPAM/DNS Integration
1. **IP Allocation**: Allocate IPs from specified networks
2. **Random Name Generation**: Generate unique names for VIPs
3. **DNS Registration**: Create DNS records and aliases
4. **Validation**: Ensure DNS entries are unique

### Load Balancer Integration
1. **API Gateway**: Route requests to appropriate load balancers
2. **Vendor Transformers**: Convert standard format to vendor-specific
3. **Monitoring**: Collect health and performance metrics
4. **Configuration**: Apply configurations to load balancers

## Security Considerations

1. **Authentication**: JWT-based authentication
2. **Authorization**: Role-based access with admin privileges
3. **Input Validation**: Strict validation of all inputs
4. **Rate Limiting**: Protection against abuse
5. **Audit Logging**: Comprehensive logging of all operations
6. **Secure Communication**: HTTPS for all endpoints
7. **Secrets Management**: Secure handling of credentials

## Docker Containerization

1. **Base Image**: Python 3.11 slim
2. **Dependencies**: Requirements specified in requirements.txt
3. **MongoDB**: Separate container for database
4. **API Gateway**: Optional container for API gateway
5. **IPAM/DNS**: Container for opensource IPAM/DNS testing
6. **Docker Compose**: Multi-container deployment configuration
7. **Environment Variables**: Configuration via environment variables
8. **Volume Mounts**: Persistent storage for MongoDB
9. **Network Configuration**: Internal container communication
10. **Health Checks**: Container health monitoring

## Monitoring and Observability

1. **Metrics Collection**: Performance and usage metrics
2. **Logging**: Structured logging with correlation IDs
3. **Alerting**: Notification of service issues
4. **Dashboards**: Visualization of service health
5. **Tracing**: Request tracing across components

## Conclusion

This enhanced LBaaS API design incorporates best practices from industry leaders like AppViewX and Imperva, while addressing specific requirements for entitlement verification, change management, and multi-vendor support. The design provides a comprehensive, secure, and scalable solution for managing load balancer configurations across multiple environments and vendors.
