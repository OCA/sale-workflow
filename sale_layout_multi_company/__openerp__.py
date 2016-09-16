# -*- coding: utf-8 -*-
# Copyright 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Layout - Multi company",
    "summary": "Multi company features for sale_layout",
    "version": "8.0.1.0.0",
    "category": "Sale",
    "website": "https://www.agilebg.com",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_layout",
    ],
    "data": [
        "views/sale_layout_view.xml",
        "security/record_rules.xml",
    ],
}
