# Copyright (C) 2015-Today GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Orders Mass Action",
    "version": "15.0.1.0.0",
    "author": "GRAP,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "category": "Sales",
    "summary": """
    Allows to easy mass operations on sale orders.
""",
    "depends": ["sale", "web_notify"],
    "data": [
        "security/security.xml",
        "wizards/sale_order_mass_action_view.xml",
    ],
}
