# -*- coding: utf-8 -*-
# © 2013-2017 Camptocamp SA (Jacques-Etienne Baudoux)
# © 2014-2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)


{
    'name': 'Sale shipping info helper',
    'version': '10.0.1.0.0',
    'category': 'Sales',
    'license': 'AGPL-3',
    'summary': 'Add shipping amounts on sale order',
    'depends': ['sale', 'delivery', 'sale_order_line_price_subtotal_gross'],
    'author': 'akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'data': ['views/sale_view.xml'],
    'installable': True,
}
