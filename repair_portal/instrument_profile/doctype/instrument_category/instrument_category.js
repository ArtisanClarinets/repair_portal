// Path: repair_portal/instrument_profile/doctype/instrument_category/instrument_category.js
// Date: 2025-10-02
// Version: 2.0.0
// Description: Enhanced client-side controller for Instrument Category with comprehensive error handling, accessibility features, real-time validation, hierarchy management, and improved user experience.
// Dependencies: frappe

frappe.ui.form.on("Instrument Category", {
	onload(frm) {
		// Initialize enhanced UX features
		frm.setup_accessibility();
		frm.setup_keyboard_shortcuts();
		frm.setup_hierarchy_management();
		frm.setup_help_system();
	},

	refresh(frm) {
		try {
			// Set up all UI components with error handling
			frm.setup_action_buttons();
			frm.setup_status_indicators();
			frm.setup_category_hierarchy();
			frm.configure_field_behavior();
			frm.setup_category_filters();
			
		} catch (error) {
			console.error("Error in Instrument Category refresh:", error);
			frappe.msgprint({
				title: __("Form Load Error"),
				message: __("There was an error loading the form. Please refresh the page."),
				indicator: "red"
			});
		}
	},

	category_name(frm) {
		frm.validate_category_name();
		frm.check_category_uniqueness();
	},

	parent_category(frm) {
		frm.handle_parent_category_change();
	},

	is_active(frm) {
		frm.handle_active_status_change();
	},

	category_code(frm) {
		frm.validate_category_code();
	},

	before_save(frm) {
		return new Promise((resolve, reject) => {
			frm.dashboard.show_progress(__("Validating Category"), 50);
			
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
			message: __("Instrument Category saved successfully"),
			indicator: "green"
		});
		frm.update_hierarchy_display();
	}
});

