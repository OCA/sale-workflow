# -*- coding: utf-8 -*-
# Copyright 2015 Anybox
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Sale product set',
    'category': 'Sale',
    'license': 'AGPL-3',
    'author': 'Anybox, Odoo Community Association (OCA)',
    'version': '10.0.1.0.2',
    'website': 'https://github.com/OCA/sale-workflow',
    'summary': "Sale product set",
    'depends': [
        'sale',
    ],
    'data': [
        'views/product_set.xml',
        'wizard/product_set_add.xml',
        'views/sale_order.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/product_set.xml',
        'demo/product_set_line.xml',
    ],
    'installable': True,
}
