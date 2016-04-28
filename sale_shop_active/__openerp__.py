# -*- coding: utf-8 -*-
# © 2016 Thomas Rehn (initOS GmbH)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Shop Active Flag",
    "version": "7.0.1.0.0",
    "depends": [
        'sale',
    ],
    'author': 'initOS GmbH, Odoo Community Association (OCA)',
    "category": "",
    "summary": "Adds active flag to shops",
    'license': 'AGPL-3',
    "description": """
Sale Shop Active Flag
=====================

This module adds an *active* flag to the shop object. This can be used
 to hide a shop without deleting it.
    """,
    'data': [
        'views/sale_shop_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
