import frappe
import json
import requests



@frappe.whitelist()
def select_codes():
    data = frappe.request.json
    end_point = "/code/selectCodes"
    data = data = {
        "tpin": data["tpin"],
        "bhfId": data["bhf_id"],
        "lastReqDt": "20240902151722"
    }
    return call_vsdc(end_point, data)

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
