# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Sales Order line description',
    'summary': """
        Allows to remove the product name and Internal reference from the Sales Order Description""",
    'version': '11.0.1.0.0',
    'category': 'Generic Modules/Sale',
    'author':   "Magboard LLC, "                
                "Odoo Community Association (OCA)",    
    'license': 'AGPL-3',
    "depends": [
        'sale',
    ],
    "data": [
        'security/order_line_security.xml',
        'views/res_config_view.xml',
    ],
    'installable': True,
}
