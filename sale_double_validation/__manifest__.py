# -*- coding: utf-8 -*-
# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{'name': 'Double validation for Sales',
 'summary': "",
 'version': '10.0.1.0.0',
 'author': 'Camptocamp SA, Odoo Community Association (OCA)',
 'maintainer': 'Camptocamp ',
 'license': 'AGPL-3',
 'category': 'sale',
 'depends': [
     'sale',
     'sales_team',
 ],
 'website': 'https://github.com/OCA/sale-workflow',
 'data': ['views/res_config.xml',
          'views/sale.xml'],
 'test': [],
 'installable': True,
 'auto_install': False,
 }
