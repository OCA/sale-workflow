# -*- coding: utf-8 -*-
#
#
# Copyright Camptocamp SA
# author nbessi
#
#
{"name": "Sale/invoice condition",
 "version": "1.3",
 "depends": ["sale", "account"],
 "description": """Adds predefine header and footer text on sale order and
     invoice.
Texts are passed in the invoice when sale order is transformed into invoice""",
 "website": "https://github.com/OCA/sale-workflow",
 "author": "Camptocamp,Odoo Community Association (OCA)",
 "init_xml": [],
 "update_xml": ["account_invoice_view.xml",
                "sale_order_view.xml",
                "condition_view.xml"],
 "category": "Sale",
 "installable": False,
 "active": False, }
