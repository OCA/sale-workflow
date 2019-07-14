# Copyright 2014-2019 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016-2019 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Rental',
    'version': '12.0.1.0.0',
    'category': 'Sales',
    'license': 'AGPL-3',
    'summary': 'Manage Rental of Products',
    'author': 'Akretion, Sodexis, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'depends': ['sale_start_end_dates', 'sale_stock', 'sales_team'],
    'data': [
        'data/rental_data.xml',
        'views/sale_order.xml',
        'views/stock_warehouse.xml',
        'views/sale_rental.xml',
        'wizard/create_rental_product_view.xml',
        'views/product.xml',
        'security/ir.model.access.csv',
        'security/sale_rental_security.xml',
    ],
    'post_init_hook': 'add_to_group_stock_packaging',
    'demo': ['demo/rental_demo.xml'],
    'installable': True,
}
