# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Serial Numbers",
    "version": "14.0.1.0.0",
    "category": "Sale",
    "depends": ["sale_stock"],
    "author": "Open Source Integrators," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "description": "Adds mechanism for creating serial numbers on sales order lines.",
    "website": "https://github.com/OCA/sale-workflow",
    "data": [
        "security/ir.model.access.csv",
        "wizard/sale_order_line_from_stock_views.xml",
        "data/stock_data.xml",
        "views/partner_views.xml",
        "views/product_views.xml",
        "views/sale_views.xml",
        "views/sequence_views.xml",
    ],
    "installable": True,
    "application": False,
}
