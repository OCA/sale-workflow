# -*- coding: utf-8 -*-

{
    'name': 'sale_product_bundle',
    'category': 'Sale',
    'author': 'Anybox',
    'version': '1.0',
    'sequence': 150,
    'website': 'http://anybox.fr',
    'summary': "Sale product bundle",
    'depends': [
        'sale',
    ],
    'data': [
        'views/product_bundle.xml',
        'views/sale_order.xml',
        'wizard/sale_order_bundle.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
