# Copyright 2019 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Stock Picking Blocking",
    "summary": "Allow you to block the creation of deliveries " "from a sale order.",
    "version": "14.0.1.1.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "depends": ["sale_stock"],
    "data": [
        "security/ir.model.access.csv",
        "security/sale_stock_picking_blocking_security.xml",
        "data/sale_stock_picking_blocking_data.xml",
        "views/sale_stock_picking_blocking_reason_view.xml",
        "views/sale_order_view.xml",
        "views/res_partner_view.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
