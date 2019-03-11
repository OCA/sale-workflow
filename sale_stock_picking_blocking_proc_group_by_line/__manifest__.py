# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Stock Picking Blocking Procurement Group By Line",
    "summary": "Module that allows module sale_delivery_block to work with "
               "sale_procurement_group_by_line",
    "version": "10.0.1.0.0",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "depends": [
        "sale_procurement_group_by_line",
        "sale_stock_picking_blocking",
    ],
    "auto_install": True,
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
