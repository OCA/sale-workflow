# -*- coding: utf-8 -*-
# © 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "sale_order_partial_advance",
    'summary': """
        Sale Order Partial Advance """,
    'author': 'ACSONE SA/NV, Odoo Community Association (OCA)',
    'website': "http://acsone.eu",
    'category': 'Sales Management',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'sale',
    ],
    'data': [
        'data/product_data.xml',
        'wizard/sale_line_invoice.xml',
    ],
}
