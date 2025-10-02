# Path: repair_portal/instrument_profile/cron/warranty_expiry_check.py
# Date: 2025-01-21
# Version: 2.0.0
# Description: Enterprise-grade cron job for warranty expiry monitoring with batch processing, error recovery, monitoring, and configurable notifications
# Dependencies: frappe, frappe.utils, repair_portal settings

import frappe
from frappe import _
from frappe.utils import add_days, nowdate, get_datetime, format_date, cint, flt, get_fullname
from frappe.utils.background_jobs import enqueue
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta

# Configuration constants
DEFAULT_BATCH_SIZE = 50
DEFAULT_EXPIRY_THRESHOLD_DAYS = 30
DEFAULT_EARLY_WARNING_DAYS = 60
MAX_RETRIES = 3
RATE_LIMIT_DELAY = 1  # seconds between batches

def execute():
    """
    Main entry point for warranty expiry check cron job.
    Implements enterprise-grade batch processing with comprehensive error handling.
    """
    job_start_time = get_datetime()
    job_id = f"warranty_check_{int(job_start_time.timestamp())}"
    
    try:
        # Initialize job logging
        frappe.logger("warranty_cron").info(f"Starting warranty expiry check job {job_id}")
        
        # Load configuration
        config = load_warranty_check_config()
        
        # Validate system state
        if not validate_system_state():
            frappe.logger("warranty_cron").error("System validation failed, aborting warranty check")
            return
        
        # Execute warranty check with batch processing
        result = execute_warranty_check_batched(config, job_id)
        
        # Generate job completion report
        generate_job_report(job_id, job_start_time, result, config)
        
        frappe.logger("warranty_cron").info(f"Completed warranty expiry check job {job_id}")
        
    except Exception as e:
        frappe.logger("warranty_cron").error(f"Warranty expiry check job {job_id} failed: {str(e)}")
        frappe.log_error(f"Warranty Expiry Check Error: {str(e)}", "Warranty Cron Job")
        
        # Send failure notification to system administrators
        send_job_failure_notification(job_id, str(e))
        raise

def load_warranty_check_config() -> Dict[str, Any]:
    """Load warranty check configuration from settings with fallback defaults"""
    
    try:
        # Try to load from Repair Portal Settings
        settings = frappe.get_single("Repair Portal Settings")
        config = {
            "batch_size": getattr(settings, "warranty_check_batch_size", DEFAULT_BATCH_SIZE),
            "expiry_threshold_days": getattr(settings, "warranty_expiry_threshold_days", DEFAULT_EXPIRY_THRESHOLD_DAYS),
            "early_warning_days": getattr(settings, "warranty_early_warning_days", DEFAULT_EARLY_WARNING_DAYS),
            "enable_customer_notifications": getattr(settings, "enable_warranty_customer_notifications", True),
            "enable_admin_notifications": getattr(settings, "enable_warranty_admin_notifications", True),
            "admin_email_list": getattr(settings, "warranty_admin_email_list", "admin@artisanclarinets.com"),
            "rate_limit_enabled": getattr(settings, "enable_warranty_rate_limiting", True),
            "max_notifications_per_run": getattr(settings, "max_warranty_notifications_per_run", 100),
            "enable_performance_monitoring": getattr(settings, "enable_warranty_performance_monitoring", True)
        }
    except Exception as e:
        frappe.logger("warranty_cron").warning(f"Could not load settings, using defaults: {str(e)}")
        config = {
            "batch_size": DEFAULT_BATCH_SIZE,
            "expiry_threshold_days": DEFAULT_EXPIRY_THRESHOLD_DAYS,
            "early_warning_days": DEFAULT_EARLY_WARNING_DAYS,
            "enable_customer_notifications": True,
            "enable_admin_notifications": True,
            "admin_email_list": "admin@artisanclarinets.com",
            "rate_limit_enabled": True,
            "max_notifications_per_run": 100,
            "enable_performance_monitoring": True
        }
    
    # Validate configuration values
    config["batch_size"] = max(1, min(cint(config["batch_size"]), 1000))
    config["expiry_threshold_days"] = max(1, min(cint(config["expiry_threshold_days"]), 365))
    config["early_warning_days"] = max(config["expiry_threshold_days"], min(cint(config["early_warning_days"]), 730))
    config["max_notifications_per_run"] = max(1, min(cint(config["max_notifications_per_run"]), 1000))
    
    frappe.logger("warranty_cron").info(f"Loaded warranty check configuration: {config}")
    return config

