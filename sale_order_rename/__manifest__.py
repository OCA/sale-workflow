# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020-2022 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Order Rename',
    'version': '12.0.1.0.1',
    'category': 'Sales',
    'website': 'https://github.com/OCA/sale-workflow',
    'author':
        'CorporateHub, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': (
        'Allows renaming of Quotation / Sale Order'
    ),
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale_order.xml',
    ],
}
