# Path: repair_portal/instrument_profile/utils/input_validation.py
# Date: 2025-01-21
# Version: 1.0.0
# Description: Comprehensive input validation, sanitization, and XSS protection utilities for Fortune-500 security standards
# Dependencies: frappe, bleach, html, re, urllib.parse

import frappe
from frappe import _
import re
import html
import bleach
from typing import Any, Dict, List, Optional, Union
import json
from datetime import datetime
from urllib.parse import urlparse

# Security configuration
ALLOWED_HTML_TAGS = ['b', 'i', 'u', 'strong', 'em', 'br', 'p', 'div', 'span']
ALLOWED_HTML_ATTRIBUTES = {
    '*': ['class', 'style'],
    'a': ['href', 'title'],
    'div': ['id'],
    'span': ['id']
}

# Validation patterns
PATTERNS = {
    'serial_number': r'^[A-Z0-9\-_]{3,50}$',
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'phone': r'^[\+]?[1-9][\d]{0,15}$',
    'alphanumeric': r'^[a-zA-Z0-9\s\-_]{1,}$',
    'numeric': r'^[0-9]+(\.[0-9]+)?$',
    'alpha': r'^[a-zA-Z\s\-\']{1,}$',
    'url': r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$',
    'html_safe': r'^[a-zA-Z0-9\s\-_.,!?\'"()&;:]*$'
}

class ValidationError(frappe.ValidationError):
    """Custom validation error with detailed context"""
    pass

