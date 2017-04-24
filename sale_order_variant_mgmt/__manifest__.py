# -*- coding: utf-8 -*-
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Handle easily multiple variants on Sales Orders',
    'summary': 'Handle the addition/removal of multiple variants from '
               'product template into the sales order',
    'version': '10.0.1.0.0',
    'author': 'Tecnativa,'
              'Odoo Community Association (OCA)',
    'category': 'Sale',
    'license': 'AGPL-3',
    'website': 'https://www.tecnativa.com',
    'depends': [
        'sale',
        'web_widget_x2many_2d_matrix',
    ],
    'demo': [],
    'data': [
        'wizard/sale_manage_variant_view.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
}
