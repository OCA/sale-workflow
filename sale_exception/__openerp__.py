# -*- coding: utf-8 -*-
# © 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{'name': 'Sale Exception',
 'summary': 'Custom exceptions on sale order',
 'version': '10.0.2.0.0',
 'category': 'Generic Modules/Sale',
 'author': "Akretion, Sodexis, Camptocamp, Odoo Community Association (OCA)",
 'website': 'http://www.akretion.com',
 'depends': ['sale', 'base_exception'],
 'license': 'AGPL-3',
 'data': [
     'data/sale_exception_data.xml',
     'wizard/sale_exception_confirm_view.xml',
     'views/sale_view.xml',
 ],
 'images': [],
 'installable': True,
 }
