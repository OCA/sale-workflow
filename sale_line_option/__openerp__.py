# coding: utf-8
# © 2015 Akretion, Valentin CHEMIERE <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Line Option',
    'version': '8.0.0.0.1',
    'author': 'Akretion',
    'website': 'www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Sale',
    'depends': [
        'sale_order_lot_mrp',
    ],
    'data': [
        'views/sale_view.xml',
        'views/mrp_view.xml',
        'views/install.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/product_demo.xml',
        'demo/config.yml',
    ],
    'installable': True,
}
