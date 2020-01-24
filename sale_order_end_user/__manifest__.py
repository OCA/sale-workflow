# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Order End User',
    'summary': """
        Allows to define the end user in sale orders if there is an
        intermediate between shipping and this end user""",
    'version': '10.0.1.1.0',
    'license': 'AGPL-3',
    'development_status': 'Beta',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow/',
    'depends': [
        'sale',
        'partner_contact_type_end_user',
    ],
    'data': [
        'views/sale_order.xml',
    ],
}
