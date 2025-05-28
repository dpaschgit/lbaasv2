# Enhanced ServiceNow CMDB and IPAM Integration for LBaaS API

## Overview
This document outlines the enhanced integration between the LBaaS API, ServiceNow CMDB, and IPAM/DNS systems. It includes entitlement verification, change management validation, and data validation rules.

## Integration Architecture

### High-Level Flow
1. User submits a request with change number to create, update, or delete a VIP
2. LBaaS API validates the change number against ServiceNow
3. LBaaS API extracts server IDs and application IDs from the request
4. LBaaS API calls the entitlement verification service
5. Entitlement service queries ServiceNow CMDB
6. CMDB returns entitlement data
7. Entitlement service processes the data and returns results
8. For new VIPs, IPAM integration allocates IP and registers DNS
9. LBaaS API allows or denies the operation based on validation results

### Components

#### 1. Change Management Service
- Validates change numbers against ServiceNow
- Verifies change state (approved, scheduled, etc.)
- Ensures change window compliance
- Logs change execution status

#### 2. Entitlement Verification Service
- Standalone service within the LBaaS API
- Handles all entitlement-related logic
- Caches CMDB responses to reduce API calls
- Implements retry and fallback mechanisms

#### 3. ServiceNow CMDB Connector
- Handles communication with ServiceNow CMDB
- Manages authentication and session handling
- Translates between LBaaS and ServiceNow data models
- Implements error handling and logging

#### 4. IPAM/DNS Integration Service
- Manages IP allocation and DNS registration
- Generates random names for VIPs
- Creates DNS aliases to desired URLs
- Validates DNS entries for uniqueness

#### 5. Data Validation Service
- Validates all input data against defined rules
- Ensures data consistency and integrity
- Prevents invalid configurations

## Change Management Integration

### Change Number Validation
1. All CRUD operations require a valid change number
2. Change number format validation (e.g., CHG0012345)
3. Change state validation (must be approved and scheduled)
4. Change window validation (operation must be within change window)
5. Change owner validation (change owner must have entitlements)

### Mock Change Numbers for Testing
- Valid change numbers: CHG0010001, CHG0010002, CHG0010003
- Invalid change numbers: CHG0099999, CHG0088888
- Expired change numbers: CHG0077777
- Future change numbers: CHG0066666

### ServiceNow Mock Service Integration
1. Mock service endpoint: `/api/v1/mock/servicenow/change`
2. Request format:
   ```json
   {
     "change_number": "CHG0010001",
     "operation_type": "CREATE|UPDATE|DELETE",
     "resource_type": "VIP",
     "resource_id": "optional-vip-id"
   }
   ```
3. Response format:
   ```json
   {
     "valid": true|false,
     "state": "approved|scheduled|implementing|closed|rejected",
     "window_start": "2025-05-26T22:00:00Z",
     "window_end": "2025-05-27T02:00:00Z",
     "owner": "user123",
     "reason": "Optional reason if invalid"
   }
   ```

## Entitlement Verification Process

### User Authentication and Context
1. User authenticates to the LBaaS API
2. JWT token contains user identity, role information, and app IDs
3. User context is extracted and passed to entitlement service
4. Admin users bypass entitlement checks

### Server Entitlement Verification
1. Extract server IDs and app IDs from VIP creation/update request
2. Call entitlement service with server IDs, app IDs, and user context
3. Entitlement service checks cache for recent results
4. If cache miss, query ServiceNow CMDB
5. Process CMDB response to determine entitlements
6. Cache results for future use
7. Return entitlement results to API

### Entitlement Decision Logic
1. For each server, determine if user has entitlement
2. Entitlement can be based on:
   - Direct server ownership
   - Application team membership (matching app IDs)
   - Role-based access (admin override)
   - Delegated access rights
3. All servers must pass entitlement check for operation to proceed
4. Detailed reason for entitlement decisions is captured for auditing

## ServiceNow CMDB Integration

### Authentication
- Service account-based authentication
- OAuth 2.0 token-based access
- Credentials stored securely in environment variables or secrets manager
- Token refresh mechanism for long-running operations

### API Endpoints
- `/api/now/table/cmdb_ci_server` - Server configuration items
- `/api/now/table/sys_user` - User information
- `/api/now/table/sys_user_group` - Group membership
- `/api/now/table/cmdb_rel_ci` - CI relationships

### CMDB Data Structure
- device: Server identifier
- device_ip: Server IP address
- owner1: Primary owner
- owner2: Secondary owner
- owner_email_distro: Owner email distribution list
- environment: Environment (Dev, UAT, Prod)
- datacenter: Datacenter (LADC, NYDC, EUDC, APDC)
- region: Region
- app_id: Application identifier (APP001-APP010)

