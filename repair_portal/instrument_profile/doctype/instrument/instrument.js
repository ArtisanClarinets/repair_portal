// Path: repair_portal/instrument_profile/doctype/instrument/instrument.js
// Date: 2025-10-02
// Version: 2.0.0
// Description: Enhanced client-side controller for Instrument master data with comprehensive error handling, accessibility features, real-time validation, and improved user experience.
// Dependencies: frappe

frappe.ui.form.on("Instrument", {
	onload(frm) {
		// Initialize enhanced UX features
		frm.setup_accessibility();
		frm.setup_keyboard_shortcuts();
		frm.setup_brand_model_integration();
		frm.setup_help_system();
	},

	refresh(frm) {
		try {
			// Set up all UI components with error handling
			frm.setup_action_buttons();
			frm.setup_status_indicators();
			frm.configure_field_behavior();
			frm.setup_filters();
			frm.display_instrument_metrics();
			
		} catch (error) {
			console.error("Error in Instrument refresh:", error);
			frappe.msgprint({
				title: __("Form Load Error"),
				message: __("There was an error loading the form. Please refresh the page."),
				indicator: "red"
			});
		}
	},

	instrument_name(frm) {
		frm.validate_instrument_name();
		frm.check_name_uniqueness();
	},

	brand(frm) {
		frm.handle_brand_change();
	},

	category(frm) {
		frm.handle_category_change();
	},

	model_code(frm) {
		frm.validate_model_code();
	},

	is_active(frm) {
		frm.handle_active_status_change();
	},

	default_setup_template(frm) {
		frm.validate_setup_template();
	},

	before_save(frm) {
		return new Promise((resolve, reject) => {
			frm.dashboard.show_progress(__("Validating Instrument"), 50);
			
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
			message: __("Instrument saved successfully"),
			indicator: "green"
		});
		frm.refresh_metrics();
	}
});