def validate_system_state() -> bool:
    """Validate system state before running warranty checks"""
    
    try:
        # Check if required DocTypes exist
        required_doctypes = ["Instrument Profile", "Customer", "User"]
        for doctype in required_doctypes:
            if not frappe.db.table_exists(f"tab{doctype}"):
                frappe.logger("warranty_cron").error(f"Required DocType {doctype} does not exist")
                return False
        
        # Check database connectivity
        frappe.db.sql("SELECT 1")
        
        # Check email configuration
        if not frappe.conf.get("mail_server"):
            frappe.logger("warranty_cron").warning("No mail server configured, notifications may fail")
        
        # Check for required fields
        if not frappe.db.has_column("Instrument Profile", "warranty_end_date"):
            frappe.logger("warranty_cron").error("Instrument Profile missing warranty_end_date field")
            return False
        
        frappe.logger("warranty_cron").info("System state validation passed")
        return True
        
    except Exception as e:
        frappe.logger("warranty_cron").error(f"System state validation failed: {str(e)}")
        return False

def execute_warranty_check_batched(config: Dict[str, Any], job_id: str) -> Dict[str, Any]:
    """Execute warranty check with batch processing and comprehensive monitoring"""
    
    batch_size = config["batch_size"]
    expiry_threshold_days = config["expiry_threshold_days"]
    early_warning_days = config["early_warning_days"]
    
    today = nowdate()
    expiry_threshold_date = add_days(today, expiry_threshold_days)
    early_warning_date = add_days(today, early_warning_days)
    
    result = {
        "total_instruments_checked": 0,
        "expiring_soon_count": 0,
        "early_warning_count": 0,
        "notifications_sent": 0,
        "errors_encountered": 0,
        "batches_processed": 0,
        "processing_time_seconds": 0,
        "instruments_processed": []
    }
    
    start_time = get_datetime()
    
    try:
        # Get instruments requiring warranty checks with batch processing
        offset = 0
        notification_count = 0
        max_notifications = config["max_notifications_per_run"]
        
        while True:
            # Get batch of instruments
            instruments_batch = get_warranty_candidates_batch(
                today, early_warning_date, batch_size, offset
            )
            
            if not instruments_batch:
                break
            
            result["batches_processed"] += 1
            batch_start_time = get_datetime()
            
            frappe.logger("warranty_cron").info(
                f"Processing batch {result['batches_processed']}, "
                f"instruments {offset + 1}-{offset + len(instruments_batch)}"
            )
            
            # Process batch with error handling
            batch_result = process_warranty_batch(
                instruments_batch, config, today, expiry_threshold_date, job_id
            )
            
            # Update result counters
            result["total_instruments_checked"] += len(instruments_batch)
            result["expiring_soon_count"] += batch_result["expiring_soon"]
            result["early_warning_count"] += batch_result["early_warning"]
            result["notifications_sent"] += batch_result["notifications_sent"]
            result["errors_encountered"] += batch_result["errors"]
            result["instruments_processed"].extend(batch_result["processed_instruments"])
            
            notification_count += batch_result["notifications_sent"]
            
            # Rate limiting and notification throttling
            if config["rate_limit_enabled"] and result["batches_processed"] > 1:
                frappe.utils.time.sleep(RATE_LIMIT_DELAY)
            
            # Stop if we've reached the notification limit
            if notification_count >= max_notifications:
                frappe.logger("warranty_cron").info(
                    f"Reached notification limit ({max_notifications}), stopping processing"
                )
                break
            
            # Performance monitoring
            batch_time = (get_datetime() - batch_start_time).total_seconds()
            frappe.logger("warranty_cron").debug(
                f"Batch {result['batches_processed']} processed in {batch_time:.2f} seconds"
            )
            
            offset += batch_size
        
        result["processing_time_seconds"] = (get_datetime() - start_time).total_seconds()
        
        frappe.logger("warranty_cron").info(
            f"Warranty check completed: {result['total_instruments_checked']} instruments checked, "
            f"{result['notifications_sent']} notifications sent"
        )
        
        return result
        
    except Exception as e:
        result["processing_time_seconds"] = (get_datetime() - start_time).total_seconds()
        result["errors_encountered"] += 1
        frappe.logger("warranty_cron").error(f"Batch processing failed: {str(e)}")
        raise