### Query Parameters
- `sysparm_query` - Filter conditions
- `sysparm_fields` - Fields to return
- `sysparm_display_value` - Return display values

### Sample CMDB Query
```
GET /api/now/table/cmdb_ci_server?
    sysparm_query=sys_id=server123
    &sysparm_fields=sys_id,name,u_application,u_owner,u_support_group,u_app_id,u_environment,u_datacenter,u_region
    &sysparm_display_value=true
```

## IPAM/DNS Integration

### IP Allocation Process
1. Receive IP allocation request with network details
2. Generate random name for VIP (e.g., vip-a1b2c3)
3. Check if IP is available in requested network
4. Allocate IP address
5. Return allocated IP information

### DNS Registration Process
1. Receive DNS registration request with hostname and IP
2. Validate that requested FQDN is not already in use
3. Create DNS A record for random VIP name
4. Create DNS CNAME alias to desired URL
5. Return DNS registration result

### Validation Rules
1. FQDN must be a valid URL format
2. IP address must be valid IPv4 or IPv6 format
3. Hostname must follow naming conventions
4. DNS records must be unique

### Open Source IPAM/DNS for Lab Testing
1. NetBox for IPAM functionality
2. Bind9 for DNS functionality
3. API endpoints for integration
4. Docker containers for easy deployment

## Data Validation Rules

### VipBase Validation
1. vip_fqdn: Must be a valid URL format
2. vip_ip: Optional, but if provided must be valid IP format
3. app_id: Must be in format APP001 through APP010
4. environment: Must be one of: Dev, UAT, Prod
5. datacenter: Must be one of: LADC, NYDC, EUDC, APDC
6. primary_contact_email: Must be valid email format
7. secondary_contact_email: Optional, but if provided must be valid email format
8. team_distribution_email: Optional, but if provided must be valid email format
9. pool: Must contain at least 2 members
10. port: Must be a valid port number (1-65535)
11. protocol: Must be one of: TCP, HTTP, HTTPS, UDP
12. lb_method: Must be one of: ROUND_ROBIN, LEAST_CONNECTIONS, PRIORITY_GROUP

### Test Data for CMDB
For each datacenter (LADC, NYDC, EUDC, APDC):
- 2 servers per environment (Dev, UAT, Prod)
- 3 users with different entitlements
- Each server assigned to one of APP001-APP010

Example:
```
Server: srv-ladc-dev-001
IP: 10.1.1.1
Owner1: user1
Owner2: user2
Owner Email Distro: team1@example.com
Environment: Dev
Datacenter: LADC
Region: US-WEST
App ID: APP001
```

## Error Handling and Resilience

### Change Management Service Unavailability
1. Implement circuit breaker pattern
2. Default to deny access when service is unavailable
3. Detailed error logging and monitoring
4. Retry mechanism with exponential backoff

### CMDB Unavailability
1. Implement circuit breaker pattern
2. Use cached results if available (with warning)
3. Configurable fallback behavior (fail open/closed)
4. Detailed error logging and monitoring

### IPAM/DNS Service Unavailability
1. Implement circuit breaker pattern
2. Queue requests for retry when service is restored
3. Provide clear error messages to users
4. Monitoring and alerting for service status

## Security Considerations

### Data Protection
1. Minimize data transfer between systems
2. Only request necessary fields from CMDB
3. Encrypt sensitive data in transit and at rest
4. Implement proper data retention policies

### Access Control
1. Use principle of least privilege for service accounts
2. Implement IP restrictions for CMDB access
3. Regular credential rotation
4. Comprehensive audit logging

### Audit Trail
1. Log all entitlement checks and change validations
2. Record decision basis and CMDB data used
3. Maintain history of entitlement decisions
4. Support compliance and security reviews

## Implementation Details

### Python Code Example for Change Validation