class InputValidator:
    """
    Comprehensive input validation and sanitization class
    Provides Fortune-500 level security for all user inputs
    """
    
    def __init__(self, strict_mode: bool = True, log_violations: bool = True):
        self.strict_mode = strict_mode
        self.log_violations = log_violations
        self.validation_context = {
            'user': frappe.session.user,
            'timestamp': frappe.utils.now(),
            'ip_address': frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else 'unknown'
        }
    
    def validate_and_sanitize(self, data: Dict[str, Any], schema: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate and sanitize input data according to schema
        
        Args:
            data: Input data to validate
            schema: Validation schema with field definitions
            
        Returns:
            Dict with validated and sanitized data
            
        Raises:
            ValidationError: If validation fails
        """
        
        validated_data = {}
        errors = []
        
        try:
            for field_name, field_config in schema.items():
                field_value = data.get(field_name)
                
                # Apply validation rules
                try:
                    validated_value = self._validate_field(field_name, field_value, field_config)
                    validated_data[field_name] = validated_value
                except ValidationError as e:
                    errors.append(str(e))
                    if self.log_violations:
                        self._log_validation_violation(field_name, field_value, str(e))
            
            # Check for unexpected fields
            unexpected_fields = set(data.keys()) - set(schema.keys())
            if unexpected_fields and self.strict_mode:
                errors.append(f"Unexpected fields: {', '.join(unexpected_fields)}")
            
            if errors:
                error_message = "; ".join(errors)
                if self.log_violations:
                    frappe.log_error(f"Input Validation Failed: {error_message}", "Input Validation")
                raise ValidationError(error_message)
            
            return validated_data
            
        except Exception as e:
            if self.log_violations:
                frappe.log_error(f"Validation Exception: {str(e)}", "Input Validation Error")
            raise
    
    def _validate_field(self, field_name: str, value: Any, config: Dict[str, Any]) -> Any:
        """Validate individual field according to configuration"""
        
        field_type = config.get('type', 'string')
        required = config.get('required', False)
        allow_empty = config.get('allow_empty', True)
        
        # Check required fields
        if required and (value is None or value == ''):
            raise ValidationError(f"Field '{field_name}' is required")
        
        # Skip validation for empty optional fields
        if value is None or (value == '' and allow_empty):
            return value
        
        # Type-specific validation
        if field_type == 'string':
            return self._validate_string(field_name, value, config)
        elif field_type == 'email':
            return self._validate_email(field_name, value, config)
        elif field_type == 'phone':
            return self._validate_phone(field_name, value, config)
        elif field_type == 'number':
            return self._validate_number(field_name, value, config)
        elif field_type == 'date':
            return self._validate_date(field_name, value, config)
        elif field_type == 'datetime':
            return self._validate_datetime(field_name, value, config)
        elif field_type == 'url':
            return self._validate_url(field_name, value, config)
        elif field_type == 'html':
            return self._validate_html(field_name, value, config)
        elif field_type == 'json':
            return self._validate_json(field_name, value, config)
        elif field_type == 'select':
            return self._validate_select(field_name, value, config)
        elif field_type == 'link':
            return self._validate_link(field_name, value, config)
        else:
            raise ValidationError(f"Unknown field type '{field_type}' for field '{field_name}'")
    
    def _validate_string(self, field_name: str, value: Any, config: Dict[str, Any]) -> str:
        """Validate string field with comprehensive security checks"""
        
        if not isinstance(value, str):
            try:
                value = str(value)
            except Exception:
                raise ValidationError(f"Field '{field_name}' must be a string")
        
        # Length validation
        min_length = config.get('min_length', 0)
        max_length = config.get('max_length', 1000)
        
        if len(value) < min_length:
            raise ValidationError(f"Field '{field_name}' must be at least {min_length} characters")
        
        if len(value) > max_length:
            raise ValidationError(f"Field '{field_name}' must not exceed {max_length} characters")
        
        # Pattern validation
        pattern = config.get('pattern')
        if pattern:
            if pattern in PATTERNS:
                pattern = PATTERNS[pattern]
            
            if not re.match(pattern, value):
                raise ValidationError(f"Field '{field_name}' has invalid format")
        
        # XSS protection
        sanitize = config.get('sanitize', True)
        if sanitize:
            value = self._sanitize_string(value)
        
        # SQL injection protection
        if self._contains_sql_injection(value):
            raise ValidationError(f"Field '{field_name}' contains potentially malicious content")
        
        return value
    
    def _validate_email(self, field_name: str, value: Any, config: Dict[str, Any]) -> str:
        """Validate email field"""
        
        if not isinstance(value, str):
            raise ValidationError(f"Field '{field_name}' must be a valid email string")
        
        value = value.strip().lower()
        
        if not frappe.utils.validate_email_address(value, throw=False):
            raise ValidationError(f"Field '{field_name}' must be a valid email address")
        
        # Additional security checks
        if len(value) > 254:  # RFC 5321 limit
            raise ValidationError(f"Field '{field_name}' email address is too long")
        
        return value
    
    def _validate_phone(self, field_name: str, value: Any, config: Dict[str, Any]) -> str:
        """Validate phone number field"""
        
        if not isinstance(value, str):
            value = str(value)
        
        # Remove common formatting characters
        cleaned_value = re.sub(r'[\s\-\(\)\.]+', '', value)
        
        if not re.match(PATTERNS['phone'], cleaned_value):
            raise ValidationError(f"Field '{field_name}' must be a valid phone number")
        
        return value
    
    def _validate_number(self, field_name: str, value: Any, config: Dict[str, Any]) -> Union[int, float]:
        """Validate numeric field"""
        
        try:
            if isinstance(value, str):
                # Check for potential code injection in numeric strings
                if not re.match(PATTERNS['numeric'], value):
                    raise ValidationError(f"Field '{field_name}' contains invalid numeric format")
                
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            elif not isinstance(value, (int, float)):
                raise ValidationError(f"Field '{field_name}' must be a number")
            
            # Range validation
            min_value = config.get('min_value')
            max_value = config.get('max_value')
            
            if min_value is not None and value < min_value:
                raise ValidationError(f"Field '{field_name}' must be at least {min_value}")
            
            if max_value is not None and value > max_value:
                raise ValidationError(f"Field '{field_name}' must not exceed {max_value}")
            
            return value
            
        except (ValueError, TypeError):
            raise ValidationError(f"Field '{field_name}' must be a valid number")
    
    def _validate_date(self, field_name: str, value: Any, config: Dict[str, Any]) -> str:
        """Validate date field"""
        
        if not isinstance(value, str):
            value = str(value)
        
        try:
            # Parse and validate date format
            parsed_date = frappe.utils.getdate(value)
            
            # Date range validation
            min_date = config.get('min_date')
            max_date = config.get('max_date')
            
            if min_date and parsed_date < frappe.utils.getdate(min_date):
                raise ValidationError(f"Field '{field_name}' date is too early")
            
            if max_date and parsed_date > frappe.utils.getdate(max_date):
                raise ValidationError(f"Field '{field_name}' date is too late")
            
            return frappe.utils.formatdate(parsed_date)
            
        except Exception:
            raise ValidationError(f"Field '{field_name}' must be a valid date")
    
    def _validate_datetime(self, field_name: str, value: Any, config: Dict[str, Any]) -> str:
        """Validate datetime field"""
        
        if not isinstance(value, str):
            value = str(value)
        
        try:
            # Parse and validate datetime format
            parsed_datetime = frappe.utils.get_datetime(value)
            return frappe.utils.get_datetime_str(parsed_datetime)
            
        except Exception:
            raise ValidationError(f"Field '{field_name}' must be a valid datetime")
    
    def _validate_url(self, field_name: str, value: Any, config: Dict[str, Any]) -> str:
        """Validate URL field"""
        
        if not isinstance(value, str):
            value = str(value)
        
        value = value.strip()
        
        if not re.match(PATTERNS['url'], value):
            raise ValidationError(f"Field '{field_name}' must be a valid URL")
        
        # Security checks for URLs
        allowed_schemes = config.get('allowed_schemes', ['http', 'https'])
        parsed_url = urlparse(value)
        
        if parsed_url.scheme not in allowed_schemes:
            raise ValidationError(f"Field '{field_name}' URL scheme not allowed")
        
        if not parsed_url.netloc:
            raise ValidationError(f"Field '{field_name}' must include a valid host")
        
        disallowed_hosts = {host.lower() for host in config.get('disallowed_hosts', [])}
        if parsed_url.hostname and parsed_url.hostname.lower() in disallowed_hosts:
            raise ValidationError(f"Field '{field_name}' URL host is not permitted")
        
        return value
    
    def _validate_html(self, field_name: str, value: Any, config: Dict[str, Any]) -> str:
        """Validate and sanitize HTML field"""
        
        if not isinstance(value, str):
            value = str(value)
        
        # Sanitize HTML content
        allowed_tags = config.get('allowed_tags', ALLOWED_HTML_TAGS)
        allowed_attributes = config.get('allowed_attributes', ALLOWED_HTML_ATTRIBUTES)
        
        sanitized_value = bleach.clean(
            value,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
        
        return sanitized_value
    
    def _validate_json(self, field_name: str, value: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate JSON field"""
        
        if isinstance(value, dict):
            return value
        
        if not isinstance(value, str):
            value = str(value)
        
        try:
            parsed_json = json.loads(value)
            
            # Validate JSON structure if schema provided
            json_schema = config.get('schema')
            if json_schema:
                # Recursive validation for nested JSON
                validator = InputValidator(self.strict_mode, self.log_violations)
                return validator.validate_and_sanitize(parsed_json, json_schema)
            
            return parsed_json
            
        except json.JSONDecodeError:
            raise ValidationError(f"Field '{field_name}' must be valid JSON")
    
    def _validate_select(self, field_name: str, value: Any, config: Dict[str, Any]) -> str:
        """Validate select field against allowed options"""
        
        if not isinstance(value, str):
            value = str(value)
        
        allowed_options = config.get('options', [])
        if not allowed_options:
            raise ValidationError(f"Field '{field_name}' has no allowed options defined")
        
        if value not in allowed_options:
            raise ValidationError(f"Field '{field_name}' must be one of: {', '.join(allowed_options)}")
        
        return value
    
    def _validate_link(self, field_name: str, value: Any, config: Dict[str, Any]) -> str:
        """Validate link field against target DocType"""
        
        if not isinstance(value, str):
            value = str(value)
        
        target_doctype = config.get('target_doctype')
        if not target_doctype:
            raise ValidationError(f"Field '{field_name}' missing target DocType configuration")
        
        # Check if target document exists
        if not frappe.db.exists(target_doctype, value):
            raise ValidationError(f"Field '{field_name}' references non-existent {target_doctype}: {value}")
        
        # Check permissions
        if not frappe.has_permission(target_doctype, 'read', value):
            raise ValidationError(f"Field '{field_name}' insufficient permissions for {target_doctype}: {value}")
        
        return value
    
    def _sanitize_string(self, value: str) -> str:
        """Sanitize string to prevent XSS attacks"""
        
        # HTML escape
        value = html.escape(value)
        
        # Remove potentially dangerous patterns
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'data:',
            r'on\w+\s*=',
            r'expression\s*\(',
            r'@import',
            r'binding\s*:'
        ]
        
        for pattern in dangerous_patterns:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE | re.DOTALL)
        
        return value
    
    def _contains_sql_injection(self, value: str) -> bool:
        """Check for potential SQL injection patterns"""
        
        sql_patterns = [
            r'\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\s',
            r'[\'\"]\s*(or|and)\s*[\'\"]\s*=\s*[\'\"]\s*[\'\"]\s*(or|and)',
            r';\s*(drop|delete|update|insert)',
            r'--\s*$',
            r'/\*.*?\*/',
            r'\bxp_cmdshell\b',
            r'\bsp_executesql\b'
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, value, re.IGNORECASE | re.MULTILINE):
                return True
        
        return False
    
    def _log_validation_violation(self, field_name: str, field_value: Any, error_message: str):
        """Log validation violations for security monitoring"""
        
        try:
            log_data = {
                'field_name': field_name,
                'field_value': str(field_value)[:100] if field_value else '',  # Truncate for logs
                'error_message': error_message,
                'user': self.validation_context['user'],
                'timestamp': self.validation_context['timestamp'],
                'ip_address': self.validation_context['ip_address'],
                'user_agent': frappe.local.request.headers.get('User-Agent', 'unknown') if hasattr(frappe.local, 'request') else 'unknown'
            }
            
            frappe.logger("security").warning(f"Input validation violation: {json.dumps(log_data)}")
            
        except Exception as e:
            frappe.logger("security").error(f"Failed to log validation violation: {str(e)}")

