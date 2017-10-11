# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Sale Merge Draft Invoice",
    "author": "Eficent, Odoo Community Association (OCA)",
    "version": "10.0.1.0.0",
    "category": "Sale Workflow",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        'sale_order_action_invoice_create_hook',
    ],
    "data": [
        'wizard/sale_make_invoice_advance_views.xml',
        'security/sale_merge_draft_invoice_security.xml',
        'view/sale_config_settings_views.xml',
    ],
    "license": 'LGPL-3',
    "installable": True
}
