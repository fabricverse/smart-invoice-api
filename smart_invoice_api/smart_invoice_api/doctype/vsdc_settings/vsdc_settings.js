// Copyright (c) 2024, Bantoo and contributors
// For license information, please see license.txt

frappe.ui.form.on("VSDC Settings", {
	refresh(frm) {
 // add button to test connection
        if (frm.doc.environment == "Sandbox"){
            frm.add_custom_button(__("Test Server Connection"), function() {
                frappe.call({
                    method: "smart_invoice_api.api.test_connection"
                })
            });
        }
	},
});
