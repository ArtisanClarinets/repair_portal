# Instrument Profile Module - API Documentation

**Fortune-500 Enterprise Documentation**  
**Version:** 2.0.0  
**Date:** 2025-10-02  
**Classification:** Internal Use  

---

## Executive Summary

This document provides comprehensive API documentation for the Instrument Profile module, designed for Fortune-500 enterprise deployment with security, scalability, and auditability at its core.

## Security Overview

All APIs implement:
- **Authentication:** Bearer token or session-based authentication required
- **Authorization:** Role-based access control with granular permissions
- **Input Validation:** Comprehensive server-side validation and sanitization
- **Audit Logging:** All API calls logged with user, timestamp, and data changes
- **Rate Limiting:** Configurable rate limits per user/IP
- **XSS Protection:** All input sanitized against cross-site scripting

## Core API Endpoints

### 1. Instrument Profile Management

#### GET `/api/resource/Instrument Profile/{name}`
**Purpose:** Retrieve instrument profile details  
**Authentication:** Required  
**Permissions:** Read access to Instrument Profile  

**Response Schema:**
```json
{
  "name": "string",
  "serial_no": "string",
  "brand": "string",
  "model": "string",
  "status": "string",
  "workflow_state": "string",
  "customer": "string",
  "current_location": "string",
  "warranty_end_date": "date",
  "creation": "datetime",
  "modified": "datetime"
}
```

**Error Codes:**
- `403` - Insufficient permissions
- `404` - Profile not found
- `500` - Internal server error

#### POST `/api/resource/Instrument Profile`
**Purpose:** Create new instrument profile  
**Authentication:** Required  
**Permissions:** Create access to Instrument Profile  

**Request Schema:**
```json
{
  "instrument": "string (required)",
  "customer": "string (optional)",
  "initial_condition_notes": "string (optional)",
  "current_location": "string (optional)"
}
```

**Validation Rules:**
- `instrument`: Must reference existing Instrument document
- `customer`: If provided, must reference existing Customer document
- `initial_condition_notes`: Max 5000 characters, XSS sanitized
- `current_location`: Max 100 characters, alphanumeric pattern

#### PUT `/api/resource/Instrument Profile/{name}`
**Purpose:** Update existing instrument profile  
**Authentication:** Required  
**Permissions:** Write access to specific profile  

**Read-Only Fields (Cannot be updated):**
- `serial_no`, `brand`, `model`, `instrument_category`
- `customer`, `owner_name`, `purchase_date`
- `warranty_start_date`, `warranty_end_date`
- `status`, `headline`

### 2. Enhanced API Methods

#### POST `/api/method/repair_portal.instrument_profile.doctype.instrument_profile.instrument_profile.get_instrument_profile_summary`
**Purpose:** Get comprehensive profile summary with security checks  
**Authentication:** Required  
**Rate Limit:** 100 requests/minute per user  

**Parameters:**
```json
{
  "name": "string (required) - Profile name"
}
```

**Response:**
```json
{
  "name": "string",
  "serial_no": "string",
  "brand": "string",
  "model": "string",
  "status": "string",
  "workflow_state": "string",
  "customer": "string",
  "customer_details": {
    "name": "string",
    "customer_name": "string",
    "email": "string"
  },
  "current_location": "string",
  "warranty_end_date": "date",
  "last_service_date": "date"
}
```

**Security Features:**
- Permission validation for both profile and customer access
- Audit logging of all access attempts
- Input validation and sanitization
- Error handling with security-safe messages

#### POST `/api/method/repair_portal.instrument_profile.doctype.instrument_profile.instrument_profile.update_instrument_location`
**Purpose:** Update instrument location with validation  
**Authentication:** Required  
**Rate Limit:** 50 requests/minute per user  

**Parameters:**
```json
{
  "name": "string (required) - Profile name",
  "new_location": "string (required) - New location (max 100 chars)"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Location updated successfully",
  "old_location": "string",
  "new_location": "string"
}
```

**Validation:**
- `new_location`: Alphanumeric pattern, max 100 characters
- Write permissions required on profile
- Audit logging of location changes

### 3. Client Instrument Profile APIs

#### POST `/api/resource/Client Instrument Profile`
**Purpose:** Create client-submitted instrument profile  
**Authentication:** Required (Portal users allowed)  
**Permissions:** Create access or Portal User role  

