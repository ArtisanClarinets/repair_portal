from datetime import date

import frappe
from frappe.utils import getdate


@frappe.whitelist()
def ops_console_get_sales_orders(
	from_date: str | date | None, to_date: str | date | None, customer: str | None = None
):
	# Ensure from_date and to_date are not None before conversion
	if from_date is not None:
		from_date = getdate(from_date)
	if to_date is not None:
		to_date = getdate(to_date)
	filters = [
		["Sales Order", "transaction_date", ">=", from_date],
		["Sales Order", "transaction_date", "<=", to_date],
	]
	if customer:
		filters.append(["Sales Order", "customer", "=", customer])

	return frappe.get_all(
		"Sales Order",
		fields=["name", "customer", "transaction_date", "grand_total", "currency", "status"],
		filters=filters,
		order_by="transaction_date desc",
		limit=50,
	)


@frappe.whitelist()
def ops_console_make_sales_order(customer: str, item_code: str, qty: float, rate: float | None = None):
	frappe.only_for(["Sales User", "Sales Manager", "System Manager"])
	so = frappe.new_doc("Sales Order")
	so.set("customer", customer)
	so.set("items", [{"item_code": item_code, "qty": qty, **({"rate": rate} if rate else {})}])
	so.flags.ignore_permissions = False  # respect perms
	so.insert()
	so.submit()  # remove this if you want Draft
	return so.name


@frappe.whitelist()
def ops_console_make_todo(subject: str, date: str | None = None):
	td = frappe.new_doc("ToDo")
	td.set("description", subject)
	if date:
		td.set("date", getdate(date))
	td.insert()
	return td.name
