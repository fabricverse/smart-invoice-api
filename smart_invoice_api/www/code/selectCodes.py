""""
import frappe
# from smart_invoice_api.app import get_boot_data
import requests
import json

def get_context(context):
	data = frappe.form_dict

	# boot = get_boot_data()
	# settings = boot["settings"]

	# testing
	if not data:
		
		data = {}
		
	
	print(data)
	frappe.errprint("2")

	context.data = data

	return context""""