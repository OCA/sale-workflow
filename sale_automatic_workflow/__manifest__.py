# -*- coding: utf-8 -*-
# © 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
# © 2013 Camptocamp SA (author: Guewen Baconnier)
# © 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Automatic Workflow',
    'version': '10.0.1.0.1',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'author': "Akretion,Camptocamp,Sodexis,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com/',
    'depends': ['sale_stock', 'sales_team',
                ],
    'data': ['views/sale_view.xml',
             'views/sale_workflow_process_view.xml',
             'data/automatic_workflow_data.xml',
             'security/ir.model.access.csv',
             ],
    'installable': True,
}