// Enhanced form methods
$.extend(frappe.ui.form.Form.prototype, {
	setup_accessibility() {
		if (this.doctype !== 'Instrument Category') return;
		
		// Add ARIA labels for key fields
		this.wrapper.attr('role', 'form');
		this.wrapper.attr('aria-label', __('Instrument Category Form'));
		
		if (this.fields_dict.category_name) {
			this.fields_dict.category_name.$wrapper.attr('aria-label', __('Enter category name'));
		}
		
		if (this.fields_dict.parent_category) {
			this.fields_dict.parent_category.$wrapper.attr('aria-label', __('Select parent category'));
		}
		
		if (this.fields_dict.category_code) {
			this.fields_dict.category_code.$wrapper.attr('aria-label', __('Enter category code'));
		}
		
		if (this.fields_dict.is_active) {
			this.fields_dict.is_active.$wrapper.attr('aria-label', __('Set category as active'));
		}
	},

	setup_keyboard_shortcuts() {
		if (this.doctype !== 'Instrument Category') return;
		
		$(document).on('keydown', (e) => {
			if (e.ctrlKey && e.key === 's') {
				e.preventDefault();
				this.save();
			}
			
			if (e.ctrlKey && e.shiftKey && e.key === 'H') {
				e.preventDefault();
				this.show_category_hierarchy();
			}
			
			if (e.ctrlKey && e.shiftKey && e.key === 'C') {
				e.preventDefault();
				this.create_child_category();
			}
		});
	},

	setup_action_buttons() {
		if (this.doctype !== 'Instrument Category') return;
		
		// Clear existing custom buttons
		this.custom_buttons = {};
		
		if (this.is_new()) return;
		if (this.__actions_added) return;

		try {
			// View hierarchy button
			this.add_custom_button(
				__("View Hierarchy"),
				() => {
					this.show_category_hierarchy();
				},
				__("View")
			).addClass('btn-info').attr('title', __('View category hierarchy (Ctrl+Shift+H)'));

			// Create child category button
			this.add_custom_button(
				__("Create Child Category"),
				() => {
					this.create_child_category();
				},
				__("Actions")
			).addClass('btn-primary').attr('title', __('Create child category (Ctrl+Shift+C)'));

			// View related instruments button
			this.add_custom_button(
				__("View Instruments"),
				() => {
					this.show_related_instruments();
				},
				__("View")
			);

			// Category usage report button
			this.add_custom_button(
				__("Usage Report"),
				() => {
					this.generate_usage_report();
				},
				__("Reports")
			);

			// Merge categories button (System Manager only)
			if (frappe.user_roles.includes('System Manager')) {
				this.add_custom_button(
					__("Merge Categories"),
					() => {
						this.merge_categories();
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
		if (this.doctype !== 'Instrument Category') return;
		
		// Active status indicator
		if (this.doc.is_active === 0) {
			this.dashboard.add_indicator(
				__('Inactive Category'),
				'red'
			);
		} else {
			this.dashboard.add_indicator(
				__('Active Category'),
				'green'
			);
		}

		// Hierarchy level indicator
		if (this.doc.parent_category) {
			this.dashboard.add_indicator(
				__('Child Category'),
				'blue'
			);
		} else {
			this.dashboard.add_indicator(
				__('Root Category'),
				'orange'
			);
		}

		// Usage count indicator
		this.show_usage_count();
	},

	setup_category_filters() {
		if (this.doctype !== 'Instrument Category') return;

		// Enhanced parent category filter (prevent circular references)
		this.set_query("parent_category", () => {
			const filters = [
				["Instrument Category", "is_active", "=", 1]
			];
			
			// Prevent self-reference and circular dependencies
			if (!this.is_new()) {
				filters.push(["Instrument Category", "name", "!=", this.doc.name]);
			}
			
			return { filters: filters };
		});
	},

	validate_category_name() {
		if (!this.doc.category_name) return;

		const name = this.doc.category_name.trim();
		
		// Basic validation
		if (name.length < 2) {
			this.show_field_error('category_name', 
				__("Category name must be at least 2 characters"));
			return;
		}

		if (name.length > 100) {
			this.show_field_error('category_name', 
				__("Category name is too long (max 100 characters)"));
			return;
		}

		// Check for valid characters
		const valid_pattern = /^[A-Za-z0-9\s\-_&().]+$/;
		if (!valid_pattern.test(name)) {
			this.show_field_error('category_name', 
				__("Category name contains invalid characters"));
			return;
		}

		this.clear_field_error('category_name');
	},

	validate_category_code() {
		if (!this.doc.category_code) return;

		const code = this.doc.category_code.trim().toUpperCase();
		
		// Auto-format code
		this.set_value('category_code', code);

		// Basic validation
		if (code.length < 2) {
			this.show_field_error('category_code', 
				__("Category code must be at least 2 characters"));
			return;
		}

		if (code.length > 10) {
			this.show_field_error('category_code', 
				__("Category code is too long (max 10 characters)"));
			return;
		}

		// Check for valid characters (alphanumeric and hyphens only)
		const valid_pattern = /^[A-Z0-9\-]+$/;
		if (!valid_pattern.test(code)) {
			this.show_field_error('category_code', 
				__("Category code can only contain letters, numbers, and hyphens"));
			return;
		}

		this.clear_field_error('category_code');
	},

	check_category_uniqueness() {
		if (!this.doc.category_name) return;

		// Debounced uniqueness check
		frappe.debounce(() => {
			this.run_uniqueness_check();
		}, 800)();
	},

	run_uniqueness_check() {
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Instrument Category",
				filters: {
					"category_name": this.doc.category_name,
					"name": ["!=", this.doc.name || ""]
				},
				limit: 1
			},
			callback: (r) => {
				if (r.message && r.message.length > 0) {
					this.show_field_warning('category_name', 
						__("Another category with this name already exists"));
				} else {
					this.clear_field_error('category_name');
				}
			},
			error: (r) => {
				console.warn("Uniqueness check failed:", r);
			}
		});
	},

	handle_parent_category_change() {
		if (this.doc.parent_category) {
			// Check for circular dependency
			this.check_circular_dependency();
			
			// Update hierarchy display
			this.update_hierarchy_path();
		} else {
			this.clear_hierarchy_display();
		}
	},

	check_circular_dependency() {
		if (!this.doc.parent_category || this.is_new()) return;

		frappe.call({
			doc: this.doc,
			method: "check_circular_dependency",
			callback: (r) => {
				if (r && r.message && r.message.has_circular) {
					this.show_field_error('parent_category', 
						__("This selection would create a circular dependency"));
					this.set_value('parent_category', '');
				}
			},
			error: (r) => {
				console.error("Circular dependency check failed:", r);
			}
		});
	},

	update_hierarchy_path() {
		if (!this.doc.parent_category) return;

		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Instrument Category",
				name: this.doc.parent_category
			},
			callback: (r) => {
				if (r.message) {
					this.display_hierarchy_path(r.message);
				}
			}
		});
	},

	display_hierarchy_path(parent_category) {
		const path_html = `
			<div class="hierarchy-path">
				<h5>${__("Category Path")}</h5>
				<div class="breadcrumb">
					<span class="breadcrumb-item">${parent_category.category_name}</span>
					<span class="breadcrumb-separator">></span>
					<span class="breadcrumb-item current">${this.doc.category_name || __("This Category")}</span>
				</div>
			</div>
		`;

		this.$wrapper.find('.hierarchy-path').remove();
		this.$wrapper.find('.layout-main-section').first().after(path_html);
	},

	clear_hierarchy_display() {
		this.$wrapper.find('.hierarchy-path').remove();
	},

	handle_active_status_change() {
		if (this.doc.is_active === 0) {
			// Check if category has active child categories or instruments
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
					if (impact.child_categories > 0 || impact.instrument_count > 0) {
						const message = __("Deactivating this category will affect {0} child categories and {1} instruments", 
							[impact.child_categories, impact.instrument_count]);
						this.show_field_warning('is_active', message);
					}
				}
			}
		});
	},

	show_category_hierarchy() {
		const dialog = new frappe.ui.Dialog({
			title: __('Category Hierarchy'),
			size: 'large',
			fields: [
				{
					fieldtype: 'HTML',
					options: '<div id="category-hierarchy-tree"></div>'
				}
			]
		});

		dialog.show();

		// Load hierarchy tree
		frappe.call({
			method: "repair_portal.api.get_category_hierarchy",
			callback: (r) => {
				if (r.message) {
					this.render_hierarchy_tree(r.message, dialog);
				}
			}
		});
	},

	render_hierarchy_tree(hierarchy, dialog) {
		const tree_html = this.build_tree_html(hierarchy);
		dialog.$wrapper.find('#category-hierarchy-tree').html(tree_html);
		
		// Add click handlers for navigation
		dialog.$wrapper.find('.category-node').on('click', (e) => {
			const category_name = $(e.target).data('category');
			if (category_name && category_name !== this.doc.name) {
				frappe.set_route("Form", "Instrument Category", category_name);
				dialog.hide();
			}
		});
	},

	build_tree_html(nodes, level = 0) {
		let html = '';
		nodes.forEach(node => {
			const indent = '&nbsp;'.repeat(level * 4);
			const is_current = node.name === this.doc.name;
			const class_current = is_current ? 'current-category' : '';
			const class_active = node.is_active ? 'active-category' : 'inactive-category';
			
			html += `
				<div class="category-node ${class_current} ${class_active}" data-category="${node.name}">
					${indent}<i class="fa fa-folder"></i> ${node.category_name}
					<span class="badge">${node.instrument_count || 0}</span>
				</div>
			`;
			
			if (node.children && node.children.length > 0) {
				html += this.build_tree_html(node.children, level + 1);
			}
		});
		return html;
	},

	create_child_category() {
		const dialog = new frappe.ui.Dialog({
			title: __('Create Child Category'),
			fields: [
				{
					fieldname: 'category_name',
					label: __('Category Name'),
					fieldtype: 'Data',
					reqd: 1
				},
				{
					fieldname: 'category_code',
					label: __('Category Code'),
					fieldtype: 'Data',
					description: __('Short code for the category')
				},
				{
					fieldname: 'description',
					label: __('Description'),
					fieldtype: 'Text'
				}
			],
			primary_action_label: __('Create Category'),
			primary_action: (values) => {
				this.execute_child_creation(values);
				dialog.hide();
			}
		});
		
		dialog.show();
	},

	execute_child_creation(values) {
		const new_doc = frappe.model.get_new_doc("Instrument Category");
		new_doc.category_name = values.category_name;
		new_doc.category_code = values.category_code;
		new_doc.description = values.description;
		new_doc.parent_category = this.doc.name;
		new_doc.is_active = 1;

		frappe.set_route("Form", "Instrument Category", new_doc.name);
	},

	show_usage_count() {
		frappe.call({
			doc: this.doc,
			method: "get_usage_statistics",
			callback: (r) => {
				if (r && r.message) {
					const stats = r.message;
					this.dashboard.add_indicator(
						__('Instruments: {0}', [stats.instrument_count]),
						'blue'
					);
					
					if (stats.child_count > 0) {
						this.dashboard.add_indicator(
							__('Child Categories: {0}', [stats.child_count]),
							'purple'
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
			if (!this.doc.category_name) {
				errors.push(__("Category name is required"));
			}

			// Format validation
			if (this.doc.category_name && this.doc.category_name.trim().length < 2) {
				errors.push(__("Category name must be at least 2 characters"));
			}

			if (this.doc.category_code) {
				const code = this.doc.category_code.trim();
				if (code.length < 2) {
					errors.push(__("Category code must be at least 2 characters"));
				}
				
				const valid_pattern = /^[A-Z0-9\-]+$/;
				if (!valid_pattern.test(code)) {
					errors.push(__("Category code contains invalid characters"));
				}
			}

			// Business logic validation
			if (this.doc.parent_category === this.doc.name) {
				errors.push(__("Category cannot be its own parent"));
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

	show_related_instruments() {
		frappe.route_options = {
			"category": this.doc.name
		};
		frappe.set_route("List", "Instrument Profile");
	},

	generate_usage_report() {
		frappe.set_route("query-report", "Category Usage Report", {
			"category": this.doc.name
		});
	},

	merge_categories() {
		if (!frappe.user_roles.includes('System Manager')) {
			frappe.msgprint({
				title: __("Access Denied"),
				message: __("You don't have permission to merge categories"),
				indicator: "red"
			});
			return;
		}

		const dialog = new frappe.ui.Dialog({
			title: __('Merge Categories'),
			fields: [
				{
					fieldname: 'target_category',
					label: __('Merge Into Category'),
					fieldtype: 'Link',
					options: 'Instrument Category',
					reqd: 1,
					get_query: () => {
						return {
							filters: [
								["Instrument Category", "name", "!=", this.doc.name],
								["Instrument Category", "is_active", "=", 1]
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
			primary_action_label: __('Merge Categories'),
			primary_action: (values) => {
				if (values.merge_confirmation !== 'MERGE') {
					frappe.msgprint(__("Please type 'MERGE' to confirm"));
					return;
				}
				this.execute_category_merge(values.target_category);
				dialog.hide();
			}
		});
		
		dialog.show();
	},

	execute_category_merge(target_category) {
		frappe.call({
			doc: this.doc,
			method: "merge_into_category",
			args: {
				target_category: target_category
			},
			callback: (r) => {
				if (r && r.message) {
					frappe.show_alert({
						message: __("Categories merged successfully"),
						indicator: "green"
					});
					frappe.set_route("Form", "Instrument Category", target_category);
				}
			},
			error: (r) => {
				frappe.msgprint({
					title: __("Merge Failed"),
					message: r.message || __("Failed to merge categories"),
					indicator: "red"
				});
			}
		});
	},

	setup_help_system() {
		if (this.doctype !== 'Instrument Category') return;

		// Add placeholder text and help
		if (this.fields_dict.category_name) {
			this.fields_dict.category_name.$wrapper.find('input')
				.attr('placeholder', __('e.g., Clarinets, Brass Instruments, Woodwinds'));
		}

		if (this.fields_dict.category_code) {
			this.fields_dict.category_code.$wrapper.find('input')
				.attr('placeholder', __('e.g., CLR, BRASS, WOOD'));
		}
	},

	update_hierarchy_display() {
		// Update hierarchy display after save
		setTimeout(() => {
			if (this.doc.parent_category) {
				this.update_hierarchy_path();
			}
		}, 1000);
	}
});
