# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Product Country Restriction',
    'summary': """
        Implements product country restrictions on sale workflow""",
    'version': '10.0.1.1.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'depends': [
        'sale',
        'sales_team',
        'product_country_restriction',
    ],
    'data': [
        'security/sale_product_country_restriction.xml',
        'views/sale_menus.xml',
        'views/sale_order.xml',
        'views/sale_config_settings.xml',
    ],
}