// Enhanced form methods
$.extend(frappe.ui.form.Form.prototype, {
	setup_accessibility() {
		if (this.doctype !== 'Instrument') return;
		
		// Add ARIA labels for key fields
		this.wrapper.attr('role', 'form');
		this.wrapper.attr('aria-label', __('Instrument Master Form'));
		
		if (this.fields_dict.instrument_name) {
			this.fields_dict.instrument_name.$wrapper.attr('aria-label', __('Enter instrument name'));
		}
		
		if (this.fields_dict.brand) {
			this.fields_dict.brand.$wrapper.attr('aria-label', __('Select instrument brand'));
		}
		
		if (this.fields_dict.category) {
			this.fields_dict.category.$wrapper.attr('aria-label', __('Select instrument category'));
		}
		
		if (this.fields_dict.model_code) {
			this.fields_dict.model_code.$wrapper.attr('aria-label', __('Enter model code'));
		}
	},

	setup_keyboard_shortcuts() {
		if (this.doctype !== 'Instrument') return;
		
		$(document).on('keydown', (e) => {
			if (e.ctrlKey && e.key === 's') {
				e.preventDefault();
				this.save();
			}
			
			if (e.ctrlKey && e.shiftKey && e.key === 'P') {
				e.preventDefault();
				this.show_instrument_profiles();
			}
			
			if (e.ctrlKey && e.shiftKey && e.key === 'M') {
				e.preventDefault();
				this.show_models();
			}
			
			if (e.ctrlKey && e.shiftKey && e.key === 'T') {
				e.preventDefault();
				this.show_setup_templates();
			}
		});
	},

	setup_action_buttons() {
		if (this.doctype !== 'Instrument') return;
		
		// Clear existing custom buttons
		this.custom_buttons = {};
		
		if (this.is_new()) return;
		if (this.__actions_added) return;

		try {
			// View instrument profiles button
			this.add_custom_button(
				__("View Profiles"),
				() => {
					this.show_instrument_profiles();
				},
				__("View")
			).addClass('btn-info').attr('title', __('View instrument profiles (Ctrl+Shift+P)'));

			// View models button
			this.add_custom_button(
				__("View Models"),
				() => {
					this.show_models();
				},
				__("View")
			).addClass('btn-info').attr('title', __('View instrument models (Ctrl+Shift+M)'));

			// View setup templates button
			this.add_custom_button(
				__("Setup Templates"),
				() => {
					this.show_setup_templates();
				},
				__("View")
			).addClass('btn-info').attr('title', __('View setup templates (Ctrl+Shift+T)'));

			// Create model button
			this.add_custom_button(
				__("Create Model"),
				() => {
					this.create_new_model();
				},
				__("Actions")
			).addClass('btn-primary');

			// Usage statistics button
			this.add_custom_button(
				__("Usage Statistics"),
				() => {
					this.show_usage_statistics();
				},
				__("Reports")
			);

			// Merge instruments button (System Manager only)
			if (frappe.user_roles.includes('System Manager')) {
				this.add_custom_button(
					__("Merge Instruments"),
					() => {
						this.merge_instruments();
					},
					__("Tools")
				);
			}

			this.__actions_added = true;

		} catch (error) {
			console.error("Error setting up action buttons:", error);
		}
	},

	setup_status_indicators() {
		if (this.doctype !== 'Instrument') return;
		
		// Active status indicator
		if (this.doc.is_active === 0) {
			this.dashboard.add_indicator(
				__('Inactive Instrument'),
				'red'
			);
		} else {
			this.dashboard.add_indicator(
				__('Active Instrument'),
				'green'
			);
		}

		// Category indicator
		if (this.doc.category) {
			this.dashboard.add_indicator(
				__('Category: {0}', [this.doc.category]),
				'blue'
			);
		}

		// Brand indicator
		if (this.doc.brand) {
			this.dashboard.add_indicator(
				__('Brand: {0}', [this.doc.brand]),
				'purple'
			);
		}

		// Usage metrics indicator
		this.show_usage_metrics();
	},

	setup_filters() {
		if (this.doctype !== 'Instrument') return;

		// Enhanced brand filter (active brands only)
		this.set_query("brand", () => {
			return {
				filters: [
					["Brand", "is_active", "=", 1]
				]
			};
		});

		// Enhanced category filter (active categories only)
		this.set_query("category", () => {
			return {
				filters: [
					["Instrument Category", "is_active", "=", 1]
				]
			};
		});

		// Setup template filter (category-specific)
		this.set_query("default_setup_template", () => {
			const filters = [
				["Setup Template", "is_active", "=", 1]
			];
			
			if (this.doc.category) {
				filters.push(["Setup Template", "instrument_category", "=", this.doc.category]);
			}
			
			return { filters: filters };
		});
	},

	validate_instrument_name() {
		if (!this.doc.instrument_name) return;

		const name = this.doc.instrument_name.trim();
		
		// Basic validation
		if (name.length < 2) {
			this.show_field_error('instrument_name', 
				__("Instrument name must be at least 2 characters"));
			return;
		}

		if (name.length > 150) {
			this.show_field_error('instrument_name', 
				__("Instrument name is too long (max 150 characters)"));
			return;
		}

		// Check for valid characters
		const valid_pattern = /^[A-Za-z0-9\s\-_&().]+$/;
		if (!valid_pattern.test(name)) {
			this.show_field_error('instrument_name', 
				__("Instrument name contains invalid characters"));
			return;
		}

		this.clear_field_error('instrument_name');
	},

	validate_model_code() {
		if (!this.doc.model_code) return;

		const code = this.doc.model_code.trim().toUpperCase();
		
		// Auto-format code
		this.set_value('model_code', code);

		// Basic validation
		if (code.length < 1) {
			this.show_field_error('model_code', 
				__("Model code cannot be empty"));
			return;
		}

		if (code.length > 20) {
			this.show_field_error('model_code', 
				__("Model code is too long (max 20 characters)"));
			return;
		}

		// Check for valid characters
		const valid_pattern = /^[A-Z0-9\-_]+$/;
		if (!valid_pattern.test(code)) {
			this.show_field_error('model_code', 
				__("Model code can only contain letters, numbers, hyphens, and underscores"));
			return;
		}

		this.clear_field_error('model_code');
	},

	check_name_uniqueness() {
		if (!this.doc.instrument_name) return;

		// Debounced uniqueness check
		frappe.debounce(() => {
			this.run_name_uniqueness_check();
		}, 800)();
	},

	run_name_uniqueness_check() {
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Instrument",
				filters: {
					"instrument_name": this.doc.instrument_name,
					"name": ["!=", this.doc.name || ""]
				},
				limit: 1
			},
			callback: (r) => {
				if (r.message && r.message.length > 0) {
					this.show_field_warning('instrument_name', 
						__("Another instrument with this name already exists"));
				} else {
					this.clear_field_error('instrument_name');
				}
			},
			error: (r) => {
				console.warn("Uniqueness check failed:", r);
			}
		});
	},

	handle_brand_change() {
		if (this.doc.brand) {
			// Load brand-specific information
			this.load_brand_info();
			
			// Update model code suggestions
			this.suggest_model_codes();
		}
	},

	load_brand_info() {
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Brand",
				name: this.doc.brand
			},
			callback: (r) => {
				if (r.message) {
					this.display_brand_info(r.message);
				}
			}
		});
	},

	display_brand_info(brand) {
		if (brand.description) {
			this.show_field_info('brand', 
				__("Brand Info: {0}", [brand.description]));
		}
	},

	suggest_model_codes() {
		frappe.call({
			method: "repair_portal.instrument_profile.api.get_suggested_model_codes",
			args: {
				brand: this.doc.brand,
				category: this.doc.category
			},
			callback: (r) => {
				if (r.message && r.message.length > 0) {
					this.show_model_suggestions(r.message);
				}
			}
		});
	},

	show_model_suggestions(suggestions) {
		const suggestion_html = suggestions.slice(0, 5).map(code => 
			`<span class="label label-info model-suggestion" data-code="${code}">${code}</span>`
		).join(' ');
		
		this.show_field_info('model_code', 
			__("Suggested codes: {0}", [suggestion_html]));
		
		// Add click handlers for suggestions
		this.$wrapper.find('.model-suggestion').on('click', (e) => {
			const code = $(e.target).data('code');
			this.set_value('model_code', code);
		});
	},

	handle_category_change() {
		if (this.doc.category) {
			// Update setup template options
			this.refresh_setup_templates();
			
			// Load category-specific validation rules
			this.load_category_rules();
		}
	},

	refresh_setup_templates() {
		if (this.fields_dict.default_setup_template) {
			this.fields_dict.default_setup_template.df.get_query = () => {
				return {
					filters: [
						["Setup Template", "is_active", "=", 1],
						["Setup Template", "instrument_category", "=", this.doc.category]
					]
				};
			};
			this.fields_dict.default_setup_template.refresh();
		}
	},

	load_category_rules() {
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Instrument Category",
				name: this.doc.category
			},
			callback: (r) => {
				if (r.message) {
					this.apply_category_rules(r.message);
				}
			}
		});
	},

	apply_category_rules(category) {
		// Apply category-specific validation or field behavior
		if (category.description) {
			this.show_field_info('category', 
				__("Category Info: {0}", [category.description]));
		}
	},

	handle_active_status_change() {
		if (this.doc.is_active === 0) {
			// Check if instrument has active profiles or models
			this.check_deactivation_impact();
		}
	},

	check_deactivation_impact() {
		frappe.call({
			doc: this.doc,
			method: "check_deactivation_impact",
			callback: (r) => {
				if (r && r.message) {
					const impact = r.message;
					if (impact.profile_count > 0 || impact.model_count > 0) {
						const message = __("Deactivating this instrument will affect {0} profiles and {1} models", 
							[impact.profile_count, impact.model_count]);
						this.show_field_warning('is_active', message);
					}
				}
			}
		});
	},

	validate_setup_template() {
		if (!this.doc.default_setup_template) return;

		// Validate template compatibility with category
		if (this.doc.category) {
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Setup Template",
					name: this.doc.default_setup_template
				},
				callback: (r) => {
					if (r.message) {
						if (r.message.instrument_category !== this.doc.category) {
							this.show_field_error('default_setup_template', 
								__("This template is not compatible with the selected category"));
						} else {
							this.clear_field_error('default_setup_template');
						}
					}
				}
			});
		}
	},

	show_usage_metrics() {
		frappe.call({
			doc: this.doc,
			method: "get_usage_statistics",
			callback: (r) => {
				if (r && r.message) {
					const stats = r.message;
					
					if (stats.profile_count > 0) {
						this.dashboard.add_indicator(
							__('Profiles: {0}', [stats.profile_count]),
							'blue'
						);
					}
					
					if (stats.model_count > 0) {
						this.dashboard.add_indicator(
							__('Models: {0}', [stats.model_count]),
							'purple'
						);
					}
					
					if (stats.template_count > 0) {
						this.dashboard.add_indicator(
							__('Templates: {0}', [stats.template_count]),
							'orange'
						);
					}
				}
			}
		});
	},

	validate_all_fields() {
		return new Promise((resolve, reject) => {
			const errors = [];

			// Required field validation
			if (!this.doc.instrument_name) {
				errors.push(__("Instrument name is required"));
			}

			if (!this.doc.brand) {
				errors.push(__("Brand is required"));
			}

			if (!this.doc.category) {
				errors.push(__("Category is required"));
			}

			// Format validation
			if (this.doc.instrument_name && this.doc.instrument_name.trim().length < 2) {
				errors.push(__("Instrument name must be at least 2 characters"));
			}

			if (this.doc.model_code) {
				const code = this.doc.model_code.trim();
				if (code.length === 0) {
					errors.push(__("Model code cannot be empty"));
				}
				
				const valid_pattern = /^[A-Z0-9\-_]+$/;
				if (!valid_pattern.test(code)) {
					errors.push(__("Model code contains invalid characters"));
				}
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

	show_instrument_profiles() {
		frappe.route_options = {
			"instrument": this.doc.name
		};
		frappe.set_route("List", "Instrument Profile");
	},

	show_models() {
		frappe.route_options = {
			"instrument": this.doc.name
		};
		frappe.set_route("List", "Instrument Model");
	},

	show_setup_templates() {
		frappe.route_options = {
			"instrument_category": this.doc.category
		};
		frappe.set_route("List", "Setup Template");
	},

	create_new_model() {
		const new_doc = frappe.model.get_new_doc("Instrument Model");
		new_doc.instrument = this.doc.name;
		new_doc.brand = this.doc.brand;
		new_doc.category = this.doc.category;
		
		if (this.doc.model_code) {
			new_doc.model_name = this.doc.model_code;
		}

		frappe.set_route("Form", "Instrument Model", new_doc.name);
	},

	show_usage_statistics() {
		frappe.set_route("query-report", "Instrument Usage Report", {
			"instrument": this.doc.name
		});
	},

	merge_instruments() {
		if (!frappe.user_roles.includes('System Manager')) {
			frappe.msgprint({
				title: __("Access Denied"),
				message: __("You don't have permission to merge instruments"),
				indicator: "red"
			});
			return;
		}

		const dialog = new frappe.ui.Dialog({
			title: __('Merge Instruments'),
			fields: [
				{
					fieldname: 'target_instrument',
					label: __('Merge Into Instrument'),
					fieldtype: 'Link',
					options: 'Instrument',
					reqd: 1,
					get_query: () => {
						return {
							filters: [
								["Instrument", "name", "!=", this.doc.name],
								["Instrument", "is_active", "=", 1]
							]
						};
					}
				},
				{
					fieldname: 'merge_confirmation',
					label: __('Confirmation'),
					fieldtype: 'Data',
					description: __('Type "MERGE" to confirm this action'),
					reqd: 1
				}
			],
			primary_action_label: __('Merge Instruments'),
			primary_action: (values) => {
				if (values.merge_confirmation !== 'MERGE') {
					frappe.msgprint(__("Please type 'MERGE' to confirm"));
					return;
				}
				this.execute_instrument_merge(values.target_instrument);
				dialog.hide();
			}
		});
		
		dialog.show();
	},

	execute_instrument_merge(target_instrument) {
		frappe.call({
			doc: this.doc,
			method: "merge_into_instrument",
			args: {
				target_instrument: target_instrument
			},
			callback: (r) => {
				if (r && r.message) {
					frappe.show_alert({
						message: __("Instruments merged successfully"),
						indicator: "green"
					});
					frappe.set_route("Form", "Instrument", target_instrument);
				}
			},
			error: (r) => {
				frappe.msgprint({
					title: __("Merge Failed"),
					message: r.message || __("Failed to merge instruments"),
					indicator: "red"
				});
			}
		});
	},

	display_instrument_metrics() {
		if (this.is_new()) return;

		// Display comprehensive instrument metrics
		this.show_usage_metrics();
	},

	setup_help_system() {
		if (this.doctype !== 'Instrument') return;

		// Add placeholder text and help
		if (this.fields_dict.instrument_name) {
			this.fields_dict.instrument_name.$wrapper.find('input')
				.attr('placeholder', __('e.g., Student Clarinet, Professional Saxophone'));
		}

		if (this.fields_dict.model_code) {
			this.fields_dict.model_code.$wrapper.find('input')
				.attr('placeholder', __('e.g., R13, YAS-62'));
		}
	},

	setup_brand_model_integration() {
		if (this.doctype !== 'Instrument') return;

		// Enhanced integration between brand and model selection
		this.setup_cascading_updates();
	},

	setup_cascading_updates() {
		// Set up cascading updates for brand/category changes
		// This will be triggered by the field change handlers
	},

	refresh_metrics() {
		// Refresh metrics after save
		setTimeout(() => {
			this.show_usage_metrics();
		}, 1000);
	}
});
