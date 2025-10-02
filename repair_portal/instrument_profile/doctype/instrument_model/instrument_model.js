// Path: repair_portal/instrument_profile/doctype/instrument_model/instrument_model.js
// Date: 2025-10-02
// Version: 2.0.0
// Description: Client-side controller for Instrument Model DocType with comprehensive error handling, validation, accessibility features, and user experience enhancements.
// Dependencies: frappe

frappe.ui.form.on("Instrument Model", {
	onload(frm) {
		// Set up accessibility attributes
		frm.setup_accessibility();
		
		// Configure auto-complete for common brand names
		frm.setup_brand_autocomplete();
		
		// Set up real-time validation
		frm.setup_realtime_validation();
	},

	refresh(frm) {
		try {
			// Add custom buttons with loading states
			frm.add_custom_buttons();
			
			// Update form status indicators
			frm.update_status_indicators();
			
			// Set up help text and tooltips
			frm.setup_help_system();
			
			// Configure field visibility based on user permissions
			frm.configure_field_visibility();
			
		} catch (error) {
			console.error("Error in Instrument Model refresh:", error);
			frappe.msgprint({
				title: __("Form Load Error"),
				message: __("There was an error loading the form. Please refresh the page."),
				indicator: "red"
			});
		}
	},

	brand(frm) {
		if (frm.doc.brand) {
			// Validate brand exists and show loading indicator
			frm.validate_brand_exists();
		}
	},

	model(frm) {
		if (frm.doc.model) {
			// Real-time validation for model naming
			frm.validate_model_format();
			
			// Check for potential duplicates
			frm.check_duplicate_models();
		}
	},

	instrument_category(frm) {
		if (frm.doc.instrument_category) {
			// Validate category and update related fields
			frm.update_category_related_fields();
		}
	},

	before_save(frm) {
		return new Promise((resolve, reject) => {
			// Show saving indicator
			frm.dashboard.show_progress(__("Validating"), 50);
			
			// Comprehensive validation before save
			frm.validate_all_fields()
				.then(() => {
					frm.dashboard.show_progress(__("Saving"), 100);
					resolve();
				})
				.catch(error => {
					frm.dashboard.hide_progress();
					frappe.msgprint({
						title: __("Validation Error"),
						message: error.message || __("Please check your inputs and try again."),
						indicator: "red"
					});
					reject(error);
				});
		});
	},

	after_save(frm) {
		// Clear progress indicators
		frm.dashboard.hide_progress();
		
		// Show success message with next steps
		frappe.show_alert({
			message: __("Instrument Model saved successfully"),
			indicator: "green"
		});
		
		// Update any dependent forms or lists
		frm.trigger_dependent_updates();
	}
});

