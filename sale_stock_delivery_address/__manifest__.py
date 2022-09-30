# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Sale Stock Sourcing Address",
    "version": "11.0.1.1.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales Management",
    "license": "LGPL-3",
    "depends": [
        "sale_stock",
        "sale_procurement_group_by_line",
    ],
    "data": [
        "views/sale_order_view.xml",
        "views/res_partner_view.xml",
    ],
    "installable": True,
}