def get_warranty_candidates_batch(today: str, early_warning_date: str, batch_size: int, offset: int) -> List[Dict[str, Any]]:
    """Get batch of instruments that need warranty checking"""
    
    try:
        instruments = frappe.db.sql("""
            SELECT 
                ip.name,
                ip.serial_no,
                ip.instrument_model,
                ip.warranty_end_date,
                ip.customer,
                ip.workflow_state,
                ip.status,
                ip.owner,
                c.customer_name,
                c.email_id as customer_email,
                im.model_name
            FROM `tabInstrument Profile` ip
            LEFT JOIN `tabCustomer` c ON ip.customer = c.name
            LEFT JOIN `tabInstrument Model` im ON ip.instrument_model = im.name
            WHERE ip.warranty_end_date BETWEEN %s AND %s
              AND ip.workflow_state != 'Archived'
              AND ip.status != 'Retired'
              AND ip.warranty_end_date IS NOT NULL
            ORDER BY ip.warranty_end_date ASC, ip.creation ASC
            LIMIT %s OFFSET %s
        """, (today, early_warning_date, batch_size, offset), as_dict=True)
        
        return instruments
        
    except Exception as e:
        frappe.logger("warranty_cron").error(f"Failed to get warranty candidates batch: {str(e)}")
        return []

def process_warranty_batch(
    instruments: List[Dict[str, Any]], 
    config: Dict[str, Any], 
    today: str, 
    expiry_threshold_date: str,
    job_id: str
) -> Dict[str, Any]:
    """Process a batch of instruments for warranty notifications"""
    
    batch_result = {
        "expiring_soon": 0,
        "early_warning": 0, 
        "notifications_sent": 0,
        "errors": 0,
        "processed_instruments": []
    }
    
    for instrument in instruments:
        try:
            instrument_result = process_single_instrument(
                instrument, config, today, expiry_threshold_date, job_id
            )
            
            # Update batch counters
            if instrument_result["category"] == "expiring_soon":
                batch_result["expiring_soon"] += 1
            elif instrument_result["category"] == "early_warning":
                batch_result["early_warning"] += 1
            
            if instrument_result["notification_sent"]:
                batch_result["notifications_sent"] += 1
            
            batch_result["processed_instruments"].append({
                "name": instrument["name"],
                "serial_no": instrument["serial_no"],
                "warranty_end_date": instrument["warranty_end_date"],
                "category": instrument_result["category"],
                "notification_sent": instrument_result["notification_sent"],
                "customer": instrument.get("customer_name", "Unknown")
            })
            
        except Exception as e:
            batch_result["errors"] += 1
            frappe.logger("warranty_cron").error(
                f"Failed to process instrument {instrument.get('name', 'Unknown')}: {str(e)}"
            )
            
            batch_result["processed_instruments"].append({
                "name": instrument.get("name", "Unknown"),
                "serial_no": instrument.get("serial_no", "Unknown"),
                "warranty_end_date": instrument.get("warranty_end_date"),
                "category": "error",
                "notification_sent": False,
                "error": str(e)
            })
    
    return batch_result

