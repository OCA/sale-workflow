# -*- coding: utf-8 -*-
# © initOS GmbH 2016
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{'name': 'Sale Payment Method - Hold Pickings (until payment)',
 'version': '8.0.1.0.0',
 'category': 'Warehouse',
 'description': """
 Sale Payment Method - Hold Pickings (until payment)
 ===================================================
 * This module allows to hold the picking until the invoice is paid
     """,
 'depends': ['stock',
             'sale',
             'sale_payment_method_automatic_workflow',
             ],
 'author': "initOS GmbH, Odoo Community Association (OCA)",
 'license': 'AGPL-3',
 'data': ['views/stock.xml',
          'views/payment_method.xml',
          ],
 'installable': True,
 'application': False,
 }
