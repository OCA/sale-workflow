# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    'name': 'Sale Automatic Workflow - Payment Mode',
    'version': '10.0.1.0.2',
    'author': 'Camptocamp,Sodexis,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'category': 'Sales Management',
    'depends': [
        'sale_automatic_workflow',
        'account_payment_sale',  # oca/bank-payment
    ],
    'website': 'https://github.com/OCA/sale-workflow',
    'data': [
        'data/automatic_workflow_data.xml',
        'views/account_payment_mode_views.xml',
        'views/sale_workflow_process_view.xml',
        'views/account_invoice.xml',
    ],
    'installable': True,
    'auto_install': True,
}
