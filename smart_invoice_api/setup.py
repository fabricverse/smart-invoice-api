import frappe
from frappe.installer import update_site_config

def configure_vsdc_queue():
    """
    Programmatically injects the single-threaded 'vsdc' queue 
    into the site_config.json if it doesn't already exist.
    """
    site_config = frappe.get_site_config()
    
    if "workers" not in site_config:
        site_config["workers"] = {}
        
    # Check if our vsdc queue is already configured
    if "vsdc" not in site_config["workers"]:
        updated_workers = site_config["workers"]
        updated_workers["vsdc"] = {
            "timeout": 300,
            "concurrency": 1
        }
        
        # Save changes to site_config.json
        update_site_config("workers", updated_workers)
        
        print("Added sequential 'vsdc' background queue in site_config.json.")