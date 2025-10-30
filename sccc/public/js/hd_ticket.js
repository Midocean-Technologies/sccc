frappe.ui.form.on("HD Ticket", {
    refresh(frm) {
        if(frm.doc.status == "Open"){
        frm.add_custom_button(__('Create Site'), function() {

            let d = new frappe.ui.Dialog({
                title: 'Create Site',
                size: 'small',
                fields: [
                    {
                        label: 'Email',
                        fieldname: 'email',
                        fieldtype: 'Data',
                        reqd: 1
                    },
                    {
                        label: 'Full Name',
                        fieldname: 'full_name',
                        fieldtype: 'Data',
                        reqd: 1
                    },
                    {
                        label: 'Site Name',
                        fieldname: 'site_name',
                        fieldtype: 'Data',
                        reqd: 1
                    },
                    {
                        label: 'Plan',
                        fieldname: 'plan',
                        fieldtype: 'Link',
                        options: 'Role Profile',
                        reqd: 1,
                        get_query: function() {
                            return {
                                filters: {
                                    name: ["in", ["Essential", "Pro", "Ultimate"]]
                                }
                            };
                        }
                    }
                ],
                primary_action_label: 'Create',
                primary_action(values) {
                    if (!values.email || !values.full_name || !values.site_name || !values.plan) {
                        frappe.msgprint(__('Please fill all required fields.'));
                        return;
                    }

                    frappe.call({
                        method: "sccc.api.create_site_from_hd_ticket",
                        args: {
                            ticket: frm.doc.name,
                            email: values.email,
                            plan: values.plan,
                            site_name: values.site_name,
                            full_name: values.full_name,
                        },
                        freeze: true,
                        freeze_message: __("Creating site..."),
                        callback: function(r) {
                            if (!r.exc) {
                                frappe.msgprint(__('Site created successfully!'));
                                d.hide();
                                frm.reload_doc();
                            } else {
                                frappe.msgprint(__('Failed to create site. Check the server logs.'));
                            }
                        }
                    });
                }
            });

            d.show();

        })
        .removeClass("btn-default")
        .addClass("btn-primary")
        .css({
            'color': 'white',
            'font-weight': 'bold'
        });
        }
    }
});
