import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

@frappe.whitelist()
def after_install():
    customfield()
    create_role_profile()

def create_role_profile():
    if not frappe.db.exists("Role Profile", "Individual"):
        doc = frappe.get_doc({
            "doctype": "Role Profile",
            "role_profile": "Individual",
            "roles": [
                {"role": "Sales User"},
                {"role": "Sales Master Manager"},
                {"role": "Sales Manager"},
                {"role": "Item Manager"},
                {"role": "Stock User"},
                {"role": "Stock Manager"},
                {"role": "Customer"},
                {"role": "Accounts Manager"},
                {"role": "Accounts User"},
                {"role":"Auditor"},
            ]
        })
        doc.insert()

    if not frappe.db.exists("Role Profile", "Essential"):
        doc = frappe.get_doc({
            "doctype": "Role Profile",
            "role_profile": "Essential",
            "roles": [
                {"role": "Sales User"},
                {"role": "Sales Master Manager"},
                {"role": "Sales Manager"},
                {"role": "Accounts Manager"},
                {"role": "Accounts User"},
                {"role":"Auditor"},
                {"role": "Item Manager"},
                {"role": "Purchase User"},
                {"role": "Purchase Manager"},
                {"role": "Purchase Master Manager"},
                {"role": "Stock User"},
                {"role": "Stock Manager"},
                {"role": "Customer"},
                {"role": "HR Manager"},
                {"role": "HR User"},
            ]
        })
        doc.insert()
        
    if not frappe.db.exists("Role Profile", "Pro"):
        doc = frappe.get_doc({
            "doctype": "Role Profile",
            "role_profile": "Pro",
            "roles": [
                {"role": "Sales User"},
                {"role": "Sales Master Manager"},
                {"role": "Sales Manager"},
                {"role": "Item Manager"},
                {"role": "Purchase User"},
                {"role": "Purchase Manager"},
                {"role": "Purchase Master Manager"},
                {"role": "Stock User"},
                {"role": "Stock Manager"},
                {"role": "Customer"},
                {"role": "HR Manager"},
                {"role": "HR User"},
                {"role": "Accounts Manager"},
                {"role":"Auditor"},
                {"role": "Accounts User"},
                {"role": "Projects Manager"},
                {"role": "Projects User"},
            ]
        })
        doc.insert()
    
    if not frappe.db.exists("Role Profile", "Ultimate"):
        doc = frappe.get_doc({
            "doctype": "Role Profile",
            "role_profile": "Ultimate",
            "roles": [
                {"role": "Sales User"},
                {"role": "Sales Master Manager"},
                {"role": "Sales Manager"},
                {"role": "Item Manager"},
                {"role": "Purchase User"},
                {"role": "Purchase Manager"},
                {"role": "Purchase Master Manager"},
                {"role": "Stock User"},
                {"role": "Stock Manager"},
                {"role": "Customer"},
                {"role": "HR Manager"},
                {"role": "HR User"},
                {"role": "Accounts Manager"},
                {"role": "Accounts User"},
                {"role": "Projects Manager"},
                {"role": "Projects User"},
                {"role": "Support Team"},
                {"role": "Dashboard Manager"},
                {"role": "Report Manager"},
                {"role":"Quality Manager"},
                {"role":"Manufacturing Manager"},
                {"role":"Manufacturing User"},
                {"role":"Auditor"},
                {"role":"Maintenance Manager"},
                {"role":"Workspace Manager"},
            ]
        })
        doc.insert()


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
    