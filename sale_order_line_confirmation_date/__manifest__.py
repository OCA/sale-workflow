# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Order Line Confirmation Date',
    'summary': """
        Adds the confrmation date on order lines""",
    'version': '10.0.1.0.1',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'depends': [
        'sale',
    ],
    'external_dependencies': {'python': ['openupgradelib']},
    'pre_init_hook': 'pre_init_hook',
}
