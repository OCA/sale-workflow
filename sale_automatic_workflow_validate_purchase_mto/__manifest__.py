# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Automatic Workflow Validate Purchase Mto',
    'summary': """
        When a sale order generates directly a purchase order,
        validates it automatically""",
    'version': '10.0.1.0.1',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/sale-workflow',
    'depends': [
        'purchase',
        'stock',
        'sale_automatic_workflow'
        ],
    'data': [
        'views/sale_workflow_process.xml',
        'data/automatic_workflow.xml',
    ],
}
