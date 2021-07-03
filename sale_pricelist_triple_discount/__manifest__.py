#  Copyright (c) 2015 credativ ltd (<http://www.credativ.co.uk>)
#  Copyright (c) 2020 Simone Rubino - Agile Business Group
#  Copyright (c) 2021 Andrea Cometa - Apulia Software s.r.l.
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Pricelist Triple Discount',
    'version': '12.0.1.0.0',
    'category': 'Sale',
    'author': 'Apulia Software s.r.l., '
              'Agile Business Group, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'summary': "This module allows the user to specify all three discounts in the pricelist.",
    'license': 'AGPL-3',
    'depends': [
        'sale_triple_discount',
    ],
    'data': [
        'view/pricelist_view.xml'
    ],
    'auto_install': False,
    'installable': True,
}
