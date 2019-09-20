# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Partner picking policy",
    'summary': """Set the picking policy on the partner""",
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': "https://github.com/OCA/sale-workflow",
    'category': 'Sales',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'sale_stock',
    ],
    'data': [
        'views/res_partner.xml',
    ],
}
