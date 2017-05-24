# -*- coding: utf-8 -*-
# Copyright 2014-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Rental',
    'version': '10.0.1.0.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': 'Manage Rental of Products',
    'author': 'Akretion, Sodexis, Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': ['sale_start_end_dates', 'sale_stock', 'sales_team'],
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
    'post_init_hook': 'add_users_to_group_mrp_properties',
    'demo': ['demo/rental_demo.xml'],
    'installable': True,
}