# Convenience functions for common validation patterns
def validate_instrument_profile_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Instrument Profile input data"""
    
    schema = {
        'serial_no': {
            'type': 'string',
            'required': True,
            'pattern': 'serial_number',
            'min_length': 3,
            'max_length': 50
        },
        'instrument_model': {
            'type': 'link',
            'target_doctype': 'Instrument Model',
            'required': True
        },
        'customer': {
            'type': 'link',
            'target_doctype': 'Customer',
            'required': False
        },
        'status': {
            'type': 'select',
            'options': ['Active', 'Inactive', 'Under Maintenance', 'Under Repair', 'Retired'],
            'required': True
        },
        'workflow_state': {
            'type': 'select',
            'options': ['Open', 'In Progress', 'Delivered', 'Archived'],
            'required': False
        },
        'notes': {
            'type': 'html',
            'required': False,
            'max_length': 5000
        }
    }
    
    validator = InputValidator()
    return validator.validate_and_sanitize(data, schema)

def validate_customer_external_work_log_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Customer External Work Log input data"""
    
    schema = {
        'instrument_profile': {
            'type': 'link',
            'target_doctype': 'Instrument Profile',
            'required': True
        },
        'work_type': {
            'type': 'select',
            'options': ['Repair', 'Maintenance', 'Inspection', 'Modification', 'Other'],
            'required': True
        },
        'provider': {
            'type': 'string',
            'required': True,
            'pattern': 'alpha',
            'min_length': 2,
            'max_length': 100
        },
        'work_date': {
            'type': 'date',
            'required': True,
            'max_date': 'today'
        },
        'cost': {
            'type': 'number',
            'min_value': 0,
            'max_value': 10000
        },
        'description': {
            'type': 'html',
            'required': False,
            'max_length': 2000
        }
    }
    
    validator = InputValidator()
    return validator.validate_and_sanitize(data, schema)

def validate_client_instrument_profile_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Client Instrument Profile input data"""
    
    schema = {
        'instrument_profile': {
            'type': 'link',
            'target_doctype': 'Instrument Profile',
            'required': True
        },
        'customer': {
            'type': 'link',
            'target_doctype': 'Customer',
            'required': True
        },
        'preferred_service_schedule': {
            'type': 'select',
            'options': ['Monthly', 'Quarterly', 'Semi-Annual', 'Annual', 'As Needed'],
            'required': False
        },
        'special_instructions': {
            'type': 'html',
            'required': False,
            'max_length': 3000
        },
        'contact_preference': {
            'type': 'select',
            'options': ['Email', 'Phone', 'Text', 'Mail'],
            'required': False
        }
    }
    
    validator = InputValidator()
    return validator.validate_and_sanitize(data, schema)