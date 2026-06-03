// Copyright (c) 2024, Bantoo and contributors
// For license information, please see license.txt

frappe.ui.form.on("VSDC Settings", {
	refresh(frm) {
 // add button to test connection
        // if (frm.doc.environment == "Sandbox"){
        if (!frm.doc.__islocal){
            frm.add_custom_button(__("Connection Test"), function() {
                frappe.call({
                    method: "smart_invoice_api.api.test_connection",
                })
            }, __("Menu"));
            frm.page.get_inner_group_button("Menu")
                .find("button")
                .removeClass("btn-default")
                .addClass("btn-info");
        // }
        }
	},
	setup(frm) {
        // Prevent layout shifting and wobbling when global progress overlays load
        document.documentElement.style.scrollbarGutter = "stable";
        
        // Listen for final logic to trigger alerts and reload the specific form
        frappe.realtime.on("sync_progress", function(data) {
            // 1. Scoping Guard: Ensure this event belongs to the active document on screen
            if (data.docname && data.docname !== frm.doc.name) {
                return; 
            }
        
            let indicator = data.indicator;
            let message = data.message || __("Sync failure without an explicit error message.");
        
            if (["green", "blue"].includes(indicator)) {
                frappe.show_alert({ message: message, indicator: indicator}, 2);
            } else {
                frappe.warn(
                    __("Smart Invoice encountered the following error:"),
                    `${message}<br>`, // Message body
                    () => {
                        // Primary Action: Redirect to the sync log document if name exists
                        frappe.set_route("Form", "Sync Request", data.name);
                    },
                    __("Open"),
                );
            }
        });
        
        // Listen for final logic execution to reload the document details
        frappe.realtime.on("reload_form", function(data) {
            // Optional verification to confirm context matches session modifier/document
            frm.reload_doc();
        });
    },
    unload: function(frm) {
        // Clean up listener when leaving the form to prevent memory leaks
        frappe.realtime.off('sync_progress');
        frappe.realtime.off('progress');
    },

});
