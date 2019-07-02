# coding: utf-8
# © 2015 Akretion, Valentin CHEMIERE <valentin.chemiere@akretion.com>
# © 2017 Akretion, David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Line Option',
    'version': '10.0.0.1.1',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'website': 'www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Sale',
    'depends': [
        'sale_order_lot_mrp',
    ],
    'data': [
        'views/sale_view.xml',
        'views/mrp_view.xml',
        'views/stock_view.xml',
        'views/install.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/config.yml',
        'demo/product_demo.xml',
    ],
    'installable': True,
}
