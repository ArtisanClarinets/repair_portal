// Path: repair_portal/instrument_profile/doctype/instrument_profile/instrument_profile.js
// Date: 2025-10-02
// Version: 3.0.0
// Description: Enhanced client-side controller for Instrument Profile with comprehensive error handling, accessibility features, validation, and improved user experience.
// Dependencies: frappe

frappe.ui.form.on('Instrument Profile', {
	onload(frm) {
		// Initialize accessibility features
		frm.setup_accessibility();
		
		// Set up keyboard shortcuts
		frm.setup_keyboard_shortcuts();
		
		// Configure real-time validation
		frm.setup_realtime_validation();
		
		// Initialize help system
		frm.setup_contextual_help();
	},

	refresh(frm) {
		try {
			// Clear any previous indicators
			frm.dashboard.clear_headline();
			frm.dashboard.clear_indicators();
			
			// Set up status indicators with enhanced error handling
			frm.setup_status_indicators();
			
			// Set up warranty tracking with alerts
			frm.setup_warranty_tracking();
			
			// Add custom action buttons
			frm.setup_action_buttons();
			
			// Configure field visibility and permissions
			frm.configure_form_permissions();
			
			// Set up data validation warnings
			frm.setup_validation_warnings();
			
		} catch (error) {
			console.error("Error in Instrument Profile refresh:", error);
			frappe.msgprint({
				title: __("Form Load Error"),
				message: __("There was an error loading the form. Please refresh the page."),
				indicator: "red"
			});
		}
	},

	status(frm) {
		// Update status-dependent UI elements
		frm.update_status_dependent_fields();
		
		// Show status change confirmation if needed
		frm.handle_status_change();
	},

	warranty_end_date(frm) {
		if (frm.doc.warranty_end_date) {
			frm.validate_warranty_date();
			frm.setup_warranty_alerts();
		}
	},

	customer(frm) {
		if (frm.doc.customer) {
			frm.load_customer_details();
		}
	},

	serial_number(frm) {
		if (frm.doc.serial_number) {
			frm.validate_serial_number();
			frm.check_serial_duplicates();
		}
	},

	before_save(frm) {
		return new Promise((resolve, reject) => {
			// Show validation progress
			frm.dashboard.show_progress(__("Validating Profile"), 30);
			
			// Comprehensive pre-save validation
			frm.validate_profile_data()
				.then(() => {
					frm.dashboard.show_progress(__("Saving Profile"), 80);
					resolve();
				})
				.catch(error => {
					frm.dashboard.hide_progress();
					frappe.msgprint({
						title: __("Validation Failed"),
						message: error.message || __("Please correct the errors and try again."),
						indicator: "red"
					});
					reject(error);
				});
		});
	},

	after_save(frm) {
		// Hide progress indicators
		frm.dashboard.hide_progress();
		
		// Show success notification
		frappe.show_alert({
			message: __("Instrument Profile saved successfully"),
			indicator: "green"
		});
		
		// Trigger dependent updates
		frm.trigger_profile_updates();
		
		// Update browser history for better navigation
		frm.update_browser_history();
	}
});

