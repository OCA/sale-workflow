# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

{
    'name': 'Default route per partner',
    'version': '12.0.1.0.0',
    'category': 'Sales Management',
    'license': 'LGPL-3',
    'summary': "Set the customer preferred route on partner",
    'author': "Opener B.V.,Odoo Community Association (OCA)",
    'website': 'https://github.com/oca/sale-workflow',
    'depends': [
        'sale_stock'
    ],
    'data': [
        'views/res_partner.xml',
    ],
    'installable': True,
}
