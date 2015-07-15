# -*- coding: utf-8 -*-

{
    'name': 'product_bundle',
    'category': 'Product',
    'author': 'Anybox',
    'version': '1.0',
    'sequence': 150,
    'website': 'http://anybox.fr',
    'summary': "Product bundle management",
    'description': """
Product bundle management
=========================
        """,
    'depends': [
        'sale',
    ],
    'data': [
        'views/product_bundle.xml',
    ],
    'init': [

    ],
    'test': [
    ],
    'demo': [
    ],
    'js': [
    ],
    'qweb': [
    ],
    'css': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
