# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Substitute Product for Online Proposals',
    'summary': 'Allows to change products by others recommended via web.',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Domatix, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'category': 'Sale',
    'depends': ['website_quote'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/website_quote_templates.xml'
        ],
    'installable': True,
}
