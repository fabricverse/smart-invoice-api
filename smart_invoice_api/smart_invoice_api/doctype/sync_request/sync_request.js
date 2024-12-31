// Copyright (c) 2024, Bantoo and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sync Request", {
	refresh(frm) {
        frm.add_custom_button("Sync", () => {
            frappe.call({
                method: 'on_update',
                self: frm.doc
            });
        });
        
        // reset attempts
        frm.add_custom_button("Reset", () => {
            frm.set_value('attempts', 0); 
            frm.refresh_field('attempts');
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
