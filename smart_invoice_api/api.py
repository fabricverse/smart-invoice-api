import frappe
import json
import requests

def get_last_request_date(endpoint):
    # find the last sync_request with status success, endpoint and request_data containing lastReqDt
    sync_request = frappe.get_all(
        "Sync Request",
        filters=[
            ["status", "=", "Success"],
            ["endpoint", "=", endpoint],
            ["response_data", "like", "%resultDt%"],
            ["response_data", "not like", '%"resultDt":null%']
        ],
        fields=["response_data"],
        order_by="creation desc",
        limit=1
    )
    
    if sync_request:
        response_data = sync_request[0].response_data
        response_data_json = json.loads(response_data)

        if response_data_json.get("resultDt", None):    
            return response_data_json.get("resultDt", None)    
    return "20231001200000"


# called from smart_invoice_app / rest api
@frappe.whitelist()
def select_codes(data=None):
    if not data:
        data = frappe.request.json
    endpoint = "/code/selectCodes"
    if data.get("initialize", False):
        last_req_dt = "20231001200000"
    else:
        last_req_dt = get_last_request_date(endpoint)
    
    data = {
        "tpin": data["tpin"],
        "bhfId": data["bhf_id"],
        "lastReqDt": last_req_dt
    }
    return create_sync_request(endpoint, data)


@frappe.whitelist()
def select_item_classes(data=None):
    if not data:
        data = frappe.request.json
    endpoint = "/itemClass/selectItemsClass"

    if data.get("initialize", False):
        last_req_dt = "20231001200000"
    else:
        last_req_dt = get_last_request_date(endpoint)
    
    data = {
        "tpin": data["tpin"],
        "bhfId": data["bhf_id"],
        "lastReqDt": last_req_dt
    }
    return create_sync_request(endpoint, data)


@frappe.whitelist()
def save_branche_user(data=None):
    if not data:
        data = frappe.request.json
    endpoint = "/branches/saveBrancheUser"

    if data.get("initialize"):
        last_req_dt = "20231001200000"
    else:
        last_req_dt = get_last_request_date(endpoint)
    
    # Include all the required user data in the API request
    api_data = {
        "tpin": data["tpin"],
        "bhfId": data["bhfId"],
        "userId": data["userId"],
        "userNm": data["userNm"],
        "adrs": data["adrs"],
        "useYn": data["useYn"],
        "regrNm": data["regrNm"],
        "regrId": data["regrId"],
        "modrNm": data["modrNm"],
        "modrId": data["modrId"],
        "lastReqDt": last_req_dt
    }
    return create_sync_request(endpoint, api_data)

@frappe.whitelist()
def save_sales(data=None):
    if not data:
        data = frappe.request.json
    endpoint = "/trnsSales/saveSales"
    return create_sync_request(endpoint, data)


@frappe.whitelist()
def save_purchase(data=None):
    if not data:
        data = frappe.request.json
    endpoint = "/trnsPurchase/savePurchase"
    return create_sync_request(endpoint, data)

@frappe.whitelist()
def save_item(data=None):
    if not data:
        data = frappe.request.json
    endpoint = "/items/saveItem"
    return create_sync_request(endpoint, data)

@frappe.whitelist()
def save_item_composition(data=None):
    if not data:
        data = frappe.request.json
    endpoint = "/items/saveItemComposition"
    return create_sync_request(endpoint, data)

@frappe.whitelist()
def save_stock_items(data=None):
    if not data:
        data = frappe.request.json
    endpoint = "/stock/saveStockItems"
    return create_sync_request(endpoint, data)

@frappe.whitelist()
def save_stock_master(data=None):
    if not data:
        data = frappe.request.json
    endpoint = "/stockMaster/saveStockMaster"
    return create_sync_request(endpoint, data)

@frappe.whitelist()
def update_item(data=None):
    if not data:
        data = frappe.request.json
    endpoint = "/items/updateItem"
    return create_sync_request(endpoint, data)

@frappe.whitelist()
def save_branche_customer(data=None):
    if not data:
        data = frappe.request.json
    endpoint = "/branches/saveBrancheCustomers"

    # Include all the required data in the API request
    api_data = {
        "tpin": data["tpin"],
        "bhfId": data["bhfId"],
        "custNo": data["custNo"],
        "custTpin": data["custTpin"],
        "custNm": data["custNm"],
        "adrs": data["adrs"],
        "email": data["email"],
        "faxNo": data["faxNo"],
        "useYn": data["useYn"],
        "remark": data.get("remark", ""),
        "regrNm": data["regrNm"],
        "regrId": data["regrId"],
        "modrNm": data["modrNm"],
        "modrId": data["modrId"]
    }
    
    return create_sync_request(endpoint, api_data)


