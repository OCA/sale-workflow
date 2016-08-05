# -*- coding: utf-8 -*-
# © initOS GmbH 2016
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Payment Method - Payment Acquirer",
    "version": "8.0.1.0.0",
    "depends": ["payment",
                "sale_payment_method",
                "sale",
                "website_sale",
                ],
    'author': 'initOS GmbH, Odoo Community Association (OCA)',
    "category": "",
    "summary": "",
    'license': 'AGPL-3',
    'data': ['payment_method_view.xml',
             'payment_acquirer_view.xml',
             'sale_view.xml',
             ],
    'images': [],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
