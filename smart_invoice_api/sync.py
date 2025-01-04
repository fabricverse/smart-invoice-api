import frappe, time, json, requests
from frappe.utils import now_datetime
from datetime import timedelta
from smart_invoice_api.api import get_last_request_date, get_settings, call_vsdc
from smart_invoice_api.smart_invoice_api.doctype.sync_request.sync_request import calculate_backoff_delay

def sync_failed_requests():
    print("start automated sync")

    if not connect():
        print('not connection, exiting ...')
        return

    settings = frappe.get_doc("VSDC Settings")

    requests = frappe.get_all('Sync Request',
        filters={
            'endpoint': ['in', ['/trnsSales/saveSales', '/trnsPurchase/savePurchase', '/stock/saveStockItems', '/stockMaster/saveStockMaster']],
            'status': ['in', ['Connection Error', 'New']],
            'attempts': ['<=', int(settings.number_of_retries)],
            'response': ['is', 'set']
        },
        pluck='name')

    print(f"{len(requests)} items queued for sync", requests)
    
    for request in requests:
        doc = frappe.get_doc('Sync Request', request)
        doc.queue()
    
    print('automatic sync complete')


def connect():
    if test_connection():
        return True
    return False

@frappe.whitelist()
def test_connection():   
    settings = get_settings()
    data={
        "tpin": settings.tpin, 
        "bhf_id": "000"
    }
    
    if not data:
        data = frappe.request.json
    endpoint = "/branches/selectBranches"

    if data.get("initialize", False):
        last_req_dt = "20250101200000"
    else:
        last_req_dt = get_last_request_date(endpoint)
    
    data = {
        "tpin": data["tpin"],
        "bhfId": data["bhf_id"],
        "lastReqDt": last_req_dt
    }
    response = call_vsdc(endpoint, data)
    if response:
        if response and response.get('error', response) != "Smart Invoice VSDC Timeout":
            if response and not response.get('error') and response.get('resultCd') in ["000", "001"]:
                return True
    return False

    # Get the current time and subtract the required minutes
    # interval = now_datetime() - timedelta(minutes=6)

    # # Fetch all Sync Requests for the specified endpoint in the given time interval
    # last_test = frappe.get_all("Sync Request", 
    #     fields=['attempts'],
    #     filters=[
    #         ["endpoint", "=", "/branches/selectBranches"],
    #         ["creation", ">=", interval]
    #     ],
    #     order_by="creation desc"
    # )

    # test_count = len(last_test)
    # delay = calculate_backoff_delay(test_count) * 10

    # print(f"Number of tests in the last 10 minutes: {test_count}")
    # print(f"delay: {delay}")

    # time.sleep(delay)