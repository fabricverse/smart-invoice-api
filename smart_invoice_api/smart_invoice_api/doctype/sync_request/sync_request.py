# Copyright (c) 2024, Bantoo and contributors
# For license information, please see license.txt

import frappe
import json
import time
from frappe.model.document import Document
from smart_invoice_api.api import call_vsdc, get_settings as get_vsdc_settings
from smart_invoice_app.app import create_qr_code

class SyncRequest(Document):
    def on_update(self):
        """
        Triggered whenever the document is saved.
        """
        # CRITICAL SAFETY CHECK: If this change originated from the background worker, stop.
        if self.flags.in_vsdc_sync:
            return

        # REMOVED 'Success' from this list. We never auto-re-enqueue a completed success.
        if self.status in ['New', 'Error', 'Connection Error'] and self.request:
            self.queue_sync()

    def queue_sync(self):
        """Enqueues the sync process to run in the background."""
        frappe.enqueue(
            'smart_invoice_api.smart_invoice_api.doctype.sync_request.sync_request.run_vsdc_sync',
            queue='vsdc',
            timeout=300,
            doc_name=self.name,
            now=frappe.flags.in_test,
            enqueue_after_commit=True
        )
        if not frappe.flags.in_test:
            frappe.msgprint("VSDC Sync enqueued in background.", alert=True)

    def get_status_from_response(self, response):
        """Maps VSDC response codes to DocType status."""
        if not response or "error" in response:
            return "Connection Error"
        
        result_cd = response.get("resultCd")
        if result_cd in ['000', '001', '902']:
            return "Success"
        return "Error"

    def get_invoice_name(self):
        """Extracts the invoice number from the JSON request data."""
        try:
            req_data = json.loads(self.request) if isinstance(self.request, str) else self.request
            return req_data.get('cisInvcNo')
        except (ValueError, TypeError):
            return None


# --- Background Tasks ---

def run_vsdc_sync(doc_name):
    """
    Background worker task with exponential backoff.
    """
    try:
        # Load fresh copy inside worker transaction isolation
        doc = frappe.get_doc("Sync Request", doc_name)
    except frappe.DoesNotExistError:
        return

    # Set worker execution flag context early on the object instance
    doc.flags.in_vsdc_sync = True

    settings = get_vsdc_settings()
    max_retries = int(settings.number_of_retries or 5)
    current_attempts = int(doc.attempts or 0)

    if current_attempts >= max_retries:
        doc.db_set("status", "Do not Retry")
        notify_user(doc, f"Sync failed after {max_retries} attempts.", "red")
        return

    # Increment attempts cleanly
    new_attempts = current_attempts + 1
    doc.db_set("attempts", new_attempts)

    try:
        request_data = json.loads(doc.request)

        frappe.errprint(f"--- STARTING VSDC SYNC FOR: {doc.name} ---")
        vsdc_response = call_vsdc(doc.endpoint, request_data)
        frappe.errprint(f"--- FINISHED VSDC SYNC FOR: {doc.name} ---")
        
        status = doc.get_status_from_response(vsdc_response)
        
        # Handle Retries for Connection Issues
        if status == "Connection Error":
            wait_time = 30 * (2 ** (new_attempts - 1))
            
            frappe.enqueue(
                'smart_invoice_api.smart_invoice_api.doctype.sync_request.sync_request.run_vsdc_sync',
                queue='vsdc',
                timeout=300,
                doc_name=doc.name,
                wait_for_seconds=wait_time
            )
            
            doc.db_set({
                "status": status,
                "response": json.dumps(vsdc_response)
            })
            
            return

        # Persist final state metrics
        doc.db_set({
            "status": status,
            "response": json.dumps(vsdc_response)
        })

        frappe.publish_realtime("vsdc_sync_progress", {"item": 'My Latest Fertilizer', "status": "Success"})
        frappe.errprint('publish')
        frappe.publish_realtime(event="vsdc_sync_progress", message={"status": "Success"}, user=frappe.session.user, after_commit=True)
        frappe.publish_realtime(event="vsdc_sync_progress", message={"status": "Success"})
        frappe.publish_realtime(event='msgprint', message='test', user=frappe.session.user)
        if status == "Success":
            process_success_logic(doc, vsdc_response)
            notify_user(doc, f"Sync Request {doc.name} completed successfully.", "green")
            
        # Explicitly commit database transaction for this sequential item 
        # so the next queued item can read a clean database state.
        frappe.db.commit()
    
    except Exception as e:
        frappe.db.rollback() # Clear transaction state if crashed mid-execution
        frappe.log_error(frappe.get_traceback(), f"VSDC Sync Crash: {doc.name}")
        doc.db_set("status", "Error")
        frappe.publish_realtime("vsdc_sync_progress", {"item": 'My Latest Fertilizer', "status": "Failed", "message": str(e)})


def process_success_logic(doc, response_json):
    """Handles post-sync logic like QR code generation for Invoices."""
    sales_endpoints = ['/trnsSales/saveSales', '/trnsPurchase/savePurchase']
    
    if doc.endpoint in sales_endpoints:
        invoice_name = doc.get_invoice_name()
        is_sales = doc.endpoint == '/trnsSales/saveSales'
        doctype = 'Sales Invoice' if is_sales else 'Purchase Invoice'
        
        if invoice_name:
            try:
                inv_doc = frappe.get_doc(doctype, invoice_name)
                if is_sales and response_json.get("resultCd") == "000":
                    create_qr_code(inv_doc, data=response_json.get("data"))
            except Exception:
                frappe.log_error(frappe.get_traceback(), "VSDC Post-Process Success Error")


def notify_user(doc, message, indicator):
    """Helper to push realtime notifications to the document owner."""
    frappe.publish_realtime(
        event="vsdc_sync",
        message={
            "status": doc.status,
            "title": "VSDC Sync Update",
            "message": message,
            "indicator": indicator
        },
        user=doc.owner
    )