// Path: repair_portal/instrument_profile/doctype/client_instrument_profile/client_instrument_profile.js
// Date: 2025-10-02
// Version: 2.0.0
// Description: Enhanced client-side controller for Client Instrument Profile with comprehensive error handling, accessibility features, real-time validation, ownership transfer management, and improved user experience.
// Dependencies: frappe

frappe.ui.form.on('Client Instrument Profile', {
	onload(frm) {
		// Initialize enhanced UX features
		frm.setup_accessibility();
		frm.setup_keyboard_shortcuts();
		frm.setup_verification_monitoring();
		frm.setup_help_system();
	},

	refresh(frm) {
		try {
			// Set up all UI components with error handling
			frm.setup_action_buttons();
			frm.setup_status_indicators();
			frm.setup_ownership_transfer_ui();
			frm.configure_field_behavior();
			frm.setup_verification_workflow();
			
		} catch (error) {
			console.error("Error in Client Instrument Profile refresh:", error);
			frappe.msgprint({
				title: __("Form Load Error"),
				message: __("There was an error loading the form. Please refresh the page."),
				indicator: "red"
			});
		}
	},

	instrument_owner(frm) {
		frm.handle_owner_change();
	},

	verification_status(frm) {
		frm.update_verification_indicators();
	},

	ownership_transfer_to(frm) {
		frm.handle_transfer_field_change();
	},

	before_save(frm) {
		return new Promise((resolve, reject) => {
			frm.dashboard.show_progress(__("Validating Profile Data"), 50);
			
			frm.validate_all_fields()
				.then(() => {
					frm.dashboard.show_progress(__("Saving"), 90);
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
		frm.dashboard.hide_progress();
		frappe.show_alert({
			message: __("Client Instrument Profile saved successfully"),
			indicator: "green"
		});
		frm.update_verification_status();
	}
});

// Enhanced form methods
$.extend(frappe.ui.form.Form.prototype, {
	setup_accessibility() {
		if (this.doctype !== 'Client Instrument Profile') return;
		
		// Add ARIA labels for key fields
		this.wrapper.attr('role', 'form');
		this.wrapper.attr('aria-label', __('Client Instrument Profile Form'));
		
		if (this.fields_dict.instrument_owner) {
			this.fields_dict.instrument_owner.$wrapper.attr('aria-label', __('Select instrument owner'));
		}
		
		if (this.fields_dict.verification_status) {
			this.fields_dict.verification_status.$wrapper.attr('aria-label', __('Verification status'));
		}
		
		if (this.fields_dict.ownership_transfer_to) {
			this.fields_dict.ownership_transfer_to.$wrapper.attr('aria-label', __('Transfer ownership to'));
		}
	},

	setup_keyboard_shortcuts() {
		if (this.doctype !== 'Client Instrument Profile') return;
		
		$(document).on('keydown', (e) => {
			if (e.ctrlKey && e.key === 's') {
				e.preventDefault();
				this.save();
			}
			
			if (e.ctrlKey && e.shiftKey && e.key === 'T') {
				e.preventDefault();
				this.initiate_ownership_transfer();
			}
			
			if (e.ctrlKey && e.shiftKey && e.key === 'V') {
				e.preventDefault();
				this.verify_profile();
			}
		});
	},

	setup_action_buttons() {
		if (this.doctype !== 'Client Instrument Profile') return;
		
		// Clear existing custom buttons
		this.custom_buttons = {};
		
		if (this.is_new()) return;
		if (this.__actions_added) return;

		try {
			// Ownership transfer button (only for approved profiles)
			if (this.doc.verification_status === 'Approved') {
				this.add_custom_button(
					__("Transfer Ownership"),
					() => {
						this.initiate_ownership_transfer();
					},
					__("Actions")
				).addClass('btn-warning').attr('title', __('Transfer instrument ownership (Ctrl+Shift+T)'));
			}

			// Verification button (for pending profiles)
			if (this.doc.verification_status === 'Pending' && frappe.user_roles.includes('System Manager')) {
				this.add_custom_button(
					__("Verify Profile"),
					() => {
						this.verify_profile();
					},
					__("Actions")
				).addClass('btn-success').attr('title', __('Verify profile information (Ctrl+Shift+V)'));
			}

			// View related documents button
			this.add_custom_button(
				__("View Related"),
				() => {
					this.show_related_documents();
				},
				__("View")
			);

			// Generate profile report button
			this.add_custom_button(
				__("Profile Report"),
				() => {
					this.generate_profile_report();
				},
				__("Reports")
			);

			this.__actions_added = true;

		} catch (error) {
			console.error("Error setting up action buttons:", error);
		}
	},

	setup_status_indicators() {
		if (this.doctype !== 'Client Instrument Profile') return;
		
		// Verification status indicator
		if (this.doc.verification_status) {
			const colors = {
				'Pending': 'orange', 
				'Approved': 'green', 
				'Rejected': 'red'
			};
			
			this.dashboard.add_indicator(
				__('Verification: {0}', [this.doc.verification_status]),
				colors[this.doc.verification_status] || 'gray'
			);
		}

		// Ownership transfer status
		if (this.doc.ownership_transfer_to) {
			this.dashboard.add_indicator(
				__('Transfer Pending: {0}', [this.doc.ownership_transfer_to]),
				'blue'
			);
		}

		// Profile completeness indicator
		const completeness = this.calculate_profile_completeness();
		if (completeness < 100) {
			this.dashboard.add_indicator(
				__('Profile {0}% Complete', [completeness]),
				completeness > 75 ? 'green' : completeness > 50 ? 'orange' : 'red'
			);
		}
	},

	calculate_profile_completeness() {
		const required_fields = [
			'instrument_owner', 'instrument_serial_number', 
			'brand', 'model', 'verification_status'
		];
		
		let completed = 0;
		required_fields.forEach(field => {
			if (this.doc[field]) completed++;
		});
		
		return Math.round((completed / required_fields.length) * 100);
	},

	initiate_ownership_transfer() {
		if (this.doc.verification_status !== 'Approved') {
			frappe.msgprint({
				title: __("Transfer Not Available"),
				message: __("Profile must be approved before ownership can be transferred"),
				indicator: "orange"
			});
			return;
		}

		const dialog = new frappe.ui.Dialog({
			title: __('Transfer Instrument Ownership'),
			fields: [
				{
					fieldname: 'current_owner',
					label: __('Current Owner'),
					fieldtype: 'Data',
					default: this.doc.instrument_owner,
					read_only: 1
				},
				{
					fieldname: 'new_owner',
					label: __('New Owner'),
					fieldtype: 'Link',
					options: 'Customer',
					reqd: 1,
					get_query: () => {
						return {
							filters: [
								["Customer", "disabled", "=", 0],
								["Customer", "name", "!=", this.doc.instrument_owner]
							]
						};
					}
				},
				{
					fieldname: 'transfer_reason',
					label: __('Reason for Transfer'),
					fieldtype: 'Text',
					reqd: 1
				},
				{
					fieldname: 'transfer_date',
					label: __('Transfer Date'),
					fieldtype: 'Date',
					default: frappe.datetime.get_today(),
					reqd: 1
				}
			],
			primary_action_label: __('Transfer Ownership'),
			primary_action: (values) => {
				this.execute_ownership_transfer(values);
				dialog.hide();
			}
		});
		
		dialog.show();
	},

	execute_ownership_transfer(transfer_data) {
		const progress = frappe.show_progress(
			__("Transferring Ownership"),
			0,
			100,
			__("Processing transfer...")
		);

		try {
			progress.set_percent(30);
			progress.set_message(__("Validating transfer data..."));

			// Set transfer fields
			this.set_value('ownership_transfer_to', transfer_data.new_owner);
			this.set_value('transfer_reason', transfer_data.transfer_reason);
			this.set_value('transfer_date', transfer_data.transfer_date);

			progress.set_percent(60);
			progress.set_message(__("Saving transfer request..."));

			this.save().then(() => {
				progress.set_percent(80);
				progress.set_message(__("Creating transfer log..."));

				// Call server method to process transfer
				frappe.call({
					doc: this.doc,
					method: "process_ownership_transfer",
					callback: (r) => {
						progress.set_percent(100);
						progress.set_message(__("Transfer completed"));

						setTimeout(() => {
							progress.hide();
							frappe.show_alert({
								message: __("Ownership transfer initiated successfully"),
								indicator: "green"
							});
							this.refresh();
						}, 1000);
					},
					error: (r) => {
						progress.hide();
						console.error("Transfer error:", r);
						
						frappe.msgprint({
							title: __("Transfer Failed"),
							message: r.message || __("Failed to process ownership transfer"),
							indicator: "red"
						});
					}
				});
			});

		} catch (error) {
			progress.hide();
			console.error("Transfer execution error:", error);
			frappe.msgprint({
				title: __("Unexpected Error"),
				message: __("An unexpected error occurred during transfer"),
				indicator: "red"
			});
		}
	},

	verify_profile() {
		if (!frappe.user_roles.includes('System Manager')) {
			frappe.msgprint({
				title: __("Access Denied"),
				message: __("You don't have permission to verify profiles"),
				indicator: "red"
			});
			return;
		}

		const dialog = new frappe.ui.Dialog({
			title: __('Verify Profile Information'),
			fields: [
				{
					fieldname: 'verification_notes',
					label: __('Verification Notes'),
					fieldtype: 'Text',
					description: __('Add any notes about the verification process')
				},
				{
					fieldname: 'verification_action',
					label: __('Verification Action'),
					fieldtype: 'Select',
					options: 'Approved\nRejected',
					reqd: 1
				}
			],
			primary_action_label: __('Complete Verification'),
			primary_action: (values) => {
				this.complete_verification(values);
				dialog.hide();
			}
		});
		
		dialog.show();
	},

	complete_verification(verification_data) {
		this.set_value('verification_status', verification_data.verification_action);
		this.set_value('verification_notes', verification_data.verification_notes);
		this.set_value('verified_by', frappe.session.user);
		this.set_value('verified_on', frappe.datetime.now_datetime());

		this.save().then(() => {
			frappe.show_alert({
				message: __("Profile verification completed"),
				indicator: "green"
			});
			this.refresh();
		});
	},

	handle_owner_change() {
		// Clear transfer field if owner changed manually
		if (this.doc.ownership_transfer_to) {
			this.set_value('ownership_transfer_to', null);
			this.show_field_info('instrument_owner', 
				__("Transfer request cleared due to owner change"));
		}
	},

	handle_transfer_field_change() {
		if (this.doc.ownership_transfer_to) {
			this.show_field_warning('ownership_transfer_to', 
				__("Ownership transfer is pending - save to process"));
		} else {
			this.clear_field_error('ownership_transfer_to');
		}
	},

	validate_all_fields() {
		return new Promise((resolve, reject) => {
			const errors = [];

			// Required field validation
			if (!this.doc.instrument_owner) {
				errors.push(__("Instrument owner is required"));
			}

			if (!this.doc.instrument_serial_number) {
				errors.push(__("Instrument serial number is required"));
			}

			// Business logic validation
			if (this.doc.ownership_transfer_to === this.doc.instrument_owner) {
				errors.push(__("Cannot transfer ownership to the same owner"));
			}

			if (this.doc.verification_status === 'Rejected' && !this.doc.verification_notes) {
				errors.push(__("Verification notes are required when rejecting a profile"));
			}

			if (errors.length > 0) {
				reject(new Error(errors.join('\n')));
			} else {
				resolve();
			}
		});
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

	show_field_info(fieldname, message) {
		const field = this.fields_dict[fieldname];
		if (field) {
			field.$wrapper.find('.help-block').remove();
			field.$wrapper.append(`<div class="help-block text-info">${message}</div>`);
		}
	},

	clear_field_error(fieldname) {
		const field = this.fields_dict[fieldname];
		if (field) {
			field.$wrapper.removeClass('has-error has-warning');
			field.$wrapper.find('.help-block').remove();
		}
	},

	show_related_documents() {
		// Show related documents in a dialog
		frappe.route_options = {
			"instrument_owner": this.doc.instrument_owner
		};
		frappe.set_route("List", "Instrument Profile");
	},

	generate_profile_report() {
		// Open profile report
		frappe.set_route("query-report", "Client Profile Summary", {
			"client_profile": this.doc.name
		});
	},

	setup_help_system() {
		if (this.doctype !== 'Client Instrument Profile') return;

		// Add contextual help
		if (this.fields_dict.verification_status) {
			this.fields_dict.verification_status.$wrapper.find('select')
				.attr('title', __('Profile verification status - affects available actions'));
		}

		if (this.fields_dict.ownership_transfer_to) {
			this.fields_dict.ownership_transfer_to.$wrapper.find('input')
				.attr('placeholder', __('Select new owner for transfer'));
		}
	},

	update_verification_status() {
		// Check if verification status needs updating based on completeness
		setTimeout(() => {
			const completeness = this.calculate_profile_completeness();
			if (completeness === 100 && this.doc.verification_status === 'Pending') {
				this.show_field_info('verification_status', 
					__("Profile is complete and ready for verification"));
			}
		}, 1000);
	}
});
