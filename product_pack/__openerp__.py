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
# TODO agregar en configuracion si se quiere usar los sale order packs (seria para el group group_pack) y ver que se haga visible la vista form
# TODO implementar totalice en price get
# TODO agregar constraint de no pack dentro de pack
# TODO calcular correctamente pack virtual available para negativos
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