@frappe.whitelist()
def select_branches(data=None):
    if not data:
        data = frappe.request.json
    endpoint = "/branches/selectBranches"

    if data.get("initialize", False):
        last_req_dt = "20231001200000"
    else:
        last_req_dt = get_last_request_date(endpoint)
    
    data = {
        "tpin": data["tpin"],
        "bhfId": data["bhf_id"],
        "lastReqDt": last_req_dt
    }
    return create_sync_request(endpoint, data)
    
    
@frappe.whitelist()
def select_trns_purchase_sales(data=None):
    if not data:
        data = frappe.request.json
    endpoint = "/trnsPurchase/selectTrnsPurchaseSales"

    if data.get("initialize", False):
        last_req_dt = "20231001200000"
    else:
        last_req_dt = get_last_request_date(endpoint)
    
    data = {
        "tpin": data["tpin"],
        "bhfId": data["bhf_id"],
        "lastReqDt": last_req_dt
    }
    
    return create_sync_request(endpoint, data)


@frappe.whitelist()
def select_import_items(data=None):
    if not data:
        data = frappe.request.json
    endpoint = "/imports/selectImportItems"

    if data.get("initialize", False):
        last_req_dt = "20231001200000"
    else:
        last_req_dt = get_last_request_date(endpoint)
    
    data = {
        "tpin": data["tpin"],
        "bhfId": data["bhf_id"],
        "lastReqDt": last_req_dt
    }
    
    return create_sync_request(endpoint, data)


@frappe.whitelist()
def update_import_items(data=None):
    if not data:
        data = frappe.request.json
    endpoint = "/imports/updateImportItems"
    return create_sync_request(endpoint, data)


@frappe.whitelist()
def select_item(data=None):
    if not data:
        data = frappe.request.json
    endpoint = "/items/selectItem"
    return create_sync_request(endpoint, data)

@frappe.whitelist()
def select_items(data=None):
    if not data:
        data = frappe.request.json

    endpoint = "/items/selectItems"
    
    if data.get("initialize", False):
        last_req_dt = "20231001200000"
    else:
        last_req_dt = get_last_request_date(endpoint)

    data.update({"lastReqDt": last_req_dt})

    return create_sync_request(endpoint, data)

def update_vsdc_details(tpin, vsdc_serial, environment):
    settings = get_settings()

    if (settings.tpin != tpin or 
        settings.vsdc_serial != vsdc_serial or
        settings.environment != environment):

        settings.tpin = tpin 
        settings.vsdc_serial = vsdc_serial
        settings.environment = environment 

        settings.save()


@frappe.whitelist()
def initialize_vsdc(data=None):
    if not data:
        data = frappe.request.json

    endpoint = "/initializer/selectInitInfo"
    
    default_server = data.get("default_server")
    tpin = data.get("tpin")
    vsdc_serial = data.get("vsdc_serial")
    branch = data.get("bhf_id")
    environment = data.get("environment")

    payload = {
        "tpin": tpin,
        "bhfId": branch,
        "dvcSrlNo": vsdc_serial
    }

    if default_server == 1:
        update_vsdc_details(tpin, vsdc_serial, environment)

    return create_sync_request(endpoint, payload)

# creating a sync request doc triggers the call to vsdc
def create_sync_request(endpoint, data):
    
    try:
        if not data:
            return {"response_data": {"resultCd": "10000", "resultMsg": f"{frappe.bold('data')} is required to create a sync request"}}
        sr = frappe.new_doc("Sync Request")
        sr.attempts = 0
        sr.endpoint = endpoint
        sr.status = "New"
        sr.doc_owner = frappe.session.user
        sr.request_data = data            
        
        sr.flags.ignore_permissions=True
        sr.flags.ignore_mandatory=True
        sr.insert()   
        return sr
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error creating Sync Request")
        print(frappe.get_traceback())
        return {"error": str(e)}


# called from sync_request doctype
def call_vsdc(endpoint, data):
    settings = get_settings()
    base_url = settings.base_url

    try:
        r = requests.post(
            base_url + endpoint, 
            json=data, 
            headers={"Content-Type": "application/json"},
            timeout=10  # timeout period in seconds
        )
        response_json = r.json()
        return response_json.get("message", response_json)

    except json.decoder.JSONDecodeError as e:
        frappe.msgprint(title="Smart Invoice Failure", msg=str(r.text))
    except requests.Timeout:
        error_msg = "Smart Invoice VSDC timedout"
        frappe.log_error(error_msg, "VSDC timeout")
        frappe.throw(error_msg)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "VSDC Error")
        frappe.throw(str(e))


def get_settings():
    settings = frappe.get_cached_doc("VSDC Settings", "VSDC Settings")
    if not settings.base_url or not settings.environment:
        frappe.throw("VSDC Settings are incomplete. The admin will be notified.")
    return settings


def get_status(response):
    if response and response.get("resultCd", None):
        return "Success"
    else:
        return "Error"


def sync_attempt(doc):	
    vsdc_response = call_vsdc(doc.endpoint, doc.request_data)
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
    if sr and sr.get("response_data"):

        frappe.msgprint("Connection Successful")
    else:
        frappe.msgprint("Connection Failed")