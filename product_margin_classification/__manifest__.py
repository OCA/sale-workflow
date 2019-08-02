# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Product Margin Classification',
    'version': '10.0.1.0.0',
    'category': 'Account',
    'author': 'GRAP,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'sale',
        'sales_team',
    ],
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'data/decimal_precision.xml',
        'views/action.xml',
        'views/menu.xml',
        'views/view_product_template.xml',
        'views/view_product_margin_classification.xml',
    ],
    'demo': [
        'demo/res_groups.xml',
        'demo/product_margin_classification.xml',
        'demo/product_template.xml',
    ],
    'installable': True,
}
