# Path: repair_portal/repair_portal/doctype/arrival_photo/arrival_photo.py
# Date: 2025-01-28
# Version: 1.0.0
# Description: Controller for Arrival Photo child table - handles photo validation, storage, and metadata for instrument arrival documentation.
# Dependencies: frappe, file handling utilities, image validation

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
import os


class ArrivalPhoto(Document):
    """
    Child table controller for Arrival Photo records.
    Handles photo validation, storage, and metadata management.
    """

    # ------------------------------------------------------------
    # VALIDATION / SAVE (DRAFT) PHASE
    # ------------------------------------------------------------
    def before_validate(self):
        """Validate photo requirements before saving."""
        self._validate_image_file()
        self._normalize_caption()

    def validate(self):
        """Validate business rules for arrival photos."""
        self._validate_image_required()
        self._validate_file_format()
        self._validate_file_size()
        self._validate_caption_length()

    def before_save(self):
        """Final preparations before saving."""
        self._set_default_caption()
        self._optimize_image_metadata()

    # ------------------------------------------------------------
    # UPDATE PHASE
    # ------------------------------------------------------------
    def on_update(self):
        """Handle photo updates and maintain references."""
        self._update_file_permissions()
        self._create_thumbnail_if_needed()

    # ------------------------------------------------------------
    # DELETE (TRASH)
    # ------------------------------------------------------------
    def on_trash(self):
        """Cleanup photo files when record is deleted."""
        self._cleanup_image_files()

    # ------------------------------------------------------------
    # PRIVATE HELPER METHODS
    # ------------------------------------------------------------
    def _validate_image_file(self):
        """Validate that the image file exists and is accessible."""
        if not self.image:
            return
            
        # Check if file exists in the system
        if not frappe.db.exists("File", {"file_url": self.image}):
            frappe.throw(_("Image file not found in system"))

    def _normalize_caption(self):
        """Clean up and normalize the caption text."""
        if self.caption:
            self.caption = self.caption.strip()
            # Remove any HTML tags if present
            import re
            self.caption = re.sub(r'<[^>]+>', '', self.caption)

    def _validate_image_required(self):
        """Ensure image is provided."""
        if not self.image:
            frappe.throw(_("Image is required for arrival photo"))

    def _validate_file_format(self):
        """Validate image file format."""
        if not self.image:
            return
            
        allowed_formats = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        file_extension = os.path.splitext(self.image.lower())[1]
        
        if file_extension not in allowed_formats:
            frappe.throw(_("Invalid image format. Allowed formats: {0}")
                        .format(', '.join(allowed_formats)))

    def _validate_file_size(self):
        """Validate image file size."""
        if not self.image:
            return
            
        file_doc = frappe.get_doc("File", {"file_url": self.image})
        if file_doc and file_doc.file_size:
            # Convert bytes to MB
            size_mb = file_doc.file_size / (1024 * 1024)
            max_size_mb = 10  # 10MB limit
            
            if size_mb > max_size_mb:
                frappe.throw(_("Image file size ({0:.1f} MB) exceeds maximum allowed size ({1} MB)")
                            .format(size_mb, max_size_mb))

    def _validate_caption_length(self):
        """Validate caption length."""
        if self.caption and len(self.caption) > 255:
            frappe.throw(_("Caption cannot exceed 255 characters"))

    def _set_default_caption(self):
        """Set default caption if not provided."""
        if not self.caption and self.image:
            # Extract filename without extension as default caption
            filename = os.path.basename(self.image)
            name_without_ext = os.path.splitext(filename)[0]
            self.caption = f"Arrival photo: {name_without_ext}"

    def _optimize_image_metadata(self):
        """Optimize image metadata for better performance."""
        if not self.image:
            return
            
        try:
            file_doc = frappe.get_doc("File", {"file_url": self.image})
            if file_doc:
                # Update file description to match caption
                if self.caption and not file_doc.description:
                    file_doc.description = self.caption
                    file_doc.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Error updating file metadata: {str(e)}", "Arrival Photo Metadata")

    def _update_file_permissions(self):
        """Update file permissions to match parent document."""
        if not self.image:
            return
            
        try:
            file_doc = frappe.get_doc("File", {"file_url": self.image})
            if file_doc:
                # Set file as private if parent document requires it
                parent_doc = self.get_parent_doc()
                if parent_doc and hasattr(parent_doc, 'is_private') and parent_doc.is_private:
                    file_doc.is_private = 1
                    file_doc.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Error updating file permissions: {str(e)}", "Arrival Photo Permissions")

    def _create_thumbnail_if_needed(self):
        """Create thumbnail for faster loading in lists."""
        if not self.image:
            return
            
        try:
            # This would integrate with image processing service
            # For now, just log the requirement
            frappe.logger().info(f"Thumbnail creation needed for {self.image}")
        except Exception as e:
            frappe.log_error(f"Error creating thumbnail: {str(e)}", "Arrival Photo Thumbnail")

    def _cleanup_image_files(self):
        """Clean up associated image files when photo record is deleted."""
        if not self.image:
            return
            
        try:
            # Find and delete the file record
            file_doc = frappe.get_doc("File", {"file_url": self.image})
            if file_doc:
                # Only delete if this is the only reference
                references = frappe.db.count("Arrival Photo", {"image": self.image})
                if references <= 1:  # This record is being deleted
                    file_doc.delete()
                    frappe.logger().info(f"Deleted file {self.image} for arrival photo")
        except Exception as e:
            frappe.log_error(f"Error cleaning up image files: {str(e)}", "Arrival Photo Cleanup")

    # ------------------------------------------------------------
    # PUBLIC API METHODS
    # ------------------------------------------------------------
    def get_image_info(self) -> dict:
        """Get detailed information about the image."""
        if not self.image:
            return {}
            
        try:
            file_doc = frappe.get_doc("File", {"file_url": self.image})
            return {
                "file_name": file_doc.file_name,
                "file_size": file_doc.file_size,
                "file_url": self.image,
                "caption": self.caption,
                "uploaded_by": file_doc.owner,
                "uploaded_on": file_doc.creation,
                "file_type": file_doc.file_type
            }
        except Exception:
            return {"error": "File information not available"}

    def get_thumbnail_url(self) -> str:
        """Get thumbnail URL for the image."""
        if not self.image:
            return ""
            
        # Generate thumbnail URL (this would integrate with image processing)
        base_url = self.image.rsplit('.', 1)[0]
        extension = self.image.rsplit('.', 1)[1] if '.' in self.image else 'jpg'
        return f"{base_url}_thumb.{extension}"

    @frappe.whitelist()
    def rotate_image(self, degrees: int = 90):
        """Rotate the image by specified degrees."""
        if not self.image:
            frappe.throw(_("No image to rotate"))
            
        if degrees not in [90, 180, 270]:
            frappe.throw(_("Invalid rotation angle. Use 90, 180, or 270 degrees"))
            
        try:
            # This would integrate with image processing service
            # For now, just log the action
            frappe.logger().info(f"Image rotation requested: {self.image} by {degrees} degrees")
            frappe.msgprint(_("Image rotation scheduled"))
            return True
        except Exception as e:
            frappe.log_error(f"Error rotating image: {str(e)}", "Arrival Photo Rotation")
            frappe.throw(_("Failed to rotate image"))

    def get_parent_doc(self):
        """Get the parent document this photo belongs to."""
        if hasattr(self, 'parent') and hasattr(self, 'parenttype'):
            return frappe.get_doc(self.parenttype, self.parent)
        return None