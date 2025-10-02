// Path: repair_portal/instrument_profile/doctype/instrument_serial_number/instrument_serial_number.js
// Date: 2025-10-02
// Version: 2.0.0
// Description: Enhanced client-side controller for Instrument Serial Number with comprehensive error handling, accessibility features, real-time validation, duplicate detection, and improved user experience.
// Dependencies: frappe

frappe.ui.form.on("Instrument Serial", {
	onload(frm) {
		// Initialize accessibility and UX features
		frm.setup_accessibility();
		frm.setup_keyboard_shortcuts();
		frm.setup_realtime_validation();
		frm.setup_help_system();
	},

	refresh(frm) {
		try {
			// Set up all UI components with error handling
			frm.setup_action_buttons();
			frm.setup_status_indicators();
			frm.check_duplicates_advisory();
			frm.configure_field_behavior();
			
		} catch (error) {
			console.error("Error in Instrument Serial refresh:", error);
			frappe.msgprint({
				title: __("Form Load Error"),
				message: __("There was an error loading the form. Please refresh the page."),
				indicator: "red"
			});
		}
	},

	ownership_type(frm) {
		frm.handle_ownership_change();
	},

	brand(frm) {
		frm.check_duplicates_advisory();
		frm.validate_brand_field();
	},

	serial_no(frm) {
		frm.check_duplicates_advisory();
		frm.validate_serial_format();
	},

	model(frm) {
		frm.check_duplicates_advisory();
		frm.validate_model_field();
	},

	year_estimate(frm) {
		frm.check_duplicates_advisory();
		frm.validate_year_estimate();
	},

	instrument_type(frm) {
		frm.update_type_dependent_fields();
	},

	before_save(frm) {
		return new Promise((resolve, reject) => {
			frm.dashboard.show_progress(__("Validating Serial Number"), 50);
			
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
			message: __("Instrument Serial Number saved successfully"),
			indicator: "green"
		});
		frm.trigger_dependent_updates();
	}
});

