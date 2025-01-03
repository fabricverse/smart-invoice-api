import frappe
from smart_invoice_api.api import test_connection

def sync_failed_requests():
    print("start automated sync")

    if not test_connection():
        print("not connected")
        return

    settings = frappe.get_doc("VSDC Settings")

    # Get all pending Sync Request documents
    requests = frappe.get_all('Sync Request',
        filters={
            'endpoint': ['in', ['/trnsSales/saveSales', '/trnsPurchase/savePurchase']],
            'status': ['in', ['Connection Error', 'New']],
            'attempts': ['<=', int(settings.number_of_retries)],
            'response': ['is', 'set']
        },
        pluck='name')

    print(f"{len(requests)} items queued for sync", requests)
    
    for req in requests:
        print(req)
        doc = frappe.get_doc('Sync Request', req)
        doc.queue()
    
    print('automatic sync complete')