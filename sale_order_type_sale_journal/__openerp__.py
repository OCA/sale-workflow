# -*- coding: utf-8 -*-
# Copyright 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order Types - Invoicing Journals",
    "summary": "Link module between sale_order_type and sale_journal",
    "version": "8.0.1.0.0",
    'category': 'Hidden',
    "website": "https://www.agilebg.com",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'auto_install': True,
    "depends": [
        "sale_journal",
        "sale_order_type",
    ],
    "data": [
        "views/sale_order_type_view.xml",
    ],
}
