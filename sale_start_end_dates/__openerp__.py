# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Start End Dates',
    'version': '9.0.1.0.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': 'Adds start date and end date on sale order lines',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': ['account_invoice_start_end_dates', 'sale'],
    'data': ['views/sale_order.xml'],
    'demo': ['demo/sale_demo.xml'],
    'installable': True,
}