```python
# Change Management Service
class ChangeManagementService:
    def __init__(self, servicenow_url, auth_token):
        self.servicenow_url = servicenow_url
        self.auth_token = auth_token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        })
        
    def validate_change(self, change_number, operation_type, resource_type, resource_id=None):
        """Validate change number against ServiceNow"""
        url = f"{self.servicenow_url}/api/v1/mock/servicenow/change"
        payload = {
            "change_number": change_number,
            "operation_type": operation_type,
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        
        try:
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                
                # Check if change is valid
                if not result.get("valid", False):
                    return False, result.get("reason", "Invalid change number")
                
                # Check if change is in correct state
                valid_states = ["approved", "scheduled", "implementing"]
                if result.get("state") not in valid_states:
                    return False, f"Change is in invalid state: {result.get('state')}"
                
                # Check if current time is within change window
                now = datetime.utcnow()
                window_start = datetime.fromisoformat(result.get("window_start").replace("Z", "+00:00"))
                window_end = datetime.fromisoformat(result.get("window_end").replace("Z", "+00:00"))
                
                if not (window_start <= now <= window_end):
                    return False, "Current time is outside change window"
                
                return True, "Change is valid"
            else:
                return False, f"Failed to validate change: {response.status_code}"
        except Exception as e:
            return False, f"Error validating change: {str(e)}"
```

### Python Code Example for IPAM Integration

```python
# IPAM Integration Service
class IPAMService:
    def __init__(self, ipam_url, auth_token):
        self.ipam_url = ipam_url
        self.auth_token = auth_token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        })
        
    def generate_random_name(self, prefix="vip"):
        """Generate a random name for a VIP"""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"{prefix}-{random_suffix}"
        
    def allocate_ip(self, network, hostname, app_id, environment, datacenter, region):
        """Allocate an IP address from IPAM"""
        url = f"{self.ipam_url}/api/ipam/ip"
        payload = {
            "network": network,
            "hostname": hostname,
            "app_id": app_id,
            "environment": environment,
            "datacenter": datacenter,
            "region": region
        }
        
        try:
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Failed to allocate IP: {response.status_code}"
        except Exception as e:
            return False, f"Error allocating IP: {str(e)}"
            
    def register_dns(self, hostname, ip_address, record_type, ttl, app_id):
        """Register a DNS record"""
        url = f"{self.ipam_url}/api/dns/record"
        payload = {
            "hostname": hostname,
            "ip_address": ip_address,
            "record_type": record_type,
            "ttl": ttl,
            "app_id": app_id
        }
        
        try:
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Failed to register DNS: {response.status_code}"
        except Exception as e:
            return False, f"Error registering DNS: {str(e)}"
            
    def create_dns_alias(self, alias, target, ttl, app_id):
        """Create a DNS CNAME alias"""
        url = f"{self.ipam_url}/api/dns/alias"
        payload = {
            "alias": alias,
            "target": target,
            "ttl": ttl,
            "app_id": app_id
        }
        
        try:
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Failed to create DNS alias: {response.status_code}"
        except Exception as e:
            return False, f"Error creating DNS alias: {str(e)}"
```

### API Integration Example with Change Validation

```python
# FastAPI route for VIP creation with change validation
@router.post("/vips", response_model=VipBase, status_code=201)
async def create_vip(
    vip: VipCreate,
    change_number: str = Query(..., description="Change number for this operation"),
    current_user: User = Depends(get_current_user),
    change_service: ChangeManagementService = Depends(get_change_service),
    entitlement_service: EntitlementService = Depends(get_entitlement_service),
    ipam_service: IPAMService = Depends(get_ipam_service),
    vip_service: VipService = Depends(get_vip_service)
):
    """Create a new VIP with change and entitlement verification"""
    # Validate input data
    validate_vip_data(vip)
    
    # Validate change number
    change_valid, change_message = change_service.validate_change(
        change_number=change_number,
        operation_type="CREATE",
        resource_type="VIP"
    )
    
    if not change_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Change validation failed: {change_message}"
        )
    
    # Extract server IDs from pool
    server_ids = [member.ip for member in vip.pool]
    app_ids = [member.app_id for member in vip.pool]
    
    # Verify entitlements (admin users bypass this check)
    if current_user.role != UserRole.ADMIN:
        entitlement_results = entitlement_service.verify_entitlements(
            user_id=current_user.id,
            server_ids=server_ids,
            app_ids=app_ids
        )
        
        # Check if all servers are entitled
        all_entitled = all(result["entitled"] for result in entitlement_results)
        if not all_entitled:
            # Find servers that failed entitlement check
            failed_servers = [
                f"{result['server_id']}: {result['reason']}"
                for result in entitlement_results
                if not result["entitled"]
            ]
            
            raise HTTPException(
                status_code=403,
                detail=f"Entitlement verification failed for servers: {', '.join(failed_servers)}"
            )
    
    # If VIP IP is not provided, allocate one from IPAM
    if not vip.vip_ip:
        # Generate random name for VIP
        random_name = ipam_service.generate_random_name()
        
        # Allocate IP address
        ip_success, ip_result = ipam_service.allocate_ip(
            network=f"10.{vip.datacenter_id}.0.0/16",
            hostname=random_name,
            app_id=vip.app_id,
            environment=vip.environment,
            datacenter=vip.datacenter,
            region=vip.region
        )
        
        if not ip_success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to allocate IP address: {ip_result}"
            )
            
        # Set allocated IP
        vip.vip_ip = ip_result["ip_address"]
        
        # Register DNS record for random name
        dns_success, dns_result = ipam_service.register_dns(
            hostname=random_name,
            ip_address=vip.vip_ip,
            record_type="A",
            ttl=3600,
            app_id=vip.app_id
        )
        
        if not dns_success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to register DNS record: {dns_result}"
            )
            
        # Create DNS alias to desired FQDN
        alias_success, alias_result = ipam_service.create_dns_alias(
            alias=vip.vip_fqdn,
            target=f"{random_name}.example.com",
            ttl=3600,
            app_id=vip.app_id
        )
        
        if not alias_success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create DNS alias: {alias_result}"
            )
    
    # Proceed with VIP creation
    return vip_service.create_vip(vip, current_user.id, change_number)
```

