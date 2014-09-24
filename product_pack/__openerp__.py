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
Allows configuring products as a collection of other products. If such a product is added in a sale order, all the products of the pack will be added automatically (when storing the order) as children of the pack product.

The module has been made compatible with nan_external_prices and containts code to specifically handle when the module is available but they're still independent and there are no dependencies between them.
    """,
    'author':  'Ingenieria ADHOC',
    'website': 'www.ingadhoc.com',
    'images': [
    ],
    'depends': [
        'sale',
        'stock',
    ],
    'data': [
		'security/ir.model.access.csv',
		'pack_view.xml'
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': False,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: