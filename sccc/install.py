import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

@frappe.whitelist()
def after_install():
    customfield()

def customfield():
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
    