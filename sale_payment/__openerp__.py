# -*- coding: utf-8 -*-
# Copyright (C) 2016  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Sale Payment',
    'version': '9.0.1.0.0',
    'category': 'Sales Management',
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com',
    'license': 'AGPL-3',
    'depends': ['sale'],
    'data': [
        'view/sale_view.xml',
        'view/statement_view.xml'
    ],
    'installable': True,
}