def process_single_instrument(
    instrument: Dict[str, Any], 
    config: Dict[str, Any], 
    today: str, 
    expiry_threshold_date: str,
    job_id: str
) -> Dict[str, Any]:
    """Process a single instrument for warranty notifications"""
    
    warranty_end_date = instrument["warranty_end_date"]
    days_until_expiry = (get_datetime(warranty_end_date) - get_datetime(today)).days
    
    # Determine notification category
    if days_until_expiry <= config["expiry_threshold_days"]:
        category = "expiring_soon"
        priority = "high"
    else:
        category = "early_warning"
        priority = "medium"
    
    notification_sent = False
    
    try:
        # Check if notification was already sent recently
        if not should_send_notification(instrument["name"], category):
            frappe.logger("warranty_cron").debug(
                f"Skipping notification for {instrument['name']} - recently sent"
            )
            return {
                "category": category,
                "notification_sent": False,
                "days_until_expiry": days_until_expiry
            }
        
        # Send notifications based on configuration
        if config["enable_admin_notifications"]:
            send_admin_notification(instrument, days_until_expiry, priority, config, job_id)
            notification_sent = True
        
        if config["enable_customer_notifications"] and instrument.get("customer_email"):
            send_customer_notification(instrument, days_until_expiry, config, job_id)
            notification_sent = True
        
        # Log notification
        if notification_sent:
            log_warranty_notification(instrument["name"], category, days_until_expiry, job_id)
        
        return {
            "category": category,
            "notification_sent": notification_sent,
            "days_until_expiry": days_until_expiry
        }
        
    except Exception as e:
        frappe.logger("warranty_cron").error(
            f"Failed to send notification for instrument {instrument['name']}: {str(e)}"
        )
        raise

def should_send_notification(instrument_name: str, category: str) -> bool:
    """Check if notification should be sent based on recent notification history"""
    
    try:
        # Check for recent notifications (within last 7 days for expiring_soon, 30 days for early_warning)
        days_threshold = 7 if category == "expiring_soon" else 30
        cutoff_date = add_days(nowdate(), -days_threshold)
        
        recent_notification = frappe.db.exists("Communication", {
            "reference_doctype": "Instrument Profile",
            "reference_name": instrument_name,
            "subject": ["like", "%Warranty%"],
            "creation": [">=", cutoff_date]
        })
        
        return not recent_notification
        
    except Exception:
        # If we can't check, err on the side of sending notification
        return True

