# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Sale product set',
    'summary': "Sale product set",
    'version': '9.0.1.0.1',
    'category': 'Sales',
    "website": "https://odoo-community.org/",
    'author': 'Anybox, Odoo Community Association (OCA)',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
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
}
