# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Product Price History',
    'summary': 'Record cost and sale prices of products',
    'version': '11.0.1.0.0',
    'category': 'Sales',
    'website': 'https://github.com/OCA/sale-workflow',
    'license': 'AGPL-3',
    'author': 'Domatix,Odoo Community Association (OCA)',
    'depends': [
        'sale',
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_lst_price_history_view.xml',
        'views/product_price_history_view.xml',
        'views/product_template_view.xml',
    ],
    'installable': True,
}
