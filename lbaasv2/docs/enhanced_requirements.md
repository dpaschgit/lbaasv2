# Enhanced LBaaS API Requirements

## Overview
This document outlines the enhanced requirements for a Load Balancing as a Service (LBaaS) API. The API will provide CRUD operations for Virtual IPs (VIPs), entitlement verification through ServiceNow CMDB integration, and a standard output format for vendor-specific transformers.

## Core Requirements

### 1. VIP Management (CRUD Operations)
- Create new VIPs with specified configurations
  - Support for both L4 and L7 VIPs
  - Persistence options:
    - Source IP
    - Session
    - Cookie
  - Load balancing methods:
    - Round Robin
    - Least Connections
    - Priority Groups
  - Monitoring capabilities:
    - TCP monitors
    - UDP monitors
    - HTTP ECV monitors
    - Alternate port support for TCP monitors
  - mTLS support (without storing certificates)
- Read/Retrieve existing VIP configurations
- Update VIP configurations
- Delete VIPs

### 2. Entitlement Verification
- Query ServiceNow CMDB for entitlement verification
- Prevent users from adding servers they don't have rights to behind a VIP
- Validate user permissions before allowing VIP modifications
- CMDB data structure:
  - device
  - device IP
  - owner1
  - owner2
  - owner email distribution list
  - environment
  - datacenter
  - region

### 3. Standard Output Format
- Provide a common, vendor-agnostic JSON output format
- Support transformers for different load balancer vendors
- Enable easy addition of new load balancer products/vendors in the future
- Direct calls to MongoDB and ServiceNow must be API compliant with the real products

### 4. Storage Requirements
- Store LBaaS configurations in a dedicated MongoDB database
- Keep configurations separate from ServiceNow CMDB data
- Store both the latest configuration and the previous configuration for each VIP
- Store translator outputs in MongoDB (not in files)

### 5. Integration Requirements
- Integrate with ServiceNow CMDB for entitlement verification
- IPAM integration
  - Need opensource IPAM/DNS for lab testing that LBaaS can make API calls against
- Plan for future API gateway integration for load balancer device communication
- Support multiple vendor-specific transformers

### 6. Documentation Requirements
- Provide complete Swagger/OpenAPI documentation for all endpoints
- Include request/response examples
- Document authentication and authorization methods

## Additional Notes
- Do not store SSL certificates for VIP or mTLS
- Docker-based deployment
- API must be designed for extensibility and future vendor support
