# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Sale Merge Draft Invoice",
    "author": "Eficent, Odoo Community Association (OCA)",
    "version": "12.0.1.0.0",
    "category": "Sale Workflow",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        'sale_order_action_invoice_create_hook',
    ],
    "data": [
        'security/sale_merge_draft_invoice_security.xml',
        'wizard/sale_make_invoice_advance_views.xml',
        'view/res_config_settings_views.xml',
    ],
    "license": 'LGPL-3',
    "installable": True
}
