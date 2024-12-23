// Copyright (c) 2024, Bantoo and contributors
// For license information, please see license.txt

frappe.ui.form.on("VSDC Settings", {
	refresh(frm) {
 // add button to test connection
        // if (frm.doc.environment == "Sandbox"){
        if (!frm.doc.__islocal){
            frm.add_custom_button(__("Connection Test"), function() {
                frappe.call({
                    method: "smart_invoice_api.api.test_connection"
                })
            }, __("Menu"));
            frm.page.get_inner_group_button("Menu")
                .find("button")
                .removeClass("btn-default")
                .addClass("btn-info");
        // }
        }
	},
});
