# -*- coding: utf-8 -*-
{
    'name': 'Product Pack',
    'version': '1.0',
    'category': 'Product',
    'sequence': 14,
    'summary': '',
    'description': """
Product Pack
============
# TODO agregar automaticamente a grupo employee el grupo nuevo cread
    """,
    'author':  'Ingenieria ADHOC',
    'website': 'www.ingadhoc.com',
    'images': [
    ],
    'depends': [
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/product_security.xml',
        'pack_view.xml',
        'sale_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
