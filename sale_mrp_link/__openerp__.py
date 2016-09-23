# -*- coding: utf-8 -*-
# Copyright (C) 2016  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Sale MRP Link',
    'version': '9.0.1.0.0',
    'category': 'Generic Modules',
    'author': 'Akretion',
    'website': 'http://akretion.com',
    'license': 'AGPL-3',
    'depends': ['sale_stock', 'mrp'],
    'data': [
        'mrp_view.xml',
        'sale_view.xml',
        ],
    'installable': True,
}
