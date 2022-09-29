# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Orders Require PO or Sales Documentation",
    "version": "12.0.1.0.1",
    "license": "AGPL-3",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "depends": ["sale_management"],
    "data": [
        "views/res_partner_view.xml",
        "views/sale_order_view.xml",
    ],
    "auto_install": False,
    "application": False,
    "installable": True,
}
