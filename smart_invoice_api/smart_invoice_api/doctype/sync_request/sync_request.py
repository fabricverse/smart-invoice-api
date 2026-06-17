# Copyright (c) 2024, Bantoo and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.model.document import Document

from smart_invoice_api.api import call_vsdc, get_settings


class SyncRequest(Document):
    def after_insert(self):
        """Triggered whenever the document is saved."""
        if self.flags.in_vsdc_sync:
            return

        if self.status in ["New", "Error", "Connection Error"] and self.request:
            self.queue_sync()

    def queue_sync(self):
        """Enqueues the sync process to run in the background."""

        frappe.enqueue(
            "smart_invoice_api.smart_invoice_api.doctype.sync_request.sync_request.sync",
            queue="vsdc",
            timeout=300,
            doc_name=self.name,
            now=frappe.flags.in_test,
            enqueue_after_commit=True,
        )

    def get_status_from_response(self, response):
        """Maps VSDC response codes to DocType status."""
        if not response or "error" in response:
            return "Connection Error"

        result_cd = response.get("resultCd")
        if result_cd in ["000", "001", "902"]:
            return "Success"
        return "Error"

    def get_invoice_name(self):
        """Extracts the invoice number from the JSON request data."""
        try:
            req_data = (
                json.loads(self.request)
                if isinstance(self.request, str)
                else self.request
            )
            return req_data.get("cisInvcNo")
        except (ValueError, TypeError):
            return None


# --- Background Tasks ---


def sync(doc_name):
    """Background worker task with exponential backoff."""
    try:
        doc = frappe.get_doc("Sync Request", doc_name)
    except frappe.DoesNotExistError:
        return

    # Set worker execution flag context early on the object instance
    doc.flags.in_vsdc_sync = True
    # frappe.publish_progress(50, title=_('Smart Invoice'), description=_('Connecting to ZRA servers...'))

    settings = get_settings(doc.company)
    max_retries = int(settings.max_retries or 5)
    current_attempts = int(doc.attempts or 0)

    if current_attempts >= max_retries:
        doc.db_set("status", "Do not Retry")
        frappe.db.commit()
        notify_user(
            doc, f"Sync stopped after {max_retries} unsuccessful attempts.", "red"
        )
        return

    new_attempts = current_attempts + 1
    doc.db_set("attempts", new_attempts, update_modified=False)

    try:
        request_data = json.loads(doc.request)
        vsdc_response = call_vsdc(doc, request_data)
        status = doc.get_status_from_response(vsdc_response)

        # Handle Retries for Connection Issues
        if status == "Connection Error":
            wait_time = 30 * (2 ** (new_attempts - 1))
            doc.db_set(
                {"status": status, "response": json.dumps(vsdc_response)},
                update_modified=False,
            )
            frappe.db.commit()

            frappe.enqueue(
                "smart_invoice_api.smart_invoice_api.doctype.sync_request.sync_request.sync",
                queue="vsdc",
                timeout=300,
                doc_name=doc.name,
            )
            return

        doc.status = status
        doc.response = json.dumps(vsdc_response)
        doc.flags.ignore_validate = True
        doc.save(ignore_permissions=True)
        frappe.db.commit()

    except Exception as e:
        doc.db_set({"status": status, "response": json.dumps(vsdc_response)})
        frappe.db.commit()

        frappe.log_error(frappe.get_traceback(), f"VSDC Sync Crash: {doc.name}")
        notify_user(doc, str(e), "red")


def notify_user(doc, message, indicator):
    """Pushes a final completion event to trigger form reload on the frontend."""
    frappe.publish_realtime(
        event="sync_progress",
        message={
            "status": doc.status,
            "message": message,
            "indicator": indicator,
            "name": doc.name,
        },
        user=doc.modifier,
    )
