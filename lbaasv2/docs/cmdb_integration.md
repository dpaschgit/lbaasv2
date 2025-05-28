# ServiceNow CMDB Integration for LBaaS API

## Overview
This document outlines the integration between the LBaaS API and ServiceNow CMDB for entitlement verification. The integration ensures that users can only add servers they have rights to behind a VIP.

## Integration Architecture

### High-Level Flow
1. User submits a request to create or update a VIP with backend servers
2. LBaaS API extracts server IDs from the request
3. LBaaS API calls the entitlement verification service
4. Entitlement service queries ServiceNow CMDB
5. CMDB returns entitlement data
6. Entitlement service processes the data and returns results
7. LBaaS API allows or denies the operation based on entitlement results

### Components

#### 1. Entitlement Verification Service
- Standalone service within the LBaaS API
- Handles all entitlement-related logic
- Caches CMDB responses to reduce API calls
- Implements retry and fallback mechanisms

#### 2. ServiceNow CMDB Connector
- Handles communication with ServiceNow CMDB
- Manages authentication and session handling
- Translates between LBaaS and ServiceNow data models
- Implements error handling and logging

#### 3. Entitlement Cache
- Caches entitlement results to reduce CMDB load
- Implements time-based expiration
- Supports cache invalidation on demand

## Entitlement Verification Process

### User Authentication and Context
1. User authenticates to the LBaaS API
2. JWT token contains user identity and role information
3. User context is extracted and passed to entitlement service

### Server Entitlement Verification
1. Extract server IDs from VIP creation/update request
2. Call entitlement service with server IDs and user context
3. Entitlement service checks cache for recent results
4. If cache miss, query ServiceNow CMDB
5. Process CMDB response to determine entitlements
6. Cache results for future use
7. Return entitlement results to API

### Entitlement Decision Logic
1. For each server, determine if user has entitlement
2. Entitlement can be based on:
   - Direct server ownership
   - Application team membership
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

### Query Parameters
- `sysparm_query` - Filter conditions
- `sysparm_fields` - Fields to return
- `sysparm_display_value` - Return display values

### Sample CMDB Query
```
GET /api/now/table/cmdb_ci_server?
    sysparm_query=sys_id=server123
    &sysparm_fields=sys_id,name,u_application,u_owner,u_support_group
    &sysparm_display_value=true
```

### Response Processing
1. Parse CMDB response JSON
2. Extract relevant fields (server details, ownership, application)
3. Map to LBaaS entitlement model
4. Apply business rules for entitlement decisions
5. Generate detailed entitlement results

## Error Handling and Resilience

### CMDB Unavailability
1. Implement circuit breaker pattern
2. Use cached results if available (with warning)
3. Configurable fallback behavior (fail open/closed)
4. Detailed error logging and monitoring

### Partial Data or Inconsistencies
1. Validate CMDB response data
2. Handle missing or incomplete data gracefully
3. Default to secure behavior (deny access) when uncertain
4. Log data quality issues for remediation

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
1. Log all entitlement checks
2. Record decision basis and CMDB data used
3. Maintain history of entitlement decisions
4. Support compliance and security reviews

## Performance Optimization

### Caching Strategy
1. Cache entitlement results for 15 minutes by default
2. Configurable TTL based on environment
3. Cache invalidation on user role changes
4. Separate caches for different query types

### Batch Processing
1. Combine multiple server queries into single CMDB call
2. Process responses in parallel where possible
3. Prioritize critical path operations

### Connection Pooling
1. Maintain persistent connections to CMDB
2. Implement connection pooling
3. Handle connection lifecycle properly

## Implementation Details

### Python Code Example