// Enhanced form methods
$.extend(frappe.ui.form.Form.prototype, {
	setup_accessibility() {
		if (this.doctype !== 'Instrument Serial') return;
		
		// Add ARIA labels for key fields
		this.wrapper.attr('role', 'form');
		this.wrapper.attr('aria-label', __('Instrument Serial Number Form'));
		
		if (this.fields_dict.serial_no) {
			this.fields_dict.serial_no.$wrapper.attr('aria-label', __('Enter instrument serial number'));
		}
		
		if (this.fields_dict.brand) {
			this.fields_dict.brand.$wrapper.attr('aria-label', __('Enter instrument brand'));
		}
		
		if (this.fields_dict.model) {
			this.fields_dict.model.$wrapper.attr('aria-label', __('Enter instrument model'));
		}
		
		if (this.fields_dict.ownership_type) {
			this.fields_dict.ownership_type.$wrapper.attr('aria-label', __('Select ownership type'));
		}
	},

	setup_keyboard_shortcuts() {
		if (this.doctype !== 'Instrument Serial') return;
		
		$(document).on('keydown', (e) => {
			if (e.ctrlKey && e.key === 's') {
				e.preventDefault();
				this.save();
			}
			
			if (e.ctrlKey && e.shiftKey && e.key === 'C') {
				e.preventDefault();
				this.create_setup_shortcut();
			}
		});
	},

	setup_action_buttons() {
		if (this.doctype !== 'Instrument Serial') return;
		
		// Clear existing custom buttons
		this.custom_buttons = {};
		
		if (this.is_new()) return;
		if (this.__actions_added) return;

		try {
			// Enhanced "Create Clarinet Setup" button
			this.add_custom_button(
				__("Create Setup"),
				() => {
					this.create_clarinet_setup_enhanced();
				},
				__("Actions")
			).addClass('btn-primary').attr('title', __('Create Clarinet Initial Setup (Ctrl+Shift+C)'));

			// View related documents button
			this.add_custom_button(
				__("View Related"),
				() => {
					this.show_related_documents();
				},
				__("View")
			);

			// Duplicate check button
			this.add_custom_button(
				__("Check Duplicates"),
				() => {
					this.run_duplicate_check();
				},
				__("Tools")
			);

			// Generate barcode button
			this.add_custom_button(
				__("Generate Barcode"),
				() => {
					this.generate_barcode();
				},
				__("Tools")
			);

			this.__actions_added = true;

		} catch (error) {
			console.error("Error setting up action buttons:", error);
		}
	},

	create_clarinet_setup_enhanced() {
		// Show confirmation dialog first
		frappe.confirm(
			__('Create a new Clarinet Initial Setup for this instrument?'),
			() => {
				this.execute_setup_creation();
			},
			() => {
				// User cancelled
			}
		);
	},

	execute_setup_creation() {
		const progress = frappe.show_progress(
			__("Creating Setup"),
			0,
			100,
			__("Initializing...")
		);

		try {
			progress.set_percent(30);
			progress.set_message(__("Validating instrument data..."));

			frappe.call({
				doc: this.doc,
				method: "create_setup",
				freeze: true,
				freeze_message: __("Creating Clarinet Initial Setup..."),
				callback: (r) => {
					progress.set_percent(80);
					progress.set_message(__("Setup created successfully"));

					if (r && r.message && r.message.setup) {
						this.set_value("current_setup", r.message.setup);
						this.save().then(() => {
							progress.set_percent(100);
							progress.set_message(__("Redirecting..."));
							
							setTimeout(() => {
								progress.hide();
								frappe.show_alert({
									message: __("Setup created successfully"),
									indicator: "green"
								});
								frappe.set_route("Form", "Clarinet Initial Setup", r.message.setup);
							}, 1000);
						});
					} else {
						progress.hide();
						frappe.msgprint({
							title: __("Setup Creation Failed"),
							message: __("No setup was created. Please try again."),
							indicator: "orange"
						});
					}
				},
				error: (r) => {
					progress.hide();
					console.error("Setup creation error:", r);
					
					frappe.msgprint({
						title: __("Setup Creation Failed"),
						message: r.message || __("Failed to create setup. Please check the instrument data and try again."),
						indicator: "red"
					});
				}
			});

		} catch (error) {
			progress.hide();
			console.error("Setup creation error:", error);
			frappe.msgprint({
				title: __("Unexpected Error"),
				message: __("An unexpected error occurred. Please try again."),
				indicator: "red"
			});
		}
	},

	check_duplicates_advisory() {
		if (this.doctype !== 'Instrument Serial') return;
		if (this.is_new()) return;

		// Clear existing duplicate warnings
		this.clear_duplicate_warnings();

		// Debounced duplicate check
		frappe.debounce(() => {
			this.run_duplicate_check_background();
		}, 800)();
	},

	run_duplicate_check_background() {
		frappe.call({
			doc: this.doc,
			method: "check_possible_duplicates",
			callback: (r) => {
				const duplicates = (r && r.message) || [];
				if (duplicates.length > 0) {
					this.show_duplicate_warning(duplicates);
				}
			},
			error: (r) => {
				// Silent error - don't disrupt user workflow
				console.warn("Duplicate check failed:", r);
			}
		});
	},

	show_duplicate_warning(duplicates) {
		const duplicate_list = duplicates
			.map(d => `
				<div class="duplicate-item">
					<strong>${d.name}</strong> - 
					${d.brand || ''} ${d.model || ''} 
					(${d.instrument_type || ''})
				</div>
			`)
			.join('');

		this.dashboard.set_headline(`
			<div class="alert alert-warning">
				<i class="fa fa-warning"></i>
				${__("Possible duplicates detected")}
			</div>
		`);

		// Show detailed duplicate information
		this.$wrapper.find('.duplicate-details').remove();
		this.$wrapper.prepend(`
			<div class="duplicate-details alert alert-warning">
				<h4>${__("Potential Duplicate Instruments")}</h4>
				<p>${__("Similar instruments found in the system:")}</p>
				${duplicate_list}
				<button class="btn btn-sm btn-default view-duplicates-btn">
					${__("Review Duplicates")}
				</button>
			</div>
		`);

		// Add click handler for review button
		this.$wrapper.find('.view-duplicates-btn').on('click', () => {
			this.show_duplicate_review_dialog(duplicates);
		});
	},

	clear_duplicate_warnings() {
		this.$wrapper.find('.duplicate-details').remove();
		this.dashboard.clear_headline();
	},

	show_duplicate_review_dialog(duplicates) {
		const dialog = new frappe.ui.Dialog({
			title: __('Review Duplicate Instruments'),
			fields: [
				{
					fieldtype: 'HTML',
					options: `
						<div class="duplicate-review">
							<p>${__('The following instruments have similar characteristics:')}</p>
							<table class="table table-bordered">
								<thead>
									<tr>
										<th>${__('Name')}</th>
										<th>${__('Brand')}</th>
										<th>${__('Model')}</th>
										<th>${__('Type')}</th>
										<th>${__('Action')}</th>
									</tr>
								</thead>
								<tbody>
									${duplicates.map(d => `
										<tr>
											<td>${d.name}</td>
											<td>${d.brand || ''}</td>
											<td>${d.model || ''}</td>
											<td>${d.instrument_type || ''}</td>
											<td>
												<a href="/app/instrument-serial/${d.name}" target="_blank">
													${__('View')}
												</a>
											</td>
										</tr>
									`).join('')}
								</tbody>
							</table>
						</div>
					`
				}
			],
			primary_action_label: __('Continue Anyway'),
			primary_action: () => {
				dialog.hide();
			}
		});
		dialog.show();
	},

	validate_serial_format() {
		if (!this.doc.serial_no) return;

		const serial = this.doc.serial_no.trim();
		
		// Basic format validation
		if (serial.length < 3) {
			this.show_field_error('serial_no', __("Serial number must be at least 3 characters"));
			return;
		}

		// Check for valid characters (alphanumeric, hyphens, underscores)
		const valid_pattern = /^[A-Za-z0-9\-_]+$/;
		if (!valid_pattern.test(serial)) {
			this.show_field_error('serial_no', __("Serial number can only contain letters, numbers, hyphens, and underscores"));
			return;
		}

		this.clear_field_error('serial_no');
	},

	validate_year_estimate() {
		if (!this.doc.year_estimate) return;

		const year = parseInt(this.doc.year_estimate);
		const current_year = new Date().getFullYear();

		if (year < 1800 || year > current_year + 1) {
			this.show_field_error('year_estimate', 
				__("Year estimate should be between 1800 and {0}", [current_year + 1]));
			return;
		}

		this.clear_field_error('year_estimate');
	},

	handle_ownership_change() {
		const ownership_type = this.doc.ownership_type;
		
		// Show/hide fields based on ownership type
		if (["Customer Owned", "Consignment"].includes(ownership_type)) {
			this.toggle_reqd('owner_name', true);
			this.toggle_reqd('owner_contact', false);
		} else {
			this.toggle_reqd('owner_name', false);
			this.toggle_reqd('owner_contact', false);
		}

		// Show helpful message
		if (ownership_type === "Customer Owned") {
			this.show_field_info('ownership_type', 
				__("Please specify owner details for customer-owned instruments"));
		} else if (ownership_type === "Consignment") {
			this.show_field_info('ownership_type', 
				__("Consignment instruments require owner tracking"));
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

	validate_all_fields() {
		return new Promise((resolve, reject) => {
			const errors = [];

			// Required field validation
			if (!this.doc.serial_no) {
				errors.push(__("Serial number is required"));
			}

			if (!this.doc.brand) {
				errors.push(__("Brand is required"));
			}

			// Format validations
			if (this.doc.serial_no && this.doc.serial_no.length < 3) {
				errors.push(__("Serial number must be at least 3 characters"));
			}

			if (this.doc.year_estimate) {
				const year = parseInt(this.doc.year_estimate);
				const current_year = new Date().getFullYear();
				if (year < 1800 || year > current_year + 1) {
					errors.push(__("Year estimate is out of valid range"));
				}
			}

			if (errors.length > 0) {
				reject(new Error(errors.join('\n')));
			} else {
				resolve();
			}
		});
	},

	setup_help_system() {
		if (this.doctype !== 'Instrument Serial') return;

		// Add placeholder text and help
		if (this.fields_dict.serial_no) {
			this.fields_dict.serial_no.$wrapper.find('input')
				.attr('placeholder', __('e.g., ABC123456, SN-2023-001'));
		}

		if (this.fields_dict.model) {
			this.fields_dict.model.$wrapper.find('input')
				.attr('placeholder', __('e.g., R13, E11, YCL-255'));
		}

		if (this.fields_dict.year_estimate) {
			this.fields_dict.year_estimate.$wrapper.find('input')
				.attr('placeholder', __('e.g., 2020, 1995'));
		}
	},

	create_setup_shortcut() {
		if (this.is_new()) {
			frappe.show_alert(__("Please save the instrument serial number first"), 3);
			return;
		}
		this.create_clarinet_setup_enhanced();
	}
});
