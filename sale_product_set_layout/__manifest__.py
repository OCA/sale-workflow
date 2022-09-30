# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Sale product set layout',
    'category': 'Sale',
    'author': 'Anybox, Odoo Community Association (OCA)',
    'version': '10.0.1.0.1',
    'license': 'AGPL-3',
    'sequence': 150,
    'website': 'https://github.com/OCA/sale-workflow',
    'summary': "Sale product set layout",
    'depends': [
        'sale_product_set',
    ],
    'data': [
        'views/product_set.xml',
        'security/groups.xml',
    ],
    'demo': [
        'demo/product_set.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
