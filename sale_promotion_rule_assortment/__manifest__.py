# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Promotion Rule Assortment',
    'summary': """
        This addon allows to reduce the appliance of a promotion rule to a
        set of products""",
    'version': '10.0.1.0.1',
    "development_status": "Beta",
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'depends': [
        'product_assortment',
        'sale_promotion_rule',
    ],
    'data': [
        'views/sale_promotion_rule.xml',
    ],
    'demo': [
        'demo/sale_promotion_rule.xml',
        'demo/sale_order.xml',
    ],
}
