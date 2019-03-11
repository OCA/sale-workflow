# -*- coding: utf-8 -*-
# Copyright 2016 Cédric Pigeon, ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Sale Product Multi Add",
    'summary': """
        Sale Product Multi Add """,
    'author': 'ACSONE SA/NV, Odoo Community Association (OCA)',
    'website': "http://acsone.eu",
    'category': 'Sale Management',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'sale',
    ],
    'data': [
        'wizards/sale_import_products_view.xml',
        'views/sale_view.xml',
    ],
}
