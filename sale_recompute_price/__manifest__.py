# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Recompute Prices',
    'version': '12.0.1.0.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': "Recompute prices by updating each sale lines",
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'https://github.com/oca/sale-workflow',
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale.xml',
    ],
    'installable': True,
}
