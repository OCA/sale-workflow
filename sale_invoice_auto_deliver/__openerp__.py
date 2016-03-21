# -*- coding: utf-8 -*-
# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Invoice Automatic Deliver",
    "version": "8.0.1.0.0",
    'author': "Acsone SA/NV,Odoo Community Association (OCA)",
    "category": "Sales Management",
    "website": "http://www.acsone.eu",
    "depends": ["sale",
                "sale_stock",
                "stock",
                ],
    "data": ["views/sale_line_invoice_views.xml"],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
