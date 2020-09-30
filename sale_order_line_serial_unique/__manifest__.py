# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Order Line Serial Unique',
    'summary': """
        Restrict the usage of unique quantity of product per line
        if product tracking is serial""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'maintainers': ['rousseldenis'],
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'depends': [
        "sale_stock",
    ],
}
