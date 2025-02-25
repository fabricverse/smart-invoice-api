# Copyright (c) 2024, Bantoo and contributors
# For license information, please see license.txt

import frappe, json, time
from frappe.model.document import Document
from smart_invoice_api.api import call_vsdc, get_settings as get_vsdc_settings
from smart_invoice_app.app import save_purchase_invoice_api, create_qr_code # TODO: separate for hosting separately
from frappe.utils.background_jobs import enqueue

class SyncRequest(Document):
    def after_insert(self):
        self.sync()
        # self.queue()

    # def before_save(self):
    #     print("before_save")
        # self.sync()
        # self.queue()

    @frappe.whitelist()
    def sync(self):
        self.attempts+=1
        try:
            vsdc_response = call_vsdc(self.endpoint, json.loads(self.request))
            self.response = str(json.dumps(vsdc_response))
            self.status = self.get_status(vsdc_response)
        except Exception as e:
            self.status = "Error"
            self.response = str({"error": str(e)})
            print(str({"error--": str(e)}))
        finally:			
            if not is_called_from("before_save"):
                self.save()
                frappe.db.commit()

    @frappe.whitelist()
    def queue(self):
        valid_transaction = self.endpoint in ['/trnsSales/saveSales', '/trnsPurchase/savePurchase',  '/stock/saveStockItems', '/stockMaster/saveStockMaster']		
        # is_first_attempt = int(self.attempts or 0) <= 0
        
        if not self.request or not valid_transaction or self.status not in ['Connection Error', 'New']:
        	return
            
        invoice_name = None
        if self.endpoint in ['/trnsSales/saveSales', '/trnsPurchase/savePurchase']:
            invoice_name = self.get_invoice_name()
            if not invoice_name:
                return
        settings = get_vsdc_settings()
        delay = 0 # calculate_backoff_delay(self.attempts)
        max_retries = settings.number_of_retries    # Maximum number of retries

        if int(self.attempts) < int(max_retries):
            frappe.msgprint(f"Retrying ...", alert=True, indicator="success")
            time.sleep(delay)
            if self.endpoint == '/trnsPurchase/savePurchase':
                self.handle_invoice_sync(invoice_name, 'Purchase Invoice')
            elif self.endpoint == '/trnsSales/saveSales':
                self.handle_invoice_sync(invoice_name, 'Sales Invoice')
            elif self.endpoint in ['/stock/saveStockItems', '/stockMaster/saveStockMaster']:
                self.handle_stock_sync()
        else:
            self.status = "Do not Retry"
            self.response = str(json.dumps({"error": "Max retries reached. Please check the network or server status."}))

            if not is_called_from("before_save"):
                self.save()
                frappe.db.commit()
            frappe.msgprint("Max retries reached", alert=True, indicator="red")

    def handle_stock_sync(self):
        self.sync()
        response_json = json.loads(self.response)
        
        if response_json.get("resultCd") not in ["000", "001"]:
            self.db_set({
                'status': self.get_status(response_json),
                'response': str(json.dumps(response_json))
            })
            self.notify_update()

    def handle_invoice_sync(self, invoice_name, invoice_type):
        try:
            invoice_doc = frappe.get_doc(invoice_type, invoice_name)
            self.sync()
        except Exception as e:
            invoice_doc = None

        if not invoice_doc:
            return
        response_json = json.loads(self.response)
        
        if response_json.get("resultCd") == "000":
            if invoice_type == "Sales Invoice":
                data = response_json.get("data")
                create_qr_code(invoice_doc, data=data)
        else:
            self.db_set({
                'status': self.get_status(response_json),
                'response': str(json.dumps(response_json))
            })
            self.notify_update()

    def get_invoice_name(self):
        request = self.request
        if type(self.request) == str:
            request = json.loads(request)

        return request.get('cisInvcNo', None)
            
    def get_status(self, response):
        if response and response.get("resultCd", None):
            if response.get("resultCd", None) in ['000', '001', '902']:
                return "Success"
            elif response.get("status", None) in [400]:
                return "Error"
            else:
                return "Error"
        elif not response.get("resultCd", None):
            return "Connection Error"
        else:
            return "Error"

import inspect
def is_called_from(name):
    # Get the current call stack
    stack = inspect.stack()
    
    # Iterate through the stack frames
    for frame in stack:
        # Check if the function name is 'before_save'
        if frame.function == name:
            return True
    return False

def calculate_backoff_delay(attempt):
    initial_delay = 1  # Initial delay in seconds
    delay = initial_delay * (2 ** (attempt - 1)) # Exponential backoff formula
    return delay