# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': "Sale Service Fleet",
    'category': 'Sales',
    'version': '8.0.1.0.0',
    'depends': [
        'sale_service_project',
        'fleet',
        'account_analytic_analysis',
    ],
    'data': [
        'views/sale_view.xml',
        'views/project_view.xml',
        'views/analytic_view.xml',
        'views/account_analytic_analysis_view.xml',
        'views/report_saleorder.xml',
        'views/report_invoice.xml',
        'report/project_report_view.xml',
    ],
    'author': 'Incaser Informatica S.L., '
              'Antiun Ingeniería S.L., '
              'Odoo Community Association (OCA)',
    'website': 'http://www.incaser.es',
    'license': 'AGPL-3',
    'installable': True,
    'autoinstall': True,
}
