# -*- coding: utf-8 -*-
# © 2015 Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale Order Lot Selection',
    'version': '10.0.1.0.1',
    'category': 'Sales Management',
    'author': "Odoo Community Association (OCA), Agile Business Group",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    'depends': ['sale_stock', 'procurement'],
    'data': [
        'view/sale_order_views.xml',
        'view/procurement_order_views.xml'
    ],
    'installable': True,
}
