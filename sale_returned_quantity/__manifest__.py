# -*- coding: utf-8 -*-
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Order Returned Qty",
    "version": "10.0.1.0.0",
    "author": "Eficent,"
              "Odoo Community Association (OCA)",
    "website": "https://odoo-community.org/",
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": [
        "sale_stock",
    ],
    "data": [
        "views/sale_order_view.xml",
        "wizards/sale_procurement_wizard_view.xml",
    ],
    "installable": True,
}
