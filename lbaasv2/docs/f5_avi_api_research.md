# F5 AS3 and AVI API Research for LBaaS Integration

## F5 AS3 API Overview

### Introduction
F5 Application Services 3 (AS3) is a declarative API that enables configuration of application delivery services on BIG-IP systems. AS3 uses a JSON template format to create and manage application configurations on BIG-IP devices.

### Key Features
- Declarative API model (vs. imperative)
- JSON-based configuration
- Tenant-based isolation
- Idempotent operations
- Support for multiple BIG-IP versions

### Authentication
- Basic Authentication (over HTTPS)
- Session-based Authentication (login, obtain session token, use token for subsequent requests)

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/mgmt/shared/appsvcs/declare` | Main endpoint for deploying configurations |
| `/mgmt/shared/appsvcs/declare/{tenant}` | Endpoint for tenant-specific operations |
| `/mgmt/shared/appsvcs/info` | Retrieve AS3 version information |
| `/mgmt/shared/appsvcs/task` | Retrieve status of asynchronous operations |

### HTTP Methods

| Method | Description |
|--------|-------------|
| POST | Deploy configuration, patch existing configuration, retrieve configuration, remove configuration |
| GET | Retrieve configuration, list stored declarations |
| DELETE | Remove configuration |

### Key POST Actions
- `deploy`: Deploy the declaration (default)
- `dry-run`: Validate without deploying
- `patch`: Modify existing declaration using JSON Patch
- `redeploy`: Redeploy a previous declaration
- `retrieve`: Return the current configuration
- `remove`: Remove the configuration

### Important Parameters
- `updateMode`: Controls how tenants are updated
  - `selective`: Only modifies tenants defined in declaration
  - `complete`: Removes any tenant not defined in declaration
- `async`: Controls whether operation is synchronous or asynchronous
- `showHash`: Returns optimisticLockKey for future updates

### Declaration Structure
```json
{
  "class": "AS3",
  "action": "deploy",
  "persist": true,
  "declaration": {
    "class": "ADC",
    "schemaVersion": "3.0.0",
    "id": "example-declaration",
    "label": "Sample",
    "remark": "Simple application",
    "Tenant_Name": {
      "class": "Tenant",
      "Application_Name": {
        "class": "Application",
        "template": "http",
        "serviceMain": {
          "class": "Service_HTTP",
          "virtualAddresses": ["10.0.1.10"],
          "pool": "web_pool"
        },
        "web_pool": {
          "class": "Pool",
          "monitors": ["http"],
          "members": [{
            "servicePort": 80,
            "serverAddresses": ["192.0.1.10", "192.0.1.11"]
          }]
        }
      }
    }
  }
}
```

### Best Practices
- Use `"persist": true` to save configurations to disk
- Use `async=true` for large declarations
- Use tenant-specific endpoints for targeted updates
- Implement optimistic locking for concurrent updates
- Handle 45-second timeout for large declarations (API swap to async mode)

## VMware AVI Load Balancer API Overview

### Introduction
VMware AVI (formerly AVI Networks) provides a RESTful API for configuring and managing the NSX Advanced Load Balancer. The API allows programmatic control of all load balancing features.

### Authentication
- Basic Authentication (over HTTPS)
- Session Authentication (login, obtain session cookies, use cookies for subsequent requests)
  - Requires both `sessionid` and `csrftoken` cookies

### HTTP Headers

#### Request Headers
| Name | Required | Description |
|------|----------|-------------|
| Content-Type | Yes | Should be application/json |
| X-Avi-Version | Yes | API version to use (e.g., 18.1.2) |
| X-Avi-Tenant | No | Tenant context (defaults to user's default tenant) |
| Authorization | Yes | Base64 encoded credentials or session cookie |
| X-CSRFToken | Yes | CSRF Token for POST/PUT (from csrftoken cookie) |
| Referer | Yes (POST) | Parent page |
| Accept-Encoding | Yes (GET) | Should be application/json |

#### Response Headers/Cookies
| Name | Description |
|------|-------------|
| Content-Type | Content format (application/json) |
| csrftoken | Auth Token for session |
| sessionid | Session ID |

### Object Management

#### Object Retrieval (GET)
```
GET /api/tenant
GET /api/tenant/admin
```

#### Object Creation (POST)
```
POST /api/pool
{
  "description": "my pool",
  "name": "pool1",
  "servers": [
    {
      "ip": {
        "addr": "10.10.1.10",
        "type": "V4"
      },
      "port": 80
    }
  ]
}
```

#### Object Modification (PUT)
```
PUT /api/pool/pool-13df5490-cb95-47f8-b414-c2b37c897ca7
{
  "uuid": "pool-13df5490-cb95-47f8-b414-c2b37c897ca7",
  "name": "p1",
  "tenant_ref": "https://10.10.1.101/api/tenant/admin",
  "servers": [
    {
      "ip": {
        "type": "V4",
        "addr": "10.10.10.10"
      },
      "enabled": true
    }
  ]
}
```

#### Object Deletion (DELETE)
```
DELETE /api/pool/pool-13df5490-cb95-47f8-b414-c2b37c897ca7
```

### Key API Categories
- Virtual Services
- Pools
- Health Monitors
- SSL Certificates
- Application Profiles
- Persistence Profiles
- Analytics
- Cloud Configuration

### Object Tenancy
- Every object is associated with a tenant
- 'admin' is the default tenant
- Users can only access tenants where they have assigned roles
- X-Avi-Tenant header specifies tenant context for operations

### Session Management Example
```python
# Login and establish session
login = requests.post('https://controller-ip/login', 
                     data={'username': 'admin', 'password': 'password'})