```python
# ServiceNow CMDB Connector
class ServiceNowConnector:
    def __init__(self, instance_url, username, password):
        self.instance_url = instance_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = None
        
    def authenticate(self):
        """Authenticate to ServiceNow and get access token"""
        auth_url = f"{self.instance_url}/oauth_token.do"
        payload = {
            "grant_type": "password",
            "client_id": os.getenv("SNOW_CLIENT_ID"),
            "client_secret": os.getenv("SNOW_CLIENT_SECRET"),
            "username": self.username,
            "password": self.password
        }
        response = self.session.post(auth_url, data=payload)
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            return True
        return False
        
    def get_server_details(self, server_id):
        """Get server details from CMDB"""
        if not self.token and not self.authenticate():
            raise Exception("Authentication failed")
            
        url = f"{self.instance_url}/api/now/table/cmdb_ci_server"
        params = {
            "sysparm_query": f"sys_id={server_id}",
            "sysparm_fields": "sys_id,name,u_application,u_owner,u_support_group",
            "sysparm_display_value": "true"
        }
        
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("result", [])
        return None
        
    def get_user_groups(self, user_id):
        """Get groups a user belongs to"""
        if not self.token and not self.authenticate():
            raise Exception("Authentication failed")
            
        url = f"{self.instance_url}/api/now/table/sys_user_grmember"
        params = {
            "sysparm_query": f"user.sys_id={user_id}",
            "sysparm_fields": "group.sys_id,group.name",
            "sysparm_display_value": "true"
        }
        
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("result", [])
        return None

# Entitlement Service
class EntitlementService:
    def __init__(self, cmdb_connector, cache_ttl=900):  # 15 minutes default
        self.cmdb = cmdb_connector
        self.cache = {}
        self.cache_ttl = cache_ttl
        
    def verify_entitlements(self, user_id, server_ids):
        """Verify user entitlements for a list of servers"""
        results = []
        
        # Get user groups (with caching)
        cache_key = f"user_groups_{user_id}"
        if cache_key in self.cache and time.time() - self.cache[cache_key]["timestamp"] < self.cache_ttl:
            user_groups = self.cache[cache_key]["data"]
        else:
            user_groups = self.cmdb.get_user_groups(user_id)
            self.cache[cache_key] = {
                "data": user_groups,
                "timestamp": time.time()
            }
            
        # Check each server
        for server_id in server_ids:
            # Check cache first
            cache_key = f"server_{server_id}"
            server_details = None
            
            if cache_key in self.cache and time.time() - self.cache[cache_key]["timestamp"] < self.cache_ttl:
                server_details = self.cache[cache_key]["data"]
            else:
                server_details = self.cmdb.get_server_details(server_id)
                if server_details:
                    self.cache[cache_key] = {
                        "data": server_details,
                        "timestamp": time.time()
                    }
            
            if not server_details:
                results.append({
                    "server_id": server_id,
                    "entitled": False,
                    "reason": "Server not found in CMDB"
                })
                continue
                
            # Check entitlement logic
            entitled = False
            reason = "No matching entitlement rules"
            
            # Rule 1: Direct ownership
            if server_details.get("u_owner") == user_id:
                entitled = True
                reason = "User is the server owner"
                
            # Rule 2: Support group membership
            elif any(g.get("group.sys_id") == server_details.get("u_support_group") for g in user_groups):
                entitled = True
                reason = "User is a member of the server support group"
                
            # Rule 3: Application team membership
            # Additional logic here...
            
            results.append({
                "server_id": server_id,
                "entitled": entitled,
                "reason": reason
            })
            
        return results
        
    def clear_cache(self, user_id=None, server_id=None):
        """Clear specific cache entries or all if none specified"""
        if user_id:
            cache_key = f"user_groups_{user_id}"
            if cache_key in self.cache:
                del self.cache[cache_key]
                
        if server_id:
            cache_key = f"server_{server_id}"
            if cache_key in self.cache:
                del self.cache[cache_key]
                
        if not user_id and not server_id:
            self.cache = {}
```

### API Integration Example

```python
# FastAPI route for entitlement verification
@router.post("/entitlements/verify", response_model=List[EntitlementResult])
async def verify_entitlement(
    verification: EntitlementVerification,
    current_user: User = Depends(get_current_user),
    entitlement_service: EntitlementService = Depends(get_entitlement_service)
):
    """Verify user entitlements for specific servers"""
    try:
        results = entitlement_service.verify_entitlements(
            user_id=current_user.id,
            server_ids=verification.server_ids
        )
        return results
    except Exception as e:
        logger.error(f"Entitlement verification failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Entitlement verification failed: {str(e)}"
        )

# VIP creation with entitlement check
@router.post("/vips", response_model=VipBase, status_code=201)
async def create_vip(
    vip: VipCreate,
    current_user: User = Depends(get_current_user),
    entitlement_service: EntitlementService = Depends(get_entitlement_service),
    vip_service: VipService = Depends(get_vip_service)
):
    """Create a new VIP with entitlement verification"""
    # Extract server IDs from pool
    server_ids = [member.ip for member in vip.pool]
    
    # Verify entitlements
    entitlement_results = entitlement_service.verify_entitlements(
        user_id=current_user.id,
        server_ids=server_ids
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
    
    # Proceed with VIP creation
    return vip_service.create_vip(vip, current_user.id)
```

## Monitoring and Observability

### Metrics to Collect
1. Entitlement check latency
2. CMDB query latency
3. Cache hit/miss ratio
4. Entitlement success/failure rate
5. CMDB availability

### Logging
1. Structured logging for all operations
2. Correlation IDs across services
3. Anonymized entitlement decisions
4. Error details for troubleshooting

### Alerting
1. CMDB connectivity issues
2. High entitlement failure rates
3. Cache performance degradation
4. Authentication failures

## Deployment Considerations

### Docker Configuration
- Include ServiceNow connector in API container
- Environment variables for configuration
- Secrets management for credentials
- Health checks for CMDB connectivity

### Scaling
- Stateless design for horizontal scaling
- Distributed caching for multi-instance deployments
- Rate limiting for CMDB protection

## Testing Strategy

### Unit Tests
- Mock CMDB responses
- Test entitlement logic
- Verify caching behavior
- Error handling scenarios

### Integration Tests
- Test with CMDB test instance
- Verify end-to-end flows
- Performance under load
- Failure recovery

### Security Tests
- Authentication bypass attempts
- Authorization boundary testing
- Data leakage checks
- Credential handling
