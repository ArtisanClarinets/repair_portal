# Clarinet Setup Log (`clarinet_setup_log`)

## Purpose
The Clarinet Setup Log DocType captures detailed activity logs and progress updates during clarinet setup projects. It provides an audit trail of all actions performed, time-stamped entries for project tracking, and comprehensive documentation for quality assurance and customer communication.

## Schema Summary

### Basic Information
- **DocType Type:** Master Document
- **Naming:** Auto-formatted as `CSL-{YY}{MM}-{#####}` (e.g., "CSL-2501-00001")
- **Engine:** InnoDB for transaction safety and referential integrity
- **Module:** Instrument Setup

### Core Identification
- **`customer`** (Link to Customer): Customer who owns the instrument (required, in list view)
- **`initial_setup`** (Link to Clarinet Initial Setup): Parent project being logged (required, in list view)
- **`instrument_profile`** (Link to Instrument Profile): Specific instrument being worked on (required, in list view)
- **`serial`** (Link to Instrument Serial Number): Unique instrument identifier (required, in list view)

### Activity Tracking
- **`log_time`** (Datetime): Timestamp of log entry (auto-populated with current datetime)
- **`action_by`** (Link to User): User who performed the logged action (defaults to session user)
- **`description`** (Text): Main description of the action or event logged
- **`notes`** (Text): Additional notes, observations, or context
- **`attachments`** (Attach): Supporting files, photos, or documentation

## Business Rules

### Automatic Population
1. **Log Time:** Automatically set to current datetime on creation
2. **Action By:** Defaults to currently logged-in user
3. **Sequential Naming:** Auto-generated with year/month prefix for organization

### Validation Rules
```python
def validate(self):
    """Validate setup log entry before saving"""
    self.validate_required_links()
    self.validate_log_time()
    self.validate_consistency()
    
def validate_required_links(self):
    """Ensure all required linked documents exist and are related"""
    if not self.customer or not self.initial_setup:
        frappe.throw("Customer and Initial Setup are required")
        
    if not self.instrument_profile or not self.serial:
        frappe.throw("Instrument Profile and Serial Number are required")
    
    # Validate relationships
    setup_customer = frappe.get_value("Clarinet Initial Setup", self.initial_setup, "customer")
    if setup_customer != self.customer:
        frappe.throw("Customer must match the Initial Setup project customer")

def validate_log_time(self):
    """Ensure log time is reasonable"""
    if self.log_time:
        from frappe.utils import now_datetime, add_days
        if self.log_time > now_datetime():
            frappe.throw("Log time cannot be in the future")
```

### Data Integrity
- All logged activities must reference valid, related documents
- Customer must match between setup project and instrument ownership
- Instrument profile must correspond to the serial number
- Log entries cannot be backdated beyond project start date

## Activity Types & Examples

### Progress Milestones
```python
milestone_logs = [
    {
        "description": "Project started - initial instrument inspection completed",
        "notes": "Instrument received in good overall condition. Minor pad replacement needed."
    },
    {
        "description": "Disassembly phase completed",
        "notes": "All components catalogued. Upper joint requires spring adjustment."
    },
    {
        "description": "Pad replacement completed",
        "notes": "Replaced 3 pads in upper joint. Used synthetic pads for improved durability."
    }
]
```

### Quality Control Events
```python
quality_logs = [
    {
        "description": "QC checkpoint: Leak test passed",
        "notes": "All pads sealing properly. Minimal air leakage within specifications."
    },
    {
        "description": "QC checkpoint: Intonation test completed", 
        "notes": "Intonation verified across all registers. A440 tuning confirmed."
    },
    {
        "description": "Final QC approval",
        "notes": "Setup meets all quality standards. Ready for customer pickup."
    }
]
```

### Issue Documentation
```python
issue_logs = [
    {
        "description": "Issue identified: Cracked tone hole",
        "notes": "Lower joint tone hole #7 has hairline crack. Requires specialized repair before setup can continue.",
        "attachments": "crack_photo_001.jpg"
    },
    {
        "description": "Issue resolved: Tone hole repaired",
        "notes": "Applied epoxy repair and refinished tone hole. Tested for air-tight seal.",
        "attachments": "repair_completion_002.jpg"
    }
]
```

### Customer Communication
```python
communication_logs = [
    {
        "description": "Customer notification: Additional work needed",
        "notes": "Called customer to inform about cracked tone hole. Obtained approval for repair work. Estimated additional 2 days."
    },
    {
        "description": "Customer notification: Setup completed",
        "notes": "Sent completion notification via email. Scheduled pickup appointment for tomorrow 2 PM."
    }
]
```

## Integration Points

### Project Management Integration
- **Timeline Updates:** Log entries provide real-time project status updates
- **Progress Tracking:** Major milestones logged automatically trigger progress calculations
- **Delay Documentation:** Issue logs provide explanation for project delays
- **Completion Verification:** Final QC logs validate project completion

### Customer Communication Integration
- **Transparency:** Customers can view relevant log entries for their instruments
- **Progress Updates:** Automated notifications generated from milestone logs  
- **Issue Alerts:** Problem logs trigger customer communication workflows
- **Completion Confirmation:** Final logs trigger pickup/delivery notifications

### Quality Assurance Integration
- **Audit Trail:** Complete record of all setup activities and decisions
- **Compliance Documentation:** QC checkpoints logged for certification
- **Issue Tracking:** Problems and resolutions documented for analysis
- **Performance Metrics:** Log data feeds into quality and efficiency reports

