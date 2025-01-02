# Copyright (c) 2024, Bantoo and contributors
# For license information, please see license.txt

import frappe, json, time
from frappe.model.document import Document
from smart_invoice_api.api import call_vsdc, get_settings as get_vsdc_settings
from smart_invoice_app.app import save_purchase_invoice_api, create_qr_code
from frappe.utils.background_jobs import enqueue

class SyncRequest(Document):
	def after_insert(self):
		print('after_insert')  
		# if not self.flags.get('from_queue', False):
		self.sync_attempt()

	def before_save(self):
		print("before_save")
		# self.sync_attempt()
		# self.flags.from_queue = False

	def sync_attempt(self):
		print("sync_attempt")
		try:
			vsdc_response = call_vsdc(self.endpoint, json.loads(self.request_data))
			self.response_data_copy = str(vsdc_response)
			self.status = self.get_status(vsdc_response)
			self.attempts+=1
		except Exception as e:
			self.attempts+=1
			self.status = self.get_status(vsdc_response)
			self.response_data_copy = str({"error": str(e)})
			print(str({"error--": str(e)}))
		finally:
			self.save()			
			frappe.db.commit()


	@frappe.whitelist()
	def queue(self):
		print('queue')
		testing = True

		is_sales_or_purchase_trans = self.endpoint in ['/trnsSales/saveSales', '/trnsPurchase/savePurchase']		
		is_first_attempt = int(self.attempts or 0) <= 0
		
		if is_first_attempt or not self.request_data or not is_sales_or_purchase_trans or self.status != 'Connection Error':
			print('returning')
			return

		print("self.attempts", self.attempts)

		request_data = self.request_data
		if type(self.request_data) == str:
			request_data = json.loads(request_data)

		invoice_name = request_data.get('cisInvcNo', None)
		print("invoice_name", invoice_name)

		if not invoice_name: 
			print('no invoice name')
			return

		settings = get_vsdc_settings()
		initial_delay = 1  # Initial delay in seconds
		max_retries = settings.number_of_retries    # Maximum number of retries
		delay = initial_delay * (2 ** (self.attempts - 1))  # Exponential backoff formula

		if self.attempts < max_retries:
			print(f"Retrying in {delay} seconds...")
			time.sleep(delay)
			print(1)
			if self.endpoint == '/trnsPurchase/savePurchase':
				invoice_doc = frappe.get_doc('Purchase Invoice', invoice_name)
				frappe.enqueue(
					"smart_invoice_app.app.save_purchase_invoice_api",
					invoice=invoice_doc,
					queue='short',
					now=False,
					timeout=300
				)
			elif self.endpoint == '/trnsSales/saveSales':
				print('save sale')
				invoice_doc = frappe.get_doc('Sales Invoice', invoice_name)
				self.sync_attempt()

				# self.save()
				# frappe.db.commit()

				self.flags.from_queue = True

				print('self.response_data_copy', self.response_data_copy)

				json_data = json.loads(self.response_data_copy)

				if json_data.get("resultCd") == "000":
					msg = json_data.get("data")
					create_qr_code(invoice_doc, data=msg)
				else:
					frappe.msgprint(f"{json_data.get('resultMsg')}", title=f"Smart Invoice Failure - {json_data.get('resultCd')}")
				
			print(f'{invoice_name} completed')
		else:
			self.status = "Do not Retry"
			self.response_data_copy = {'error': "Max retries reached. Please check the network or server status."}
			self.save()
			frappe.db.commit()
			print("Max retries reached. Stopping retries.")
			
	def get_status(self, response):
		if response and response.get("resultCd", None):
			if response.get("resultCd", None) in ['000', '001']:
				return "Success"
			else:
				return "Error"
		elif not response.get("resultCd", None):
			return "Connection Error"
		else:
			return "Error"
