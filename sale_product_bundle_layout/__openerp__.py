# -*- coding: utf-8 -*-
{
    'name': 'sale_product_bundle_layout',
    'category': 'Sale',
    'author': 'Anybox',
    'version': '1.0',
    'sequence': 150,
    'website': 'http://anybox.fr',
    'summary': "Sale product bundle layout",
    'depends': [
        'sale_product_bundle',
        'sale_layout',
    ],
    'data': [
        'views/product_bundle.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