### Reporting Integration
```python
def generate_project_summary(initial_setup_id):
    """Generate comprehensive project summary from logs"""
    logs = frappe.get_all("Clarinet Setup Log", 
        filters={"initial_setup": initial_setup_id},
        fields=["log_time", "description", "notes", "action_by"],
        order_by="log_time"
    )
    
    summary = {
        "total_entries": len(logs),
        "project_duration": calculate_duration(logs),
        "technicians_involved": get_unique_technicians(logs),
        "major_milestones": filter_milestone_entries(logs),
        "issues_resolved": filter_issue_entries(logs)
    }
    return summary
```

## Automated Logging Triggers

### Setup Project Events
- **Project Start:** Automatic log when Initial Setup is created
- **Status Changes:** Workflow state transitions generate log entries
- **Task Completion:** Major setup tasks trigger milestone logs
- **Project Completion:** Final approval creates completion log

### System Integration Events
- **QC Tests:** Quality check results automatically logged
- **Material Usage:** Parts/materials usage creates activity logs
- **Time Tracking:** Work session start/stop events logged
- **Document Generation:** Certificate creation and delivery logged

### Custom Triggers
```python
@frappe.whitelist()
def log_custom_activity(initial_setup, description, notes=None, attachments=None):
    """Create custom log entry from setup workflow"""
    setup_doc = frappe.get_doc("Clarinet Initial Setup", initial_setup)
    
    log_entry = frappe.get_doc({
        "doctype": "Clarinet Setup Log",
        "customer": setup_doc.customer,
        "initial_setup": initial_setup,
        "instrument_profile": setup_doc.instrument_profile,
        "serial": setup_doc.serial,
        "description": description,
        "notes": notes,
        "attachments": attachments
    })
    log_entry.insert()
    return log_entry.name
```

## Permission Structure

### Role-Based Access
- **Technicians:** Can read logs for their assigned projects
- **Service Managers:** Full read/write access to all setup logs
- **Customers:** Can read logs for their own instruments only (if_owner rule)
- **Quality Managers:** Read access for audit and compliance purposes

### Data Security
- Customer data protected through role-based permissions
- Audit trail preserved - no deletion allowed after creation
- Sensitive notes and attachments restricted to internal roles
- Customer-visible entries filtered for appropriate content

## Reporting & Analytics

### Project Reporting
- **Activity Timeline:** Chronological view of project progress
- **Technician Performance:** Work quality and efficiency metrics
- **Issue Analysis:** Common problems and resolution patterns
- **Duration Analysis:** Time spent on different project phases

### Quality Metrics
- **Audit Compliance:** Complete documentation of quality checkpoints
- **Issue Rate:** Frequency and types of problems encountered
- **Resolution Time:** Speed of issue identification and fixing
- **Customer Satisfaction:** Correlation between logging detail and customer feedback

### Operational Insights
```python
def analyze_setup_efficiency():
    """Analyze setup efficiency from log data"""
    query = """
        SELECT 
            initial_setup,
            COUNT(*) as total_logs,
            MIN(log_time) as project_start,
            MAX(log_time) as project_end,
            TIMESTAMPDIFF(HOUR, MIN(log_time), MAX(log_time)) as duration_hours
        FROM `tabClarinet Setup Log`
        WHERE log_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        GROUP BY initial_setup
        ORDER BY duration_hours
    """
    return frappe.db.sql(query, as_dict=True)
```

## Data Retention & Archival

### Log Lifecycle
- **Active Phase:** Logs remain fully accessible during project execution
- **Completion Phase:** Logs become read-only after project completion
- **Archive Phase:** Old logs archived but remain accessible for compliance
- **Retention Policy:** Logs preserved for minimum 7 years for warranty support

### Storage Optimization
- Attachments stored in efficient format with compression
- Old logs indexed for fast search but moved to archive storage
- Regular cleanup of temporary or duplicate entries
- Backup strategy ensures long-term data preservation

## Test Plan

### Log Creation Tests
- **test_auto_population:** Verify automatic timestamp and user assignment
- **test_required_validation:** Ensure all required fields properly validated  
- **test_relationship_validation:** Confirm linked documents are related
- **test_naming_format:** Verify naming follows CSL-YYMM-##### pattern

### Integration Tests  
- **test_project_integration:** Log entries properly linked to setup projects
- **test_customer_access:** Customer permissions correctly enforced
- **test_reporting_data:** Log data feeds correctly into reports
- **test_workflow_triggers:** Automated logging triggers work properly

### Permission Tests
- **test_technician_access:** Technicians see only assigned project logs
- **test_customer_access:** Customers see only their instrument logs
- **test_manager_access:** Service managers have full access
- **test_audit_trail:** Modifications properly tracked and logged

### Performance Tests
- **test_large_datasets:** Performance with thousands of log entries
- **test_search_efficiency:** Fast log searching and filtering
- **test_report_generation:** Efficient report compilation from logs
- **test_archival_process:** Archive operations don't impact active system

## Security Considerations

### Data Protection
- Customer PII protected in log entries and attachments
- Access logging for all setup log views and modifications
- Secure attachment storage with proper access controls
- Regular security audits of log access patterns

### Audit Requirements
- Complete audit trail of who accessed what logs when
- Tamper-proof logging system prevents retroactive modifications
- Compliance with service industry recordkeeping regulations
- Integration with broader company audit and compliance systems

## Changelog
- **2025-08-17** – Created comprehensive setup activity logging system
- **2025-08-17** – Added automated logging triggers and customer permissions
- **2025-08-17** – Implemented reporting integration and analytics capabilities
- **2025-08-17** – Added security controls and audit trail functionality