import frappe

def sync_all_pending_requests():

    logging.info("sync_all_pending_requests_started")
    # Get all pending Sync Request documents
    pending_requests = frappe.get_all('Sync Request', 
        filters={'status': 'New'}, 
        pluck='name')
    
    for request_name in pending_requests:
        doc = frappe.get_doc('Sync Request', request_name)
        sync_attempt(doc)

# @frappe.whitelist()
def sync_attempt(doc):
    doc.attempts = (doc.attempts or 0) + 1
    doc.save()
    frappe.db.commit()