# -*- coding: utf-8 -*-
# © 2014 Today Akretion (http://www.akretion.com).
# @author David BEAL <david.beal@akretion.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'sale_order_lot_mrp',
    'version': '10.0.1.0.0',
    'category': 'Generic Modules',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'license': 'AGPL-3',
    'depends': [
        'mrp_production_note',
        'sale_order_lot_generator',
    ],
    'data': [
        'views/mrp_view.xml',
    ],
    'installable': True,
}
