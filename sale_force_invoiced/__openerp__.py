# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Force Invoiced',
    'summary': 'Allows to force the invoice status of the sales order to '
               'Invoiced',
    'version': '9.0.1.0.0',
    "author": "Eficent,"
              "Odoo Community Association (OCA)",
    'category': 'sale',
    'license': 'AGPL-3',
    'website': "https://github.com/OCA/sale-workflow",
    'depends': ['sale'],
    'data': [
        'view/sale_view.xml'
    ],
    'installable': True,
}
