# -*- coding: utf-8 -*-
# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale product set variants',
    'category': 'Sale',
    'license': 'AGPL-3',
    'author': 'Camptocamp SA, Odoo Community Association (OCA)',
    'version': '10.0.1.0.0',
    'sequence': 150,
    'website': 'https://github.com/OCA/sale-workflow',
    'summary': "Sale product set variants",
    'depends': [
        'sale_product_set',
    ],
    'data': [
        'views/product_set.xml',
        'wizard/product_set_add.xml',
    ],
    'demo': [
        'demo/product_set.xml',
    ],
    'installable': True,
    'application': False,
}
