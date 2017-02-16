# coding: utf-8
#   @author Valentin CHEMIERE <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'sale_order_lot_generator',
    'version': '10.0.0.0.1',
    'author': 'Akretion',
    'website': 'www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Sale',
    'depends': [
        'sale_order_lot_selection',
    ],
    'data': [
        'views/product_view.xml',
    ],
    'installable': True,
}
