# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Group procurements by requested date",
    "summary": "Groups pickings based on requested date of order line",
    "version": "10.0.1.0.0",
    "category": "Sales Management",
    'website': "https://github.com/OCA/sale-workflow",
    "author": "Eficent , "
              "SerpentCS,"
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "sale_order_line_date",
        "sale_procurement_group_by_line",
    ],
    "installable": True,
}
