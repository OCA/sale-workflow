# -*- coding: utf-8 -*-
# © 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
# © 2013 Camptocamp SA (author: Guewen Baconnier)
# © 2016 Sodexis
# © 2017 Hucke Media GmbH & Co. KG/IFE GmbH (author: Hamza Talibi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Automatic Workflow',
    'version': '11.0.1.0.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'author': "Akretion,Camptocamp,Sodexis,Hucke Media GmbH & Co. KG/IFE GmbH, Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com/',
    'depends': ['sale_stock', 'sales_team','sale_management','sale'
                ],
    'data': ['views/sale_view.xml',
             'views/sale_workflow_process_view.xml',
             'data/automatic_workflow_data.xml',
             'security/ir.model.access.csv',
             ],
    'installable': True,
}
