# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# © 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl

{
    'name': "Sale Packaging Price",
    'category': 'Sales Management',
    'version': '9.0.1.0.0',
    'depends': ['sale_stock'],
    'data': [
        'views/product_view.xml',
        'views/sale_order_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/sale_packaging_price_demo.xml',
    ],
    'author': 'Antiun Ingeniería S.L., '
              'Incaser Informatica S.L., '
              'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'license': 'LGPL-3',
    'installable': False,
}
