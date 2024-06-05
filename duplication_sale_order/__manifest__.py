# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Order - Duplication",
    "summary": "Duplication Tools for Sale Orders with a given frequency",
    "version": "16.0.1.0.0",
    "category": "Sale",
    "author": "GRAP, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": [
        "sale_management",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/view_sale_order_duplication_wizard.xml",
        "views/action.xml",
    ],
    "installable": True,
}
