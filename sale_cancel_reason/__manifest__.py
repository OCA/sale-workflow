# Copyright 2013 Guewen Baconnier, Camptocamp SA
# Copyright 2019 Victor M.M. Torres, Tecnativa SL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Cancel Reason",
    "version": "12.0.1.2.0",
    "author": "Camptocamp," "Odoo Community Association (OCA)",
    "category": "Sale",
    "license": "AGPL-3",
    "complexity": "normal",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale"],
    "data": [
        "wizard/cancel_reason_view.xml",
        "view/sale_view.xml",
        "security/ir.model.access.csv",
        "data/sale_order_cancel_reason.xml",
    ],
    "auto_install": False,
    "installable": True,
}