### Data Validation Function

```python
def validate_vip_data(vip: VipBase):
    """Validate VIP data against defined rules"""
    # Validate FQDN
    if not re.match(r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$', vip.vip_fqdn):
        raise ValueError("Invalid FQDN format")
        
    # Validate IP if provided
    if vip.vip_ip and not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', vip.vip_ip):
        raise ValueError("Invalid IP address format")
        
    # Validate app_id
    if not re.match(r'^APP00[1-9]$|^APP010$', vip.app_id):
        raise ValueError("app_id must be in format APP001 through APP010")
        
    # Validate environment
    valid_environments = ["Dev", "UAT", "Prod"]
    if vip.environment not in valid_environments:
        raise ValueError(f"environment must be one of: {', '.join(valid_environments)}")
        
    # Validate datacenter
    valid_datacenters = ["LADC", "NYDC", "EUDC", "APDC"]
    if vip.datacenter not in valid_datacenters:
        raise ValueError(f"datacenter must be one of: {', '.join(valid_datacenters)}")
        
    # Validate email formats
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, vip.primary_contact_email):
        raise ValueError("Invalid primary contact email format")
        
    if vip.secondary_contact_email and not re.match(email_pattern, vip.secondary_contact_email):
        raise ValueError("Invalid secondary contact email format")
        
    if vip.team_distribution_email and not re.match(email_pattern, vip.team_distribution_email):
        raise ValueError("Invalid team distribution email format")
        
    # Validate pool members
    if len(vip.pool) < 2:
        raise ValueError("Pool must contain at least 2 members")
        
    # Validate port
    if not 1 <= vip.port <= 65535:
        raise ValueError("Port must be between 1 and 65535")
        
    # Validate protocol
    valid_protocols = ["TCP", "HTTP", "HTTPS", "UDP"]
    if vip.protocol not in valid_protocols:
        raise ValueError(f"Protocol must be one of: {', '.join(valid_protocols)}")
        
    # Validate lb_method if provided
    if vip.lb_method:
        valid_methods = ["ROUND_ROBIN", "LEAST_CONNECTIONS", "PRIORITY_GROUP"]
        if vip.lb_method not in valid_methods:
            raise ValueError(f"lb_method must be one of: {', '.join(valid_methods)}")
```

## Monitoring and Observability

### Metrics to Collect
1. Change validation success/failure rate
2. Entitlement check latency
3. CMDB query latency
4. IPAM/DNS operation latency
5. Cache hit/miss ratio
6. Service availability

### Logging
1. Structured logging for all operations
2. Correlation IDs across services
3. Change number included in all logs
4. Error details for troubleshooting

### Alerting
1. ServiceNow connectivity issues
2. IPAM/DNS service issues
3. High change validation failure rates
4. High entitlement failure rates

## Deployment Considerations

### Docker Configuration
- Include ServiceNow, CMDB, and IPAM connectors in API container
- Environment variables for configuration
- Secrets management for credentials
- Health checks for all integration points

### Scaling
- Stateless design for horizontal scaling
- Distributed caching for multi-instance deployments
- Rate limiting for external service protection

## Testing Strategy

### Unit Tests
- Mock ServiceNow, CMDB, and IPAM responses
- Test validation logic
- Verify caching behavior
- Error handling scenarios

### Integration Tests
- Test with mock services
- Verify end-to-end flows
- Performance under load
- Failure recovery

### Security Tests
- Authentication bypass attempts
- Authorization boundary testing
- Data leakage checks
- Credential handling
