# -*- coding: utf-8 -*-
# © 2013-2017 Camptocamp SA (Jacques-Etienne Baudoux)
# © 2014-2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)


{
    'name': 'Default Quotation Validity',
    'version': '9.0.1.0.0',
    'category': 'Sales',
    'license': 'AGPL-3',
    'summary': 'Set a default validity delay on quotations',
    'depends': ['sale'],
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'website': 'http://www.camptocamp.com',
    'data': [
        'views/res_company_view.xml',
        'views/sale_order_view.xml'
    ],
    'installable': True,
}
