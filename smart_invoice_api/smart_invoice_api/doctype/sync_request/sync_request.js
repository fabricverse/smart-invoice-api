// Copyright (c) 2024, Bantoo and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sync Request", {
	refresh(frm) {
        let invoice_endpoint = ["/trnsSales/saveSales", "/trnsPurchase/savePurchase"].includes(frm.doc.endpoint)
        if ((frm.doc.status !== "Success" && !invoice_endpoint) || (!["Success", "Error"].includes(frm.doc.status) && invoice_endpoint)){
            let sync = frm.add_custom_button("Retry Sync", () => {
                frappe.call({
                    method: 'sync',
                    doc: frm.doc,
                    callback: (r=> {
                        frm.reload_doc()
                    })
                });

                frappe.show_alert({
                    message:__('Synchronizing ...'),
                    indicator:'green'
                }, 3);
            });

            sync.removeClass('btn-default').addClass('btn-success');
        }
        
        if (frm.doc.status !== "Success"){
            // reset attempts
            frm.add_custom_button("Reset", () => {
                frm.set_value('attempts', 1); 
                frm.set_value('status', "New"); 
                frm.save();
                frm.refresh_field('attempts');
                frm.refresh_field('status');
            });
        }
	}
});
