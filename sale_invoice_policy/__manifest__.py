# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Sale invoice Policy",
    'description': """
        Sales Management: let the user choose the invoice policy on the
        order""",
    'author': 'ACSONE SA/NV, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'category': 'Sales Management',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'sale',
        'sale_stock',
    ],
    'data': [
        'wizards/res_config_view.xml',
        'views/product_template_view.xml',
        'views/sale_view.xml',
    ],
    'post_init_hook': 'post_init_hook',
}