// Enhanced form methods for comprehensive functionality
$.extend(frappe.ui.form.Form.prototype, {
	setup_accessibility() {
		if (this.doctype !== 'Instrument Profile') return;
		
		// Add ARIA labels for screen readers
		this.wrapper.attr('role', 'form');
		this.wrapper.attr('aria-label', __('Instrument Profile Form'));
		
		// Add semantic labels to key fields
		if (this.fields_dict.customer) {
			this.fields_dict.customer.$wrapper.attr('aria-label', __('Select customer for this instrument'));
		}
		
		if (this.fields_dict.serial_number) {
			this.fields_dict.serial_number.$wrapper.attr('aria-label', __('Enter instrument serial number'));
		}
		
		if (this.fields_dict.status) {
			this.fields_dict.status.$wrapper.attr('aria-label', __('Current instrument status'));
		}
		
		// Add skip links for keyboard navigation
		this.wrapper.prepend(`
			<div class="skip-links">
				<a href="#main-content" class="sr-only sr-only-focusable">
					${__('Skip to main content')}
				</a>
			</div>
		`);
	},

	setup_keyboard_shortcuts() {
		if (this.doctype !== 'Instrument Profile') return;
		
		$(document).on('keydown', (e) => {
			// Ctrl+S to save
			if (e.ctrlKey && e.key === 's') {
				e.preventDefault();
				this.save();
				return false;
			}
			
			// Ctrl+Shift+S to sync
			if (e.ctrlKey && e.shiftKey && e.key === 'S') {
				e.preventDefault();
				this.sync_profile();
				return false;
			}
			
			// Escape to close dialogs
			if (e.key === 'Escape') {
				$('.modal').modal('hide');
			}
		});
	},

	setup_status_indicators() {
		if (this.doctype !== 'Instrument Profile') return;
		
		try {
			// Main status headline
			if (this.doc.status) {
				const status_color = this.get_status_color(this.doc.status);
				this.dashboard.set_headline(`
					<span class="indicator ${status_color}">
						${__('Status')}: ${this.doc.status}
					</span>
				`);
			}
			
			// Additional status indicators
			if (this.doc.last_service_date) {
				const days_since_service = frappe.datetime.get_diff(
					frappe.datetime.now_date(), 
					this.doc.last_service_date
				);
				
				const service_color = days_since_service > 365 ? 'red' : 
									  days_since_service > 180 ? 'orange' : 'green';
				
				this.dashboard.add_indicator(
					__('Last Service: {0} days ago', [days_since_service]),
					service_color
				);
			}
			
		} catch (error) {
			console.error("Error setting up status indicators:", error);
		}
	},

	get_status_color(status) {
		const status_colors = {
			'Active': 'green',
			'In Service': 'blue',
			'Maintenance': 'orange',
			'Retired': 'grey',
			'Damaged': 'red',
			'Lost': 'red'
		};
		return status_colors[status] || 'grey';
	},

	setup_warranty_tracking() {
		if (this.doctype !== 'Instrument Profile') return;
		
		try {
			if (this.doc.warranty_end_date) {
				const days_remaining = frappe.datetime.get_diff(
					this.doc.warranty_end_date, 
					frappe.datetime.now_date()
				);
				
				let warranty_color = 'green';
				let warranty_message = '';
				
				if (days_remaining < 0) {
					warranty_color = 'red';
					warranty_message = __('Warranty Expired {0} days ago', [Math.abs(days_remaining)]);
				} else if (days_remaining < 30) {
					warranty_color = 'red';
					warranty_message = __('Warranty Expires in {0} days', [days_remaining]);
				} else if (days_remaining < 90) {
					warranty_color = 'orange';
					warranty_message = __('Warranty Expires in {0} days', [days_remaining]);
				} else {
					warranty_message = __('Warranty Valid until {0}', [
						frappe.datetime.str_to_user(this.doc.warranty_end_date)
					]);
				}
				
				this.dashboard.add_indicator(warranty_message, warranty_color);
				
				// Add warranty alert for expired or expiring warranties
				if (days_remaining < 30) {
					this.setup_warranty_alert(days_remaining);
				}
			}
		} catch (error) {
			console.error("Error setting up warranty tracking:", error);
		}
	},

	setup_warranty_alert(days_remaining) {
		if (days_remaining < 0) {
			frappe.show_alert({
				message: __('Warranty has expired for this instrument'),
				indicator: 'red'
			}, 5);
		} else if (days_remaining < 30) {
			frappe.show_alert({
				message: __('Warranty expires soon - consider renewal'),
				indicator: 'orange'
			}, 5);
		}
	},

	setup_action_buttons() {
		if (this.doctype !== 'Instrument Profile') return;
		
		try {
			// Sync Now button with enhanced UX
			if (!this.is_new()) {
				this.add_custom_button(__('Sync Profile'), () => {
					this.sync_profile();
				}, __('Actions')).addClass('btn-primary');
				
				// View service history
				this.add_custom_button(__('Service History'), () => {
					this.view_service_history();
				}, __('View'));
				
				// Generate QR code
				this.add_custom_button(__('Generate QR Code'), () => {
					this.generate_qr_code();
				}, __('Tools'));
				
				// Export profile data
				this.add_custom_button(__('Export Data'), () => {
					this.export_profile_data();
				}, __('Tools'));
			}
		} catch (error) {
			console.error("Error setting up action buttons:", error);
		}
	},

	sync_profile() {
		// Enhanced sync with better UX
		const progress_dialog = frappe.show_progress(
			__('Syncing Profile'),
			0,
			100,
			__('Initializing sync...')
		);
		
		frappe.call({
			method: 'repair_portal.instrument_profile.services.profile_sync.sync_now',
			args: { 
				profile: this.doc.name,
				force_refresh: true
			},
			freeze: true,
			freeze_message: __('Syncing profile data...'),
			callback: (r) => {
				progress_dialog.set_percent(100);
				progress_dialog.set_message(__('Sync completed successfully'));
				
				setTimeout(() => {
					progress_dialog.hide();
					frappe.show_alert({
						message: __('Profile synchronized successfully'),
						indicator: 'green'
					});
					this.reload_doc();
				}, 1000);
			},
			error: (r) => {
				progress_dialog.hide();
				console.error("Sync error:", r);
				
				frappe.msgprint({
					title: __('Sync Failed'),
					message: r.message || __('Unable to sync profile. Please try again.'),
					indicator: 'red'
				});
			}
		});
	},

	validate_profile_data() {
		return new Promise((resolve, reject) => {
			const errors = [];
			
			// Required field validation
			if (!this.doc.customer) {
				errors.push(__("Customer is required"));
			}
			
			if (!this.doc.serial_number) {
				errors.push(__("Serial number is required"));
			}
			
			// Date validation
			if (this.doc.warranty_end_date && this.doc.purchase_date) {
				if (frappe.datetime.get_diff(this.doc.warranty_end_date, this.doc.purchase_date) < 0) {
					errors.push(__("Warranty end date cannot be before purchase date"));
				}
			}
			
			// Serial number format validation
			if (this.doc.serial_number && !this.validate_serial_format(this.doc.serial_number)) {
				errors.push(__("Serial number format is invalid"));
			}
			
			if (errors.length > 0) {
				reject(new Error(errors.join('\n')));
			} else {
				resolve();
			}
		});
	},

	validate_serial_format(serial) {
		// Basic serial number validation (alphanumeric, hyphens, underscores)
		const serial_pattern = /^[A-Za-z0-9\-_]+$/;
		return serial_pattern.test(serial) && serial.length >= 3;
	},

	load_customer_details() {
		if (!this.doc.customer) return;
		
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Customer",
				fieldname: ["customer_name", "customer_type", "territory"],
				filters: { name: this.doc.customer }
			},
			callback: (r) => {
				if (r.message) {
					// Update customer info display
					this.update_customer_info_display(r.message);
				}
			},
			error: (r) => {
				console.error("Customer details error:", r);
			}
		});
	},

	update_customer_info_display(customer_info) {
		// Add customer information to the form
		const customer_html = `
			<div class="customer-info alert alert-info">
				<strong>${__('Customer Info')}:</strong>
				${customer_info.customer_name} (${customer_info.customer_type})
			</div>
		`;
		
		this.$wrapper.find('.customer-info').remove();
		this.fields_dict.customer.$wrapper.after(customer_html);
	},

	view_service_history() {
		frappe.route_to_list("Service Record", {
			instrument_profile: this.doc.name
		});
	},

	generate_qr_code() {
		frappe.call({
			method: "repair_portal.instrument_profile.api.generate_qr_code",
			args: { profile: this.doc.name },
			callback: (r) => {
				if (r.message) {
					// Show QR code in dialog
					this.show_qr_code_dialog(r.message);
				}
			},
			error: (r) => {
				frappe.msgprint({
					title: __('QR Code Generation Failed'),
					message: __('Unable to generate QR code. Please try again.'),
					indicator: 'red'
				});
			}
		});
	},

	show_qr_code_dialog(qr_code_data) {
		const dialog = new frappe.ui.Dialog({
			title: __('Instrument QR Code'),
			fields: [
				{
					fieldtype: 'HTML',
					options: `
						<div class="text-center">
							<img src="${qr_code_data}" alt="QR Code" style="max-width: 300px;">
							<p class="text-muted">${__('Scan to view instrument profile')}</p>
						</div>
					`
				}
			],
			primary_action_label: __('Download'),
			primary_action: () => {
				// Download QR code
				const link = document.createElement('a');
				link.href = qr_code_data;
				link.download = `instrument_${this.doc.serial_number}_qr.png`;
				link.click();
				dialog.hide();
			}
		});
		dialog.show();
	},

	export_profile_data() {
		frappe.call({
			method: "repair_portal.instrument_profile.api.export_profile",
			args: { profile: this.doc.name },
			callback: (r) => {
				if (r.message) {
					// Download the exported data
					frappe.tools.downloadify(
						r.message, 
						null, 
						`instrument_profile_${this.doc.serial_number}.json`
					);
				}
			},
			error: (r) => {
				frappe.msgprint({
					title: __('Export Failed'),
					message: __('Unable to export profile data. Please try again.'),
					indicator: 'red'
				});
			}
		});
	},

	setup_contextual_help() {
		if (this.doctype !== 'Instrument Profile') return;
		
		// Add help text for key fields
		if (this.fields_dict.serial_number) {
			this.fields_dict.serial_number.$wrapper.find('input')
				.attr('placeholder', __('Enter unique serial number (e.g., ABC123456)'));
		}
		
		if (this.fields_dict.status) {
			this.fields_dict.status.$wrapper.append(`
				<div class="help-block text-muted">
					${__('Current operational status of the instrument')}
				</div>
			`);
		}
	}
});
