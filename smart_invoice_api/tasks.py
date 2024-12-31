import frappe

def sync_requests():

    # logging.info("sync_all_pending_requests_started")
    print("sync_all_pending_requests_started")
    settings = frappe.get_doc("VSDC Settings")
    # Get all pending Sync Request documents
    pending_requests = frappe.get_all('Sync Request', 
        filters={
            'status': ['in', ['Connection Error']],
            'attempts': ['<=', int(settings.number_of_retries)],
            'request_data': ['is', 'set']
        },
        pluck='name')
    
    for req in requests:
        doc = frappe.get_doc('Sync Request', req)        
        doc.queue()
