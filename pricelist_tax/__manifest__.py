# coding: utf-8
# Copyright (c) 2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Pricelist Tax',
    'version': '10.0.1.0.0',
    'category': 'Sale',
    'author': 'Akretion',
    'depends': [
        'sale',
        'l10n_fr',
        'onchange_helper',
    ],
    'website': 'http://www.akretion.com/',
    'data': [
        'views/pricelist_view.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
}
