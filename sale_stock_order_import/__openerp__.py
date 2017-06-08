# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Stock Order Import',
    'version': '8.0.1.0.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': 'Glue module between sale_stock and sale_order_import',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': [
        'sale_stock',
        'sale_order_import',
        'base_business_document_import_stock',
        ],
    'data': [],
    'installable': True,
    'auto_install': True,
}
