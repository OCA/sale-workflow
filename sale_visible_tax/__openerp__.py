# -*- coding: utf-8 -*-
# Copyright (C) 2014-Today: Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Order Line and Invoice Line - Visible Tax',
    'version': '8.0.1.0.0',
    'author': "Akretion,GRAP,Odoo Community Association (OCA)",
    'website': 'www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Sale',
    'depends': [
        'sale',
    ],
    'data': [
        'views/view_sale_order.xml',
        'views/view_account_invoice.xml',
    ],
    'installable': True,
}
