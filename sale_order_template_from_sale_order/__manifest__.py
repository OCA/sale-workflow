# Copyright 2026 Cetmix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Order Template from Sale Order",
    "summary": "Save a quotation or sales order as a sale order template",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["sale_management"],
    "data": [
        "security/sale_order_template_security.xml",
        "security/ir.model.access.csv",
        "wizard/sale_order_create_template_views.xml",
        "views/sale_order_views.xml",
        "views/sale_order_template_views.xml",
    ],
    "demo": [
        "demo/res_groups_demo.xml",
    ],
    "installable": True,
}
