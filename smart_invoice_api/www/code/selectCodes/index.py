
import frappe
def get_context(context):
        
    # data = frappe.form_dict
    print("selectCodes")
    frappe.errprint("selectCodes")
    # "selectCOdes"
    context.data = "selectCodes 1"

    return context