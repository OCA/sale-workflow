# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{'name': 'Sale Automatic Workflow - Payment Mode',
 'version': '9.0.1.0.0',
 'author': 'Camptocamp,Odoo Community Association (OCA)',
 'license': 'AGPL-3',
 'category': 'Sales Management',
 'depends': ['sale_automatic_workflow',
             'account_payment_sale',  # oca/bank-payment
             ],
 'website': 'http://www.camptocamp.com',
 'data': ['views/account_payment_mode_views.xml',
          ],
 'installable': True,
 'auto_install': True,
 }