// Extended form methods for enhanced functionality
$.extend(frappe.ui.form.Form.prototype, {
	setup_accessibility() {
		// Add ARIA labels and keyboard navigation
		this.fields_dict.brand.$wrapper.attr('aria-label', __('Select instrument brand'));
		this.fields_dict.model.$wrapper.attr('aria-label', __('Enter model name'));
		this.fields_dict.instrument_category.$wrapper.attr('aria-label', __('Select instrument category'));
		this.fields_dict.body_material.$wrapper.attr('aria-label', __('Enter body material'));
		
		// Add keyboard shortcuts
		$(document).on('keydown', (e) => {
			if (e.ctrlKey && e.key === 's' && this.doctype === 'Instrument Model') {
				e.preventDefault();
				this.save();
			}
		});
	},

	setup_brand_autocomplete() {
		// Enhanced autocomplete with error handling
		if (this.fields_dict.brand) {
			this.fields_dict.brand.get_query = () => {
				return {
					filters: { disabled: 0 },
					order_by: "brand asc"
				};
			};
		}
	},

	setup_realtime_validation() {
		// Real-time field validation with debouncing
		let validation_timeout;
		
		$(this.wrapper).on('input change', 'input, select, textarea', (e) => {
			clearTimeout(validation_timeout);
			validation_timeout = setTimeout(() => {
				this.validate_field_realtime(e.target);
			}, 500);
		});
	},

	validate_field_realtime(field) {
		const fieldname = $(field).attr('data-fieldname');
		const value = $(field).val();
		
		try {
			switch (fieldname) {
				case 'model':
					this.validate_model_format_sync(value);
					break;
				case 'body_material':
					this.validate_body_material_sync(value);
					break;
			}
		} catch (error) {
			this.show_field_error(fieldname, error.message);
		}
	},

	validate_model_format_sync(model) {
		if (!model) return;
		
		// Check model format (alphanumeric, hyphens, spaces allowed)
		const valid_pattern = /^[a-zA-Z0-9\s\-]+$/;
		if (!valid_pattern.test(model)) {
			throw new Error(__("Model name can only contain letters, numbers, spaces, and hyphens"));
		}
		
		// Clear any existing error
		this.clear_field_error('model');
	},

	validate_body_material_sync(material) {
		if (!material) return;
		
		// List of common materials for validation
		const common_materials = [
			'Grenadilla', 'Rosewood', 'Plastic', 'Metal', 'Carbon Fiber',
			'Ebonite', 'Boxwood', 'Cocobolo', 'Blackwood'
		];
		
		// Show suggestion if material doesn't match common ones
		if (!common_materials.includes(material)) {
			this.show_field_warning('body_material', 
				__("Consider using a standard material name for consistency"));
		} else {
			this.clear_field_error('body_material');
		}
	},

	show_field_error(fieldname, message) {
		const field = this.fields_dict[fieldname];
		if (field) {
			field.$wrapper.addClass('has-error');
			field.$wrapper.find('.help-block').remove();
			field.$wrapper.append(`<div class="help-block text-danger">${message}</div>`);
		}
	},

	show_field_warning(fieldname, message) {
		const field = this.fields_dict[fieldname];
		if (field) {
			field.$wrapper.addClass('has-warning');
			field.$wrapper.find('.help-block').remove();
			field.$wrapper.append(`<div class="help-block text-warning">${message}</div>`);
		}
	},

	clear_field_error(fieldname) {
		const field = this.fields_dict[fieldname];
		if (field) {
			field.$wrapper.removeClass('has-error has-warning');
			field.$wrapper.find('.help-block').remove();
		}
	},

	validate_brand_exists() {
		if (!this.doc.brand) return;
		
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Brand",
				fieldname: "disabled",
				filters: { name: this.doc.brand }
			},
			callback: (r) => {
				if (!r.message) {
					this.show_field_error('brand', __("Selected brand does not exist"));
				} else if (r.message.disabled) {
					this.show_field_error('brand', __("Selected brand is disabled"));
				} else {
					this.clear_field_error('brand');
				}
			},
			error: (r) => {
				console.error("Brand validation error:", r);
				this.show_field_error('brand', __("Unable to validate brand"));
			}
		});
	},

	check_duplicate_models() {
		if (!this.doc.brand || !this.doc.model) return;
		
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Instrument Model",
				filters: {
					brand: this.doc.brand,
					model: this.doc.model,
					name: ["!=", this.doc.name || ""]
				},
				limit: 1
			},
			callback: (r) => {
				if (r.message && r.message.length > 0) {
					this.show_field_warning('model', 
						__("A similar model already exists for this brand"));
				}
			},
			error: (r) => {
				console.error("Duplicate check error:", r);
			}
		});
	},

	validate_all_fields() {
		return new Promise((resolve, reject) => {
			const validations = [];
			
			// Validate required fields
			if (!this.doc.brand) {
				validations.push(Promise.reject(new Error(__("Brand is required"))));
			}
			
			if (!this.doc.model) {
				validations.push(Promise.reject(new Error(__("Model is required"))));
			}
			
			if (!this.doc.instrument_category) {
				validations.push(Promise.reject(new Error(__("Instrument Category is required"))));
			}
			
			// If no validation errors, resolve
			if (validations.length === 0) {
				resolve();
			} else {
				Promise.all(validations)
					.then(resolve)
					.catch(reject);
			}
		});
	},

	add_custom_buttons() {
		// Add helpful action buttons
		if (this.doc.name && !this.doc.__islocal) {
			this.add_custom_button(__("View Related Instruments"), () => {
				frappe.route_to_list("Instrument", {
					instrument_model: this.doc.name
				});
			});
			
			this.add_custom_button(__("Duplicate Model"), () => {
				this.duplicate_model();
			});
		}
	},

	duplicate_model() {
		frappe.prompt([
			{
				fieldtype: "Data",
				fieldname: "new_model",
				label: __("New Model Name"),
				reqd: 1
			}
		], (values) => {
			frappe.call({
				method: "frappe.client.clone_doc",
				args: {
					doctype: "Instrument Model",
					name: this.doc.name,
					new_name: values.new_model
				},
				callback: (r) => {
					if (r.message) {
						frappe.set_route("Form", "Instrument Model", r.message.name);
					}
				},
				error: (r) => {
					frappe.msgprint({
						title: __("Duplication Error"),
						message: __("Unable to duplicate model. Please try again."),
						indicator: "red"
					});
				}
			});
		}, __("Duplicate Instrument Model"));
	},

	update_status_indicators() {
		// Add visual status indicators
		if (this.doc.name && !this.doc.__islocal) {
			this.dashboard.add_indicator(__("Active"), "green");
		}
	},

	setup_help_system() {
		// Add contextual help
		this.fields_dict.model.$wrapper.find('input').attr('placeholder', 
			__('e.g., R13, E11, YCL-255'));
		
		this.fields_dict.body_material.$wrapper.find('input').attr('placeholder',
			__('e.g., Grenadilla, Rosewood, Plastic'));
	},

	configure_field_visibility() {
		// Configure field visibility based on user permissions
		if (!frappe.user.has_role('System Manager')) {
			// Hide advanced fields for non-admin users if needed
		}
	},

	trigger_dependent_updates() {
		// Refresh any dependent views
		if (window.cur_list && window.cur_list.doctype === 'Instrument Model') {
			window.cur_list.refresh();
		}
	}
});
