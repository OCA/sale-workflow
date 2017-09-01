# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Fixed Discount",
    "summary": "Allows to apply fixed amount discounts in sales orders.",
    "version": "9.0.1.0.0",
    "category": "Sales",
    "website": "https://odoo-community.org/",
    "author": "Eficent, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale", "account_invoice_fixed_discount"
    ],
    "data": [
        "views/sale_order_view.xml",
        "reports/report_sale_order.xml",
    ],
}