**Request Schema:**
```json
{
  "serial_no": "string (required)",
  "instrument_model": "string (required, max 100 chars)",
  "instrument_category": "string (required, enum)",
  "instrument_owner": "string (required)",
  "repair_preferences": "string (optional, max 2000 chars)",
  "ownership_transfer_to": "string (optional)"
}
```

**Business Rules:**
- `verification_status` defaults to "Pending"
- `ownership_transfer_to` cannot be same as `instrument_owner`
- When approved, automatically creates Instrument Profile

#### PUT `/api/resource/Client Instrument Profile/{name}`
**Purpose:** Update client instrument profile  
**Authentication:** Required  
**Permissions:** Write access or ownership validation  

**Restricted Fields:**
- Only technicians can modify `verification_status`
- `technician_notes` required when status = "Rejected"

### 4. File Upload APIs

#### POST `/api/method/upload_file`
**Purpose:** Upload files with security validation  
**Authentication:** Required  
**Content-Type:** multipart/form-data  

**Security Validation:**
- **Allowed Extensions:** .pdf, .jpg, .jpeg, .png, .gif, .webp
- **Max File Size:** 10MB for images, 5MB for documents
- **MIME Type Validation:** Server-side content type verification
- **Virus Scanning:** Integration with enterprise antivirus
- **File Name Sanitization:** Remove malicious characters

**Parameters:**
```
file: Binary file data
doctype: "Instrument Profile" or "Client Instrument Profile"
docname: Document name to attach to
fieldname: Field name for attachment
```

## Authentication & Authorization

### Supported Authentication Methods

1. **Session Authentication**
   - Browser-based login sessions
   - CSRF token validation required
   - Session timeout: 8 hours (configurable)

2. **API Key Authentication**
   - Token-based authentication for API clients
   - Rate limiting: 1000 requests/hour per token
   - Token rotation: 90 days (configurable)

3. **OAuth 2.0 (Enterprise)**
   - Integration with enterprise SSO providers
   - Scope-based access control
   - Refresh token support

### Role-Based Permissions

| Role | Instrument Profile | Client Instrument Profile | File Upload |
|------|-------------------|---------------------------|-------------|
| **System Manager** | Full Access | Full Access | Full Access |
| **Repair Manager** | Full Access | Full Access | Full Access |
| **Technician** | Read/Write | Read/Write/Approve | Read/Write |
| **Customer** | Read (Own) | Read/Write (Own) | Read/Write (Own) |
| **Portal User** | Read (Permitted) | Create/Read (Own) | Upload (Own) |

### Permission Validation

All API endpoints implement:
```python
# Permission check example
if not frappe.has_permission("Instrument Profile", "read", doc_name):
    frappe.throw(_("Insufficient permissions"), frappe.PermissionError)

# Ownership validation for customers
if frappe.has_role("Customer") and doc.customer != frappe.session.user:
    frappe.throw(_("Access denied"), frappe.PermissionError)
```

## Error Handling

### Standard Error Response Format

```json
{
  "message": "Human-readable error message",
  "exception": "Technical error details (dev mode only)",
  "exc_type": "ValidationError | PermissionError | NotFoundError",
  "indicator": "red",
  "_server_messages": [
    {
      "message": "Detailed error information",
      "title": "Error Type",
      "indicator": "red"
    }
  ]
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Unprocessable Entity (business rule violations)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

### Error Logging

All errors are logged with:
- **Timestamp:** ISO 8601 format
- **User:** Current user identification
- **IP Address:** Client IP for security tracking
- **Request Data:** Sanitized request parameters
- **Stack Trace:** For debugging (internal logs only)
- **Error Classification:** Security, Business, Technical

## Rate Limiting

### Default Limits

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Read Operations | 1000 req/hour | Per user |
| Write Operations | 500 req/hour | Per user |
| File Uploads | 100 req/hour | Per user |
| Search/Filter | 200 req/hour | Per user |

### Rate Limit Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1609459200
```

## Data Validation

### Input Sanitization

All text inputs undergo:
1. **HTML Sanitization:** Remove malicious HTML/JavaScript
2. **SQL Injection Prevention:** Parameterized queries only
3. **XSS Protection:** Content Security Policy enforcement
4. **Length Validation:** Enforce maximum field lengths
5. **Pattern Validation:** Regex patterns for specific fields

### Field-Specific Validation