session_id = login.cookies['sessionid']
csrf_token = login.cookies['csrftoken']

# Use session for subsequent requests
headers = {
    'X-Avi-Version': '18.1.2',
    'X-CSRFToken': csrf_token,
    'Referer': 'https://controller-ip/'
}
resp = requests.get('https://controller-ip/api/pool', 
                   cookies={'sessionid': session_id}, 
                   headers=headers)

# Logout
logout = requests.post('https://controller-ip/logout', 
                      headers=headers, 
                      cookies={'sessionid': session_id})
```

## Integration Considerations for LBaaS

### Common Integration Points

1. **Authentication and Session Management**
   - Both APIs support basic and session-based authentication
   - Session management is recommended for multiple operations
   - Token/cookie handling required for both APIs

2. **Configuration Management**
   - F5 AS3: Declarative model with full configuration in single JSON
   - AVI: RESTful CRUD operations on individual objects
   - LBaaS should abstract these differences with a common model

3. **Tenant Isolation**
   - Both support multi-tenant operations
   - F5 AS3: Tenants defined in declaration
   - AVI: X-Avi-Tenant header for context

4. **Error Handling**
   - Both use standard HTTP response codes
   - Asynchronous operations need polling for completion status
   - F5 AS3 has automatic async conversion for operations >45 seconds

5. **Version Compatibility**
   - F5 AS3: X-F5-Auth-Token for authentication
   - AVI: X-Avi-Version header required for API versioning

### Implementation Recommendations

1. **Abstraction Layer**
   - Create a common interface that translates LBaaS operations to vendor-specific API calls
   - Implement vendor-specific adapters for F5 AS3 and AVI

2. **Configuration Translation**
   - Develop transformers to convert LBaaS configuration to:
     - F5 AS3 declarations
     - AVI API object operations

3. **Authentication Handling**
   - Implement session caching and renewal
   - Handle CSRF tokens for AVI
   - Support connection pooling for efficiency

4. **Asynchronous Operations**
   - Implement polling mechanism for long-running operations
   - Use task IDs to track operation status

5. **Error Standardization**
   - Create common error codes and messages
   - Map vendor-specific errors to standard format

6. **Monitoring Integration**
   - Both platforms provide health monitoring capabilities
   - Standardize health check configurations

7. **Logging and Auditing**
   - Track all API operations for troubleshooting
   - Implement detailed logging for configuration changes

### Sample Integration Flow

1. User submits VIP creation request to LBaaS API
2. LBaaS validates request against entitlements (ServiceNow CMDB)
3. LBaaS determines target load balancer type (F5 or AVI)
4. LBaaS transforms request to vendor-specific format
5. LBaaS authenticates with target load balancer API
6. LBaaS submits configuration to load balancer
7. LBaaS monitors operation completion
8. LBaaS stores successful configuration in MongoDB
9. LBaaS returns standardized response to user
