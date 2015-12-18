# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': "Sale Service Project",
    'category': 'Sales',
    'version': '8.0.1.0.0',
    'depends': [
        'project_task_materials',
        'sale_service',
        'project_timesheet',
        'hr_timesheet_invoice'],
    'demo': [
        'data/sale_service_project_demo.xml',
    ],
    'data': [
        'views/sale_service_view.xml',
        'views/sale_service_project_view.xml',
        'views/sale_view.xml',
        'views/project_view.xml',
        'wizard/product_price_service_view.xml',
    ],
    'author': 'Antiun Ingeniería S.L., '
              'Incaser Informatica S.L., '
              'Odoo Community Association (OCA)',
    'website': 'http://www.antiun.com',
    'license': 'AGPL-3',
    'installable': True,
}
