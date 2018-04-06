# -*- coding: utf-8 -*-
# © 2015 Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Sale Order Lot Selection',
    'version': '11.0.1.0.0',
    'category': 'Sales Management',
    'author': "Odoo Community Association (OCA), Agile Business Group",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    'depends': [
        'stock',
        'sale_management',
        'sale_stock',
        ],
    'data': [
        'view/sale_view.xml',
        ],
    'installable': True,
}
