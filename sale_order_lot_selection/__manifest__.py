# © 2015 Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Sale Order Lot Selection',
	'summary': 'Select the Lot/Serial number on Sale Order',
    'version': '11.0.1.0.0',
    'category': 'Sales Management',
    'author': 'Agile Business Group, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'license': 'AGPL-3',
    'depends': [
        'stock',
        'sale_management',
        'sale_stock',
        ],
    'data': [
        'view/sale_view.xml',
        ],
    'installable': True,
    'development_status': 'Production/Stable',
    'maintainers': []
}