def send_admin_notification(
    instrument: Dict[str, Any], 
    days_until_expiry: int, 
    priority: str, 
    config: Dict[str, Any],
    job_id: str
):
    """Send warranty notification to administrators"""
    
    admin_emails = [email.strip() for email in config["admin_email_list"].split(",")]
    
    subject = f"🔔 Warranty {'URGENT ' if priority == 'high' else ''}Alert: {instrument['serial_no']}"
    
    if instrument.get("customer_name"):
        customer_info = f" (Customer: {instrument['customer_name']})"
    else:
        customer_info = " (No customer assigned)"
    
    message = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px;">
        <h2 style="color: {'#dc3545' if priority == 'high' else '#ffc107'};">
            Warranty {'Expiring Soon' if priority == 'high' else 'Early Warning'}
        </h2>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <strong>Instrument Details:</strong><br>
            • Serial Number: {instrument['serial_no']}<br>
            • Model: {instrument.get('model_name', 'Unknown')}<br>
            • Warranty Expires: {format_date(instrument['warranty_end_date'])}<br>
            • Days Remaining: {days_until_expiry}{customer_info}<br>
            • Current Status: {instrument.get('workflow_state', 'Unknown')}
        </div>
        
        <div style="margin: 20px 0;">
            <strong>Recommended Actions:</strong><br>
            {'• Contact customer immediately for warranty renewal<br>' if priority == 'high' else ''}
            • Review maintenance history<br>
            • Schedule preventive maintenance if needed<br>
            • Update customer communication records
        </div>
        
        <p style="font-size: 12px; color: #6c757d; margin-top: 30px;">
            Job ID: {job_id} | Generated: {frappe.utils.now_datetime()}
        </p>
    </div>
    """
    
    frappe.sendmail(
        recipients=admin_emails,
        subject=subject,
        message=message,
        delayed=False,
        retry=MAX_RETRIES
    )

def send_customer_notification(
    instrument: Dict[str, Any], 
    days_until_expiry: int, 
    config: Dict[str, Any],
    job_id: str
):
    """Send warranty notification to customer"""
    
    customer_email = instrument.get("customer_email")
    if not customer_email:
        return
    
    customer_name = instrument.get("customer_name", "Valued Customer")
    
    subject = f"Warranty Notice: Your {instrument.get('model_name', 'Instrument')} Warranty"
    
    message = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px;">
        <h2 style="color: #007bff;">Warranty Notification</h2>
        
        <p>Dear {customer_name},</p>
        
        <p>This is a friendly reminder that the warranty for your instrument is approaching expiration.</p>
        
        <div style="background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <strong>Instrument Information:</strong><br>
            • Serial Number: {instrument['serial_no']}<br>
            • Model: {instrument.get('model_name', 'Unknown')}<br>
            • Warranty Expires: {format_date(instrument['warranty_end_date'])}<br>
            • Days Remaining: {days_until_expiry}
        </div>
        
        <div style="margin: 20px 0;">
            <p><strong>What happens next?</strong></p>
            <ul>
                <li>Contact us to discuss warranty extension options</li>
                <li>Schedule a maintenance check if needed</li>
                <li>Review your instrument care and maintenance</li>
            </ul>
        </div>
        
        <p>If you have any questions, please don't hesitate to contact us.</p>
        
        <p>Best regards,<br>
        Artisan Clarinets Team</p>
        
        <p style="font-size: 12px; color: #6c757d; margin-top: 30px;">
            This is an automated notification. Job ID: {job_id}
        </p>
    </div>
    """
    
    frappe.sendmail(
        recipients=[customer_email],
        subject=subject,
        message=message,
        delayed=True,
        retry=MAX_RETRIES
    )

def log_warranty_notification(instrument_name: str, category: str, days_until_expiry: int, job_id: str):
    """Log warranty notification for audit trail"""
    
    try:
        communication = frappe.get_doc({
            "doctype": "Communication",
            "communication_type": "Automated Email",
            "content": f"Warranty {category} notification sent ({days_until_expiry} days remaining)",
            "subject": f"Warranty Notification - {category}",
            "reference_doctype": "Instrument Profile",
            "reference_name": instrument_name,
            "status": "Sent",
            "sender": "warranty-cron@artisanclarinets.com"
        })
        communication.insert(ignore_permissions=True)
        
        frappe.logger("warranty_cron").info(
            f"Logged warranty notification for {instrument_name} (Job: {job_id})"
        )
        
    except Exception as e:
        frappe.logger("warranty_cron").warning(
            f"Could not log warranty notification for {instrument_name}: {str(e)}"
        )

def generate_job_report(job_id: str, start_time: datetime, result: Dict[str, Any], config: Dict[str, Any]):
    """Generate comprehensive job completion report"""
    
    end_time = get_datetime()
    total_time = (end_time - start_time).total_seconds()
    
    # Calculate performance metrics
    instruments_per_second = result["total_instruments_checked"] / max(total_time, 1)
    notifications_per_second = result["notifications_sent"] / max(total_time, 1)
    
    report = {
        "job_id": job_id,
        "execution_time": {
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "duration_seconds": total_time,
            "duration_formatted": f"{total_time:.2f}s"
        },
        "statistics": {
            "total_instruments_checked": result["total_instruments_checked"],
            "expiring_soon": result["expiring_soon_count"],
            "early_warning": result["early_warning_count"],
            "notifications_sent": result["notifications_sent"],
            "errors_encountered": result["errors_encountered"],
            "batches_processed": result["batches_processed"]
        },
        "performance": {
            "instruments_per_second": round(instruments_per_second, 2),
            "notifications_per_second": round(notifications_per_second, 2),
            "average_batch_size": round(result["total_instruments_checked"] / max(result["batches_processed"], 1), 2)
        },
        "configuration": config,
        "status": "SUCCESS" if result["errors_encountered"] == 0 else "COMPLETED_WITH_ERRORS"
    }
    
    # Log comprehensive report
    frappe.logger("warranty_cron").info(f"Job Report for {job_id}: {json.dumps(report, indent=2)}")
    
    # Send summary email to administrators if configured
    if config["enable_admin_notifications"] and config["enable_performance_monitoring"]:
        send_job_summary_email(report)

