# Copyright 2020 Commown SCIC SAS (https://commown.fr)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Sale product email',
    'category': 'Sales',
    'summary': "Send a product-specific email to its buyers",
    'version': '12.0.1.0.0',
    'author': "Commown SCIC SAS, Akretion, Odoo Community Association (OCA)",
    'license': "AGPL-3",
    'website': "https://github.com/OCA/sale-workflow",
    'data': [
        'data/sale_order_actions.xml',
        'views/product_template.xml',
    ],
    'depends': [
        'product',
    ],
    'installable': True,
}
