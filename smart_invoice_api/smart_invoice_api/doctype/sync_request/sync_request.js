// Copyright (c) 2024, Bantoo and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sync Request", {
	refresh(frm) {
        let attempts = 0;
        // increment attempts after sync attempt
        frm.add_custom_button("Sync", () => {
            attempts += 1;
            frm.set_value('attempts', attempts); 
        })
        // reset attempts
        frm.add_custom_button("Reset Attempt", () => {
            frm.set_value('attempts', 0); 
        })
	},
    attempts(frm) {
        // Alert Admins after 6 tries
        if(frm.doc.attempts > 6){
            //function to alert admins
            frappe.throw("Contacting Admins")
        }
    }
});
