import frappe
from smart_invoice_api.api import sync_attempt

def sync_all_pending_requests():

    # logging.info("sync_all_pending_requests_started")
    print("sync_all_pending_requests_started")
    # Get all pending Sync Request documents
    pending_requests = frappe.get_all('Sync Request', 
        filters={'status': ['in', ['New', 'Error']]}, 
        pluck='name')
    
    for request_name in pending_requests:
        doc = frappe.get_doc('Sync Request', request_name)
        sync_attempt(doc)
