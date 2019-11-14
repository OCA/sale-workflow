# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Wishlist',
    'summary': """
        Handle sale wishlist for partners""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Camptocamp SA,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'depends': [
        'sale_product_set',
    ],
    'data': [
        'views/product_set.xml',
        'views/partner.xml',
    ],
}
