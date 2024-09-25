import frappe
import json
import requests



# called from smart_invoice_app / rest api
@frappe.whitelist()
def select_codes(data=None):
    if not data:
        data = frappe.request.json
    end_point = "/code/selectCodes"
    data = {
        "tpin": data["tpin"],
        "bhfId": data["bhf_id"],
        "lastReqDt": "20240902151722"
    }
    return create_sync_request(end_point, data)

# creating a sync request doc triggers the call to vsdc
def create_sync_request(end_point, data):
    try:
        sr = frappe.get_doc({
            "doctype": "Sync Request",
            "attempts": 0,
            "end_point": end_point,
            "status": "New",
            "doc_owner": frappe.session.user,
            "request_data": data            
        })
        sr.insert(ignore_permissions=True)   
        return sr
        frappe.db.commit() 
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error creating Sync Request")
        return {"error": str(e)}

# to be called from sync_request doctype
def call_vsdc(end_point, data):
    settings = get_settings()
    base_url = settings.base_url
    try:
        r = requests.post(base_url + end_point, json=data, headers={"Content-Type": "application/json"})
        response_json = r.json()
        return response_json.get("message", response_json)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error calling VSDC")
        return {"error": str(e)}


    

def get_settings():
    settings = frappe.get_single("VSDC Settings")
    if not settings.base_url or not settings.environment:
        frappe.throw("VSDC Settings are incomplete. The admin will be notified.")
    return settings


def get_status(response):
    if response.get("resultCd"):
        return "Success"
    else:
        return "Error"


def sync_attempt(doc):	
	vsdc_response = call_vsdc(doc.end_point, doc.request_data)
	doc.attempts += 1
	doc.response_data = vsdc_response
	doc.status = get_status(vsdc_response)
	doc.save()

@frappe.whitelist()
def test_connection():
    settings = get_settings()
    data={
        "tpin": settings.tpin, "bhf_id": "000"
    }
    sr = select_codes(data)
    if sr:
        frappe.msgprint("Connection Successful")
    else:
        frappe.msgprint("Connection Failed")
    frappe.errprint("sync request: " + sr.name)