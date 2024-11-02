// Copyright (c) 2024, Bantoo and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sync Request", {
	refresh(frm) {
        // frm.add_custom_button("Sync", () => {
        //     frappe.call({
        //         method: 'smart_invoice_api.smart_invoice_api.doctype.sync_request.sync_attempt.sync_attempt',
        //         args: {
        //             docname: frm.doc.name
        //         }
        //     });
        // });
        // reset attempts
        frm.add_custom_button("Reset Attempt", () => {
            frm.set_value('attempts', 0); 
        });
	},
    attempts(frm) {
        // Alert Admins after 6 tries
        if(frm.doc.attempts > 6){
            //function to alert admins
            frappe.throw("Contacting Admins")
        }
    }
});
