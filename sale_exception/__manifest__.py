# Copyright 2011 Akretion, Camptocamp, Sodexis
# Copyright 2018 Akretion, Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Exception',
    'summary': 'Custom exceptions on sale order',
    'version': '11.0.1.0.0',
    'category': 'Generic Modules/Sale',
    'author': "Akretion, "
              "Sodexis, "
              "Camptocamp, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/sale-workflow',
    'depends': ['sale', 'base_exception'],
    'license': 'AGPL-3',
    'data': [
        'data/sale_exception_data.xml',
        'wizard/sale_exception_confirm_view.xml',
        'views/sale_view.xml',
    ],
}
