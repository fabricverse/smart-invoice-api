# Copyright (c) 2024, Bantoo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from smart_invoice_api.api import call_vsdc, get_status


"""
Sync Request created {'resultCd': '000', 'resultMsg': 'It is succeeded', 'resultDt': '20240924163305', 'data': {'clsList': [{'cdCls': '06', 'cdClsNm': 'Sale category', 'userDfnNm1': None, 'dtlList': [{'cd': '4', 'cdNm': 'RVAT', 'userDfnCd1': None}]}, {'cdCls': '10', 'cdClsNm': 'Quantity Unit', 'userDfnNm1': None, 'dtlList': [{'cd': 'P1', 'cdNm': 'Pack', 'userDfnCd1': None}, {'cd': 'EA', 'cdNm': 'Each', 'userDfnCd1': None}, {'cd': 'PL', 'cdNm': 'Pallet', 'userDfnCd1': None}, {'cd': 'EACH', 'cdNm': 'Each', 'userDfnCd1': None}, {'cd': 'Ft', 'cdNm': 'Feet', 'userDfnCd1': None}, {'cd': 'MM', 'cdNm': 'Millimetre', 'userDfnCd1': None}, {'cd': 'In', 'cdNm': 'Inches', 'userDfnCd1': None}, {'cd': 'Oz', 'cdNm': 'Ounce', 'userDfnCd1': None}, {'cd': 'YR', 'cdNm': 'Year', 'userDfnCd1': None}, {'cd': 'M ', 'cdNm': 'Month', 'userDfnCd1': None}, {'cd': 'Wk', 'cdNm': 'Week', 'userDfnCd1': None}, {'cd': 'D', 'cdNm': 'Day', 'userDfnCd1': None}, {'cd': 'hr', 'cdNm': 'Hour', 'userDfnCd1': None}, {'cd': 'ha', 'cdNm': 'Hectare', 'userDfnCd1': None}, {'cd': 'yd2', 'cdNm': 'Square yards', 'userDfnCd1': None}, {'cd': 'ft2', 'cdNm': 'Square feet', 'userDfnCd1': None}, {'cd': 'cm2', 'cdNm': 'Square centimetre', 'userDfnCd1': None}, {'cd': 'm2', 'cdNm': 'Square metre', 'userDfnCd1': None}, {'cd': 'pt', 'cdNm': 'Pints', 'userDfnCd1': None}, {'cd': 'qt', 'cdNm': 'Quarts', 'userDfnCd1': None}, {'cd': 'mm', 'cdNm': 'Millilitre', 'userDfnCd1': None}, {'cd': '2X', 'cdNm': 'Meter/Minute', 'userDfnCd1': None}, {'cd': '4G', 'cdNm': 'Microliter', 'userDfnCd1': None}, {'cd': '4O', 'cdNm': 'Microfarad', 'userDfnCd1': None}, {'cd': '4T', 'cdNm': 'Pikofarad', 'userDfnCd1': None}, {'cd': 'A', 'cdNm': 'Ampere', 'userDfnCd1': None}, {'cd': 'A87', 'cdNm': 'Gigaohm', 'userDfnCd1': None}, {'cd': 'A93', 'cdNm': 'Gram/Cubic meter', 'userDfnCd1': None}, {'cd': 'ACR', 'cdNm': 'Acre', 'userDfnCd1': None}, {'cd': 'B34', 'cdNm': 'Kilogram/cubic decimeter', 'userDfnCd1': None}, {'cd': 'B45', 'cdNm': 'Kilomol', 'userDfnCd1': None}, {'cd': 'B47', 'cdNm': 'Kilonewton', 'userDfnCd1': None}, {'cd': 'B73', 'cdNm': 'Meganewton', 'userDfnCd1': None}, {'cd': 'B75', 'cdNm': 'Megohm', 'userDfnCd1': None}, {'cd': 'B78', 'cdNm': 'Megavolt', 'userDfnCd1': None}, {'cd': 'B84', 'cdNm': 'Microampere', 'userDfnCd1': None}, {'cd': 'BAG', 'cdNm': 'Bag', 'userDfnCd1': None}, {'cd': 'BAR', 'cdNm': 'bar', 'userDfnCd1': None}, {'cd': 'BOT', 'cdNm': 'Bottle', 'userDfnCd1': None}, {'cd': 'BQK', 'cdNm': 'Becquerel/kilogram', 'userDfnCd1': None}, {'cd': 'C10', 'cdNm': 'Millifarad', 'userDfnCd1': None}, {'cd': 'C36', 'cdNm': 'Mol per cubic meter', 'userDfnCd1': None}, {'cd': 'C38', 'cdNm': 'Mol per liter', 'userDfnCd1': None}, {'cd': 'C39', 'cdNm': 'Nanoampere', 'userDfnCd1': None}, {'cd': 'C3S', 'cdNm': 'Cubic centimeter/second', 'userDfnCd1': None}, {'cd': 'C41', 'cdNm': 'Nanofarad', 'userDfnCd1': None}, {'cd': 'C56', 'cdNm': 'Newton/Square millimeter', 'userDfnCd1': None}, {'cd': 'CCM', 'cdNm': 'Cubic centimeter', 'userDfnCd1': None}, {'cd': 'CD', 'cdNm': 'Candela', 'userDfnCd1': None}, {'cd': 'CDM', 'cdNm': 'Cubic decimeter', 'userDfnCd1': None}]}, {'cdCls': '400', 'cdClsNm': 'Taxation Type', 'userDfnNm1': 'Tax Rate', 'dtlList': [{'cd': 'A', 'cdNm': 'Standard Rated(16%)', 'userDfnCd1': '16'}, {'cd': 'B', 'cdNm': 'Minimum Taxable Value (MTV-16%)', 'userDfnCd1': '16'}, {'cd': 'C3', 'cdNm': 'Zero-rated by nature', 'userDfnCd1': '0'}, {'cd': 'D', 'cdNm': 'Exempt', 'userDfnCd1': '0'}, {'cd': 'RVAT', 'cdNm': 'Reverse VAT', 'userDfnCd1': '16'}, {'cd': 'E', 'cdNm': 'Disbursement', 'userDfnCd1': '0'}]}]}}
"""
class SyncRequest(Document):
	def after_insert(self):
		# frappe.enqueue(sync_attempt, doc=self, queue='short')
		sync_attempt(self)

def sync_attempt(doc):	
	vsdc_response = call_vsdc(doc.end_point, doc.request_data)
	# print("Sync Request created", r)
	doc.attempts += 1
	doc.response_data = vsdc_response
	doc.status = get_status(vsdc_response)
	doc.save()

	

	




