# -*- coding: utf-8 -*-
# © 2015 Sergio Teruel <sergio.teruel@tecnativa.com>
# © 2015 Carlos Dauden <carlos.dauden@tecnativa.com>
# © 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Sale Service Project",
    'category': 'Sales',
    'version': '8.0.1.1.1',
    'depends': [
        'project_task_materials',
        'sale_service',
        'project_timesheet',
        'hr_timesheet_invoice'
    ],
    'demo': [
        'data/sale_service_project_demo.xml',
    ],
    'data': [
        'views/sale_service_view.xml',
        'views/sale_service_project_view.xml',
        'views/sale_view.xml',
        'views/account_invoice_view.xml',
        'views/project_view.xml',
        'views/report_saleorder.xml',
        'views/report_invoice.xml',
        'wizard/product_price_service_view.xml',
        'security/ir.model.access.csv',
    ],
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.tecnativa.com',
    'license': 'AGPL-3',
    'installable': True,
    'images': [],
}
