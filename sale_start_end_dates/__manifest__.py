# -*- coding: utf-8 -*-
# Copyright 2014-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Start End Dates',
    'version': '10.0.1.0.1',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': 'Adds start date and end date on sale order lines',
    'author': 'Akretion, Sodexis, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'depends': ['account_invoice_start_end_dates', 'sale'],
    'data': ['views/sale_order.xml'],
    'demo': ['demo/sale_demo.xml'],
    'installable': True,
}