def send_job_summary_email(report: Dict[str, Any]):
    """Send job summary email to administrators"""
    
    try:
        subject = f"Warranty Check Job Summary - {report['status']}"
        
        message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px;">
            <h2>Warranty Expiry Check - Job Summary</h2>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <strong>Execution Summary:</strong><br>
                • Job ID: {report['job_id']}<br>
                • Duration: {report['execution_time']['duration_formatted']}<br>
                • Status: {report['status']}<br>
                • Instruments Checked: {report['statistics']['total_instruments_checked']}<br>
                • Notifications Sent: {report['statistics']['notifications_sent']}
            </div>
            
            <div style="background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <strong>Categories:</strong><br>
                • Expiring Soon (≤30 days): {report['statistics']['expiring_soon']}<br>
                • Early Warning (>30 days): {report['statistics']['early_warning']}<br>
                • Errors Encountered: {report['statistics']['errors_encountered']}
            </div>
            
            <div style="background-color: #d1ecf1; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <strong>Performance Metrics:</strong><br>
                • Processing Rate: {report['performance']['instruments_per_second']} instruments/sec<br>
                • Notification Rate: {report['performance']['notifications_per_second']} notifications/sec<br>
                • Batches Processed: {report['statistics']['batches_processed']}
            </div>
        </div>
        """
        
        frappe.sendmail(
            recipients=["admin@artisanclarinets.com"],
            subject=subject,
            message=message,
            delayed=True
        )
        
    except Exception as e:
        frappe.logger("warranty_cron").warning(f"Could not send job summary email: {str(e)}")

def send_job_failure_notification(job_id: str, error_message: str):
    """Send failure notification to system administrators"""
    
    try:
        subject = f"🚨 Warranty Check Job FAILED - {job_id}"
        
        message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px;">
            <h2 style="color: #dc3545;">Warranty Check Job Failed</h2>
            
            <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 15px 0; border: 1px solid #f5c6cb;">
                <strong>Error Details:</strong><br>
                Job ID: {job_id}<br>
                Timestamp: {frappe.utils.now_datetime()}<br>
                Error: {error_message}
            </div>
            
            <div style="margin: 20px 0;">
                <strong>Recommended Actions:</strong><br>
                • Check system logs for detailed error information<br>
                • Verify database connectivity and email configuration<br>
                • Review warranty check configuration settings<br>
                • Consider running job manually to diagnose issues
            </div>
            
            <p style="color: #721c24;">
                <strong>Important:</strong> Warranty notifications may not be sent until this issue is resolved.
            </p>
        </div>
        """
        
        frappe.sendmail(
            recipients=["admin@artisanclarinets.com"],
            subject=subject,
            message=message,
            delayed=False
        )
        
    except Exception as e:
        frappe.logger("warranty_cron").error(f"Could not send failure notification: {str(e)}")

# Background job functions for scalability
def enqueue_warranty_check():
    """Enqueue warranty check as background job for better performance"""
    
    return enqueue(
        "repair_portal.instrument_profile.cron.warranty_expiry_check.execute",
        timeout=3600,  # 1 hour timeout
        job_name="warranty_expiry_check",
        queue="default"
    )

def execute_async():
    """Async wrapper for background job execution"""
    execute()
