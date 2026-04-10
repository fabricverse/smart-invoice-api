# Copyright (c) 2024, Bantoo and contributors
# For license information, please see license.txt
import frappe, json
from frappe.model.document import Document
from smart_invoice_api.api import call_vsdc, get_settings as get_vsdc_settings
from smart_invoice_app.app import create_qr_code 
# from frappe.utils.background_jobs import enqueue

class SyncRequest(Document):
    def on_update(self):
        """
        Triggered whenever the document is saved.
        We only enqueue if the status is 'New' or 'Connection Error'.
        """
        queue = 'y'
        if queue == "y":

            if self.status in ['New', 'Error', 'Success'] and self.request:
                self.queue_sync()
        else:
            run_vsdc_sync(self)

    def queue_sync(self):
        # Enqueue the sync process to run in the background
        # 'vsdc_queue' helps separate this from standard long/short jobs
        print('queue_sync ****************')
        frappe.enqueue(
            'smart_invoice_api.smart_invoice_api.doctype.sync_request.sync_request.run_vsdc_sync', # Update to your actual path
            queue='long', 
            timeout=300,
            doc_name=self.name,
            now=frappe.flags.in_test
        )
        frappe.msgprint("VSDC Sync enqueued in background.", alert=True)

    def get_status(self, response):
        if not response or "error" in response:
            return "Connection Error"
        
        result_cd = response.get("resultCd")
        if result_cd in ['000', '001', '902']:
            return "Success"
        return "Error"

    def get_invoice_name(self):
        req_data = self.request
        if isinstance(req_data, str):
            req_data = json.loads(req_data)
        return req_data.get('cisInvcNo')

# --- Background Task (Outside the Class) ---
def run_vsdc_sync(doc_name):
    try:
        doc = frappe.get_doc("Sync Request", doc_name)
    except frappe.DoesNotExistError:
        return # Doc might have been deleted
    print(f"Running VSDC sync for document: {doc.name}")
    """
    Background worker task with exponential backoff and connection handling.
    """
    # 1. Fetch the document and settings
    settings = get_vsdc_settings()
    max_retries = int(settings.number_of_retries or 5)
    current_attempts = int(doc.attempts or 0)

    # 2. Check if we've already exhausted retries
    if current_attempts >= max_retries:
        doc.db_set("status", "Do not Retry")
        frappe.publish_realtime("msgprint", {
            "message": f"Sync failed for {doc.name} after {max_retries} attempts.",
            "indicator": "red"
        }, user=doc.owner)
        return

    # 3. Log the attempt and increment
    new_attempts = current_attempts + 1
    doc.db_set("attempts", new_attempts)
    try:
    
        # 4. Execute the API call
        request_data = json.loads(doc.request)
        vsdc_response = call_vsdc(doc.endpoint, request_data)
        
        status = doc.get_status(vsdc_response)
        
        # 5. Handle "Connection Refused" or "Timeout" specifically for requeueing
        # We check for the error keys returned by your call_vsdc function
        if isinstance(vsdc_response, dict) and "error" in vsdc_response:
            error_msg = vsdc_response.get("error", "")
            if "Timeout" in error_msg or "Connection Error" in error_msg:
                
                # Calculate exponential backoff (e.g., 30s, 60s, 120s...)
                wait_time = 30 * (2 ** (new_attempts - 1))
                
                # Re-enqueue the job for later
                frappe.enqueue(
                    'smart_invoice_api.smart_invoice_api.doctype.sync_request.sync_request.run_vsdc_sync',
                    queue='long',
                    timeout=300, # 10 mins for the 2-min VSDC spikes
                    doc_name=doc.name,
                    at_front=False,
                    enqueue_after_serve=True,
                    wait_for_seconds=wait_time
                )
                
                doc.db_set("status", "Connection Error")
                return

        # 6. Update document with the final result
        doc.db_set({
            "status": status,
            "response": json.dumps(vsdc_response)
        })

        # 7. Post-processing for successful syncs
        if status == "Success":
            process_success_logic(doc, vsdc_response)
            frappe.publish_realtime(
                event="vsdc_sync",
                message={
                    "status": status,
                    "title": "VSDC Sync Update",
                    "message": f"Sync Request {doc.name} completed successfully.",
                    "indicator": "green" if status == "Success" else "orange"
                },
                user=frappe.session.user
            )
    
    except Exception as e:
        # Catch logic errors (JSON parsing, code crashes)
        frappe.log_error(frappe.get_traceback(), f"Sync Request Crash: {doc.name}")
        doc.db_set("status", "Error")
        print(f"Error during VSDC sync for {doc.name}: {str(e)}")

def process_success_logic(doc, response_json):
    """Handles post-sync logic like QR codes"""
    if doc.endpoint in ['/trnsSales/saveSales', '/trnsPurchase/savePurchase']:
        invoice_name = doc.get_invoice_name()
        invoice_type = 'Sales Invoice' if doc.endpoint == '/trnsSales/saveSales' else 'Purchase Invoice'
        
        if invoice_name:
            try:
                inv_doc = frappe.get_doc(invoice_type, invoice_name)
                if invoice_type == "Sales Invoice" and response_json.get("resultCd") == "000":
                    data = response_json.get("data")
                    create_qr_code(inv_doc, data=data)
            except Exception:
                pass

def calculate_backoff_delay(attempt):
    initial_delay = 1  # Initial delay in seconds
    delay = initial_delay * (2 ** (attempt - 1)) # Exponential backoff formula
    return delay