```python
# Example validation schema
{
    'serial_no': {
        'type': 'string',
        'pattern': '^[A-Z0-9-]{3,50}$',
        'required': True
    },
    'current_location': {
        'type': 'string',
        'pattern': '^[A-Za-z0-9\s-]{1,100}$',
        'sanitize': True
    },
    'initial_condition_notes': {
        'type': 'html',
        'max_length': 5000,
        'sanitize': True,
        'allowed_tags': ['p', 'br', 'strong', 'em']
    }
}
```

## Audit Logging

### Audit Trail Components

All API operations generate audit entries:
- **Operation Type:** CREATE, READ, UPDATE, DELETE
- **Document Type:** Instrument Profile, Client Instrument Profile
- **Document Name:** Unique identifier
- **User Details:** User ID, roles, IP address
- **Timestamp:** UTC timestamp with millisecond precision
- **Changes:** Field-level change tracking
- **Result:** Success/failure status

### Audit Log Format

```json
{
  "timestamp": "2025-10-02T14:30:00.123Z",
  "operation": "UPDATE",
  "doctype": "Instrument Profile",
  "docname": "IP-2025-001",
  "user": "user@company.com",
  "user_roles": ["Technician"],
  "ip_address": "192.168.1.100",
  "changes": {
    "current_location": {
      "old": "Shop Floor",
      "new": "Quality Control"
    }
  },
  "result": "success",
  "duration_ms": 45
}
```

## Performance Considerations

### Database Optimization

- **Indexes:** All query fields indexed appropriately
- **Query Optimization:** Efficient filtering and sorting
- **Connection Pooling:** Database connection management
- **Caching:** Redis-based caching for read-heavy operations

### Response Time Targets

| Operation Type | Target | Maximum |
|----------------|--------|---------|
| Simple Read | < 100ms | 500ms |
| Complex Read | < 200ms | 1000ms |
| Write Operations | < 300ms | 1500ms |
| File Upload | < 2s | 10s |

### Monitoring

Real-time monitoring of:
- **API Response Times:** P50, P95, P99 percentiles
- **Error Rates:** By endpoint and error type
- **Rate Limit Violations:** Tracking and alerting
- **Database Performance:** Query execution times
- **Security Events:** Failed authentications, permission violations

## Security Compliance

### Data Protection

- **PII Handling:** Customer data encrypted at rest
- **Data Retention:** Configurable retention policies
- **Data Export:** GDPR-compliant data portability
- **Data Deletion:** Right to be forgotten implementation

### Security Headers

All API responses include:
```
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
```

### Vulnerability Management

- **Dependency Scanning:** Automated vulnerability detection
- **Code Analysis:** Static security analysis (Bandit, CodeQL)
- **Penetration Testing:** Quarterly security assessments
- **Incident Response:** 24/7 security monitoring and response

## SDK and Client Libraries

### Python SDK Example

```python
from repair_portal_client import InstrumentProfileAPI

# Initialize client
client = InstrumentProfileAPI(
    base_url="https://api.company.com",
    api_key="your-api-key"
)

# Get profile summary
try:
    profile = client.get_profile_summary("IP-2025-001")
    print(f"Profile: {profile['name']}, Status: {profile['status']}")
except client.PermissionError:
    print("Access denied")
except client.ValidationError as e:
    print(f"Validation error: {e.message}")
```

### JavaScript SDK Example

```javascript
import { InstrumentProfileAPI } from '@company/repair-portal-sdk';

const client = new InstrumentProfileAPI({
  baseURL: 'https://api.company.com',
  apiKey: 'your-api-key'
});

// Update location
try {
  const result = await client.updateLocation('IP-2025-001', 'Quality Control');
  console.log('Location updated:', result.new_location);
} catch (error) {
  if (error.type === 'PermissionError') {
    console.error('Access denied');
  } else {
    console.error('Update failed:', error.message);
  }
}
```

## Deployment Considerations

### Environment Configuration

```yaml
# Production settings
database:
  connection_pool_size: 50
  query_timeout: 30s

security:
  rate_limit_enabled: true
  audit_logging: true
  file_scan_enabled: true

performance:
  cache_enabled: true
  cache_ttl: 300s
  response_compression: true
```

### Health Check Endpoints

- `GET /api/health` - Service health status
- `GET /api/health/database` - Database connectivity
- `GET /api/health/cache` - Cache service status
- `GET /api/health/security` - Security service status

---

**Document Classification:** Internal Use Only  
**Next Review Date:** 2025-12-01  
**Document Owner:** Platform Engineering Team  
**Security Review:** Completed 2025-10-02  