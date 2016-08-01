# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Group procurements by requested date",
    "summary": "Groups pickings based on requested date of order line",
    "version": "8.0.0.0.1",
    "category": "Sales Management",
    "website": "http://www.eficent.com",
    "author": "Eficent, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_order_line_dates",
        "sale_procurement_group_by_line",
        "sale_sourced_by_line"
    ],
}
