# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Rental',
    'version': '9.0.1.0.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': 'Manage Rental of Products',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': ['sale_start_end_dates', 'sale_stock'],
    'data': [
        'data/rental_data.xml',
        'views/sale_order.xml',
        'views/stock.xml',
        'views/sale_rental.xml',
        'wizard/create_rental_product_view.xml',
        'views/product.xml',
        'security/ir.model.access.csv',
        'security/sale_rental_security.xml',
    ],
    'demo': ['demo/rental_demo.xml'],
    'installable': True,
}
