// Path: repair_portal/instrument_profile/doctype/customer_external_work_log/customer_external_work_log.js
// Date: 2025-10-02
// Version: 2.0.0
// Description: Enhanced client-side controller for Customer External Work Log with comprehensive error handling, accessibility features, real-time validation, cost calculations, and improved user experience.
// Dependencies: frappe

frappe.ui.form.on("Customer External Work Log", {
	onload(frm) {
		// Initialize enhanced UX features
		frm.setup_accessibility();
		frm.setup_keyboard_shortcuts();
		frm.setup_cost_calculation();
		frm.setup_help_system();
	},

	refresh(frm) {
		try {
			// Set up all UI components with error handling
			frm.setup_action_buttons();
			frm.setup_status_indicators();
			frm.setup_cost_summary();
			frm.configure_field_behavior();
			frm.setup_date_validation();
			
		} catch (error) {
			console.error("Error in Customer External Work Log refresh:", error);
			frappe.msgprint({
				title: __("Form Load Error"),
				message: __("There was an error loading the form. Please refresh the page."),
				indicator: "red"
			});
		}
	},

	customer(frm) {
		frm.handle_customer_change();
	},

	instrument_profile(frm) {
		frm.handle_instrument_change();
	},

	work_date(frm) {
		frm.validate_work_date();
	},

	estimated_cost(frm) {
		frm.validate_cost_field('estimated_cost');
		frm.calculate_cost_variance();
	},

	actual_cost(frm) {
		frm.validate_cost_field('actual_cost');
		frm.calculate_cost_variance();
	},

	work_description(frm) {
		frm.validate_work_description();
	},

	external_provider(frm) {
		frm.handle_provider_change();
	},

	before_save(frm) {
		return new Promise((resolve, reject) => {
			frm.dashboard.show_progress(__("Validating Work Log"), 50);
			
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
			message: __("External Work Log saved successfully"),
			indicator: "green"
		});
		frm.update_cost_summary();
	}
});

