# -*- coding: utf-8 -*-
# © 2016 Dreambits Technologies (http://www.dreambits.in)
# @author Karan Shah <admin@dreambits.in>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Procurement After Payment',
    'version': '9.0.1.0.0',
    'website': 'https://www.dreambits.in/',
    'category': 'Sales',
    'depends': ['procurement', 'sale_stock'],
    'license': 'AGPL-3',
    'author': 'Dreambits Technologies, Odoo Community Association (OCA)',
    'data': [
        'security/sale_security.xml',
        'data/sale_procurement_scheduler.xml',
        'views/config_view.xml',
        'views/product_view.xml',
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'auto_install': True,
}
