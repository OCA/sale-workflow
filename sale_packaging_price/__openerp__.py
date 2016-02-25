# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': "Sale Packaging Price",
    'category': 'Sales Management',
    'version': '8.0.1.0.0',
    'depends': ['sale_stock'],
    'data': [
        'views/product_view.xml',
        'views/sale_stock_view.xml',
        'views/sale_packaging_price_menu.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/sale_packaging_price_demo.xml',
    ],
    'author': 'Antiun Ingeniería S.L., '
              'Incaser Informatica S.L., '
              'Odoo Community Association (OCA)',
    'website': 'http://www.incaser.es',
    'license': 'AGPL-3',
    'installable': True,
}