// Enhanced form methods
$.extend(frappe.ui.form.Form.prototype, {
	setup_accessibility() {
		if (this.doctype !== 'Customer External Work Log') return;
		
		// Add ARIA labels for key fields
		this.wrapper.attr('role', 'form');
		this.wrapper.attr('aria-label', __('Customer External Work Log Form'));
		
		if (this.fields_dict.customer) {
			this.fields_dict.customer.$wrapper.attr('aria-label', __('Select customer'));
		}
		
		if (this.fields_dict.instrument_profile) {
			this.fields_dict.instrument_profile.$wrapper.attr('aria-label', __('Select instrument profile'));
		}
		
		if (this.fields_dict.work_date) {
			this.fields_dict.work_date.$wrapper.attr('aria-label', __('Select work date'));
		}
		
		if (this.fields_dict.estimated_cost) {
			this.fields_dict.estimated_cost.$wrapper.attr('aria-label', __('Enter estimated cost'));
		}
		
		if (this.fields_dict.actual_cost) {
			this.fields_dict.actual_cost.$wrapper.attr('aria-label', __('Enter actual cost'));
		}
	},

	setup_keyboard_shortcuts() {
		if (this.doctype !== 'Customer External Work Log') return;
		
		$(document).on('keydown', (e) => {
			if (e.ctrlKey && e.key === 's') {
				e.preventDefault();
				this.save();
			}
			
			if (e.ctrlKey && e.shiftKey && e.key === 'C') {
				e.preventDefault();
				this.calculate_costs();
			}
		});
	},

	setup_action_buttons() {
		if (this.doctype !== 'Customer External Work Log') return;
		
		// Clear existing custom buttons
		this.custom_buttons = {};
		
		if (this.is_new()) return;
		if (this.__actions_added) return;

		try {
			// Cost calculation button
			this.add_custom_button(
				__("Calculate Costs"),
				() => {
					this.calculate_costs();
				},
				__("Tools")
			).addClass('btn-primary').attr('title', __('Calculate cost estimates (Ctrl+Shift+C)'));

			// View related work button
			this.add_custom_button(
				__("View Related Work"),
				() => {
					this.show_related_work();
				},
				__("View")
			);

			// Generate work summary button
			this.add_custom_button(
				__("Work Summary"),
				() => {
					this.generate_work_summary();
				},
				__("Reports")
			);

			// Copy work log button
			this.add_custom_button(
				__("Copy Work Log"),
				() => {
					this.copy_work_log();
				},
				__("Actions")
			);

			this.__actions_added = true;

		} catch (error) {
			console.error("Error setting up action buttons:", error);
		}
	},

	setup_status_indicators() {
		if (this.doctype !== 'Customer External Work Log') return;
		
		// Cost variance indicator
		if (this.doc.estimated_cost && this.doc.actual_cost) {
			const variance = this.calculate_cost_variance_percentage();
			const color = Math.abs(variance) > 20 ? 'red' : Math.abs(variance) > 10 ? 'orange' : 'green';
			
			this.dashboard.add_indicator(
				__('Cost Variance: {0}%', [variance.toFixed(1)]),
				color
			);
		}

		// Work date indicator
		if (this.doc.work_date) {
			const work_date = moment(this.doc.work_date);
			const days_ago = moment().diff(work_date, 'days');
			
			if (days_ago > 30) {
				this.dashboard.add_indicator(
					__('Work Date: {0} days ago', [days_ago]),
					'orange'
				);
			}
		}

		// Provider reliability indicator
		if (this.doc.external_provider) {
			this.show_provider_reliability();
		}
	},

	setup_cost_summary() {
		if (this.doctype !== 'Customer External Work Log') return;
		
		// Add cost summary section
		const cost_html = `
			<div class="cost-summary">
				<h5>${__("Cost Summary")}</h5>
				<div class="row">
					<div class="col-md-4">
						<div class="cost-item">
							<label>${__("Estimated Cost")}</label>
							<div class="cost-value">${this.format_currency(this.doc.estimated_cost || 0)}</div>
						</div>
					</div>
					<div class="col-md-4">
						<div class="cost-item">
							<label>${__("Actual Cost")}</label>
							<div class="cost-value">${this.format_currency(this.doc.actual_cost || 0)}</div>
						</div>
					</div>
					<div class="col-md-4">
						<div class="cost-item">
							<label>${__("Variance")}</label>
							<div class="cost-value variance-${this.get_variance_class()}">
								${this.format_currency(this.calculate_cost_variance_amount())}
							</div>
						</div>
					</div>
				</div>
			</div>
		`;

		// Add to form
		this.$wrapper.find('.cost-summary').remove();
		if (this.doc.estimated_cost || this.doc.actual_cost) {
			this.$wrapper.find('.layout-main-section').first().after(cost_html);
		}
	},

	format_currency(amount) {
		return frappe.format(amount, {fieldtype: 'Currency'});
	},

	calculate_cost_variance_amount() {
		if (!this.doc.estimated_cost || !this.doc.actual_cost) return 0;
		return this.doc.actual_cost - this.doc.estimated_cost;
	},

	calculate_cost_variance_percentage() {
		if (!this.doc.estimated_cost || !this.doc.actual_cost) return 0;
		const variance = this.doc.actual_cost - this.doc.estimated_cost;
		return (variance / this.doc.estimated_cost) * 100;
	},

	get_variance_class() {
		const variance = this.calculate_cost_variance_percentage();
		if (Math.abs(variance) <= 5) return 'good';
		if (Math.abs(variance) <= 15) return 'moderate';
		return 'high';
	},

	handle_customer_change() {
		if (!this.doc.customer) {
			this.set_value("instrument_profile", "");
			return;
		}

		// Show loading indicator
		this.show_field_loading('instrument_profile', true);
		
		// Update instrument profile filter
		this.fields_dict.instrument_profile.get_query = () => {
			return {
				filters: [
					["Instrument Profile", "customer", "=", this.doc.customer],
					["Instrument Profile", "workflow_state", "!=", "Archived"]
				]
			};
		};

		this.fields_dict.instrument_profile.refresh();
		this.show_field_loading('instrument_profile', false);

		// Show helpful message
		this.show_field_info('customer', 
			__("Instrument profiles will be filtered for this customer"));
	},

	handle_instrument_change() {
		if (!this.doc.instrument_profile) return;

		// Fetch instrument details for context
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Instrument Profile",
				name: this.doc.instrument_profile
			},
			callback: (r) => {
				if (r.message) {
					this.display_instrument_info(r.message);
				}
			},
			error: (r) => {
				console.error("Error fetching instrument profile:", r);
			}
		});
	},

	display_instrument_info(profile) {
		const info_html = `
			<div class="instrument-info">
				<h5>${__("Instrument Information")}</h5>
				<div class="row">
					<div class="col-md-6">
						<strong>${__("Serial Number")}:</strong> ${profile.serial_number || __("Not set")}
					</div>
					<div class="col-md-6">
						<strong>${__("Model")}:</strong> ${profile.model || __("Not specified")}
					</div>
				</div>
			</div>
		`;

		// Add to form
		this.$wrapper.find('.instrument-info').remove();
		this.$wrapper.find('.layout-main-section').first().after(info_html);
	},

	validate_work_date() {
		if (!this.doc.work_date) return;

		const work_date = moment(this.doc.work_date);
		const today = moment();
		
		// Check if date is in the future
		if (work_date.isAfter(today)) {
			this.show_field_warning('work_date', 
				__("Work date is in the future"));
		}
		
		// Check if date is too far in the past
		const months_ago = today.diff(work_date, 'months');
		if (months_ago > 12) {
			this.show_field_warning('work_date', 
				__("Work date is more than a year ago"));
		} else {
			this.clear_field_error('work_date');
		}
	},

	validate_cost_field(fieldname) {
		const value = this.doc[fieldname];
		if (!value) return;

		if (value < 0) {
			this.show_field_error(fieldname, 
				__("Cost cannot be negative"));
			return;
		}

		if (value > 10000) {
			this.show_field_warning(fieldname, 
				__("Cost seems unusually high - please verify"));
		} else {
			this.clear_field_error(fieldname);
		}
	},

	validate_work_description() {
		if (!this.doc.work_description) return;

		const description = this.doc.work_description.trim();
		
		if (description.length < 10) {
			this.show_field_warning('work_description', 
				__("Work description should be more detailed"));
		} else if (description.length > 1000) {
			this.show_field_warning('work_description', 
				__("Work description is very long - consider summarizing"));
		} else {
			this.clear_field_error('work_description');
		}
	},

	handle_provider_change() {
		if (!this.doc.external_provider) return;

		// Check provider history and reliability
		this.check_provider_history();
	},

	check_provider_history() {
		frappe.call({
			method: "repair_portal.api.get_provider_history",
			args: {
				provider: this.doc.external_provider
			},
			callback: (r) => {
				if (r.message) {
					this.display_provider_info(r.message);
				}
			},
			error: (r) => {
				console.warn("Provider history check failed:", r);
			}
		});
	},

	display_provider_info(provider_data) {
		if (provider_data.work_count > 0) {
			const avg_variance = provider_data.avg_cost_variance || 0;
			const variance_text = avg_variance > 10 ? 
				__("typically over budget") : 
				avg_variance < -10 ? 
				__("typically under budget") : 
				__("usually on budget");

			this.show_field_info('external_provider', 
				__("Provider has completed {0} jobs, {1}", [provider_data.work_count, variance_text]));
		}
	},

	calculate_costs() {
		if (!this.doc.work_description) {
			frappe.msgprint({
				title: __("Missing Information"),
				message: __("Please add work description first"),
				indicator: "orange"
			});
			return;
		}

		const progress = frappe.show_progress(
			__("Calculating Costs"),
			50,
			100,
			__("Analyzing work requirements...")
		);

		frappe.call({
			doc: this.doc,
			method: "calculate_estimated_costs",
			callback: (r) => {
				progress.hide();
				
				if (r && r.message) {
					this.set_value("estimated_cost", r.message.estimated_cost);
					
					frappe.show_alert({
						message: __("Cost estimate calculated: {0}", [this.format_currency(r.message.estimated_cost)]),
						indicator: "green"
					});
				}
			},
			error: (r) => {
				progress.hide();
				console.error("Cost calculation failed:", r);
				
				frappe.msgprint({
					title: __("Calculation Failed"),
					message: r.message || __("Unable to calculate costs"),
					indicator: "red"
				});
			}
		});
	},

	validate_all_fields() {
		return new Promise((resolve, reject) => {
			const errors = [];

			// Required field validation
			if (!this.doc.customer) {
				errors.push(__("Customer is required"));
			}

			if (!this.doc.instrument_profile) {
				errors.push(__("Instrument Profile is required"));
			}

			if (!this.doc.work_date) {
				errors.push(__("Work date is required"));
			}

			if (!this.doc.work_description) {
				errors.push(__("Work description is required"));
			}

			if (!this.doc.external_provider) {
				errors.push(__("External provider is required"));
			}

			// Business validation
			if (this.doc.estimated_cost && this.doc.estimated_cost < 0) {
				errors.push(__("Estimated cost cannot be negative"));
			}

			if (this.doc.actual_cost && this.doc.actual_cost < 0) {
				errors.push(__("Actual cost cannot be negative"));
			}

			if (this.doc.work_description && this.doc.work_description.trim().length < 10) {
				errors.push(__("Work description must be at least 10 characters"));
			}

			if (errors.length > 0) {
				reject(new Error(errors.join('\n')));
			} else {
				resolve();
			}
		});
	},

	show_field_loading(fieldname, show) {
		const field = this.fields_dict[fieldname];
		if (field) {
			if (show) {
				field.$wrapper.find('.control-input').append('<i class="fa fa-spinner fa-spin text-muted"></i>');
			} else {
				field.$wrapper.find('.fa-spinner').remove();
			}
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

	show_related_work() {
		frappe.route_options = {
			"customer": this.doc.customer,
			"instrument_profile": this.doc.instrument_profile
		};
		frappe.set_route("List", "Customer External Work Log");
	},

	generate_work_summary() {
		frappe.set_route("query-report", "External Work Summary", {
			"customer": this.doc.customer
		});
	},

	copy_work_log() {
		const new_doc = frappe.model.copy_doc(this.doc);
		new_doc.work_date = frappe.datetime.get_today();
		new_doc.actual_cost = 0;
		
		frappe.set_route("Form", this.doctype, new_doc.name);
	},

	setup_help_system() {
		if (this.doctype !== 'Customer External Work Log') return;

		// Add placeholder text and help
		if (this.fields_dict.work_description) {
			this.fields_dict.work_description.$wrapper.find('textarea')
				.attr('placeholder', __('Describe the work performed, parts used, and any special considerations...'));
		}

		if (this.fields_dict.estimated_cost) {
			this.fields_dict.estimated_cost.$wrapper.find('input')
				.attr('placeholder', __('0.00'));
		}

		if (this.fields_dict.actual_cost) {
			this.fields_dict.actual_cost.$wrapper.find('input')
				.attr('placeholder', __('0.00'));
		}
	},

	update_cost_summary() {
		// Update cost summary after save
		setTimeout(() => {
			this.setup_cost_summary();
		}, 1000);
	}
});
