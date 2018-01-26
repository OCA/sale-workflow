# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Credit Points',
    'version': '11.0.1.0.0',
    'category': 'Sales',
    'license': 'AGPL-3',
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'website': 'http://www.camptocamp.com/',
    'depends': [
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'data/res_currency.xml',
        'views/partner.xml',
        'views/point_history.xml',
        'wizards/manage_credit_point.xml',
    ],
}
