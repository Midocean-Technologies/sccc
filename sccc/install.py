import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

@frappe.whitelist()
def after_install():
    customfield()
    create_role_profile()

def create_role_profile():
    if not frappe.db.exists("Role", "SCCC Admin Team"):
        doc = frappe.new_doc("Role")
        doc.role_name = "SCCC Admin Team"
        doc.insert(ignore_permissions=True)

def customfield():
    if "bench_manager" in frappe.get_installed_apps():
        create_custom_field(  
            "Site",
            {
                "label":_("Customer Onboarding"),
                "fieldname": "customer_onboarding",
                "fieldtype": "Data",
                "insert_after": "disable_website_cache",
                "read_only":1
            }
        )
